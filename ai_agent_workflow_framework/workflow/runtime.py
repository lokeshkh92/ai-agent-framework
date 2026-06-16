import uuid
from typing import Dict, Any, List, Optional, Tuple

from workflow.context import WorkflowExecutionContext
from core.exceptions import WorkflowExecutionError


class WorkflowRuntime:
    """
    Generic workflow runtime with support for:
      - normal node execution
      - apply_to_each loop propagation
      - workflow execution audit
      - node execution audit

    Loop behavior supported:
      1. ApplyToEachNode emits:
         {
           "status": "SUCCESS",
           "output": {
             "__apply_to_each__": True,
             "items": [...],
             "item_alias": "current_item",
             "index_alias": "current_index"
           }
         }

      2. The immediate succeeding node is executed once per item.

      3. Downstream nodes continue to execute per item if their upstream input
         contains "__loop_results__".

    Current limitation:
      - only one active loop source per node execution path
      - nested loops and multiple loop-source fan-in are not supported yet
    """

    def __init__(
        self,
        node_registry,
        workflow_repository,
        workflow_execution_repository,
        node_execution_repository,
        dag_engine,
    ):
        self.node_registry = node_registry
        self.workflow_repository = workflow_repository
        self.workflow_execution_repository = workflow_execution_repository
        self.node_execution_repository = node_execution_repository
        self.dag_engine = dag_engine

    def run_workflow(
        self,
        workflow_id: str,
        input_payload: Dict[str, Any],
        trigger_type: str = "manual",
        trigger_source: str = "api",
    ) -> Dict[str, Any]:
        workflow = self.workflow_repository.get_published_workflow(workflow_id)
        execution_id = str(uuid.uuid4())

        context = WorkflowExecutionContext(
            workflow_id=workflow.workflow_id,
            execution_id=execution_id,
            trigger_type=trigger_type,
            trigger_source=trigger_source,
            input_payload=input_payload,
        )

        self.workflow_execution_repository.create_started_execution(
            execution_id=execution_id,
            workflow_id=workflow.workflow_id,
            workflow_version=workflow.version,
            trigger_type=trigger_type,
            trigger_source=trigger_source,
            input_payload=input_payload,
        )

        try:
            order = self.dag_engine.build_execution_order(workflow)
            node_map = {node.id: node for node in workflow.nodes}
            incoming_map = self._build_incoming_map(workflow)

            for node_id in order:
                node_def = node_map[node_id]
                node_impl = self.node_registry.get(node_def.type)

                inputs = self._collect_inputs(
                    node_id=node_id,
                    incoming_map=incoming_map,
                    context=context,
                )

                self.node_execution_repository.create_started_node_execution(
                    execution_id=execution_id,
                    node_id=node_id,
                    node_type=node_def.type,
                    input_payload=inputs,
                )

                try:
                    result = self._execute_node_with_loop_support(
                        node_impl=node_impl,
                        node_def=node_def,
                        inputs=inputs,
                        context=context,
                    )

                    context.set_node_output(node_id, result)

                    if result.get("artifacts"):
                        for artifact in result["artifacts"]:
                            context.add_artifact(artifact)

                    self.node_execution_repository.mark_success(
                        execution_id=execution_id,
                        node_id=node_id,
                        output_payload=result,
                    )

                except Exception as node_exc:
                    context.add_error({
                        "node_id": node_id,
                        "error": str(node_exc),
                    })

                    self.node_execution_repository.mark_failed(
                        execution_id=execution_id,
                        node_id=node_id,
                        error_message=str(node_exc),
                    )

                    raise WorkflowExecutionError(
                        f"Node {node_id} failed: {node_exc}"
                    ) from node_exc

            final_output = {
                "workflow_id": workflow.workflow_id,
                "execution_id": execution_id,
                "node_outputs": context.node_outputs,
                "artifacts": context.artifacts,
                "errors": context.errors,
            }

            self.workflow_execution_repository.mark_success(
                execution_id=execution_id,
                output_payload=final_output,
            )

            return final_output

        except Exception as exc:
            self.workflow_execution_repository.mark_failed(
                execution_id=execution_id,
                error_message=str(exc),
                output_payload={
                    "node_outputs": context.node_outputs,
                    "errors": context.errors,
                },
            )
            raise

    def _execute_node_with_loop_support(
        self,
        node_impl,
        node_def,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext,
    ) -> Dict[str, Any]:
        """
        Executes a node either:
          - once (normal mode)
          - once per item (loop mode)

        Loop mode is triggered when an upstream node output contains either:
          1. "__apply_to_each__"  → emitted by ApplyToEachNode
          2. "__loop_results__"   → emitted by a downstream node already running inside loop
        """
        loop_source = self._detect_loop_source(inputs)

        if not loop_source:
            return node_impl.execute(
                inputs=inputs,
                config=node_def.config,
                context=self._build_template_context(context),
            )

        loop_type, upstream_node_id, loop_payload = loop_source

        if loop_type == "apply_to_each":
            return self._execute_from_apply_to_each_payload(
                node_impl=node_impl,
                node_def=node_def,
                inputs=inputs,
                context=context,
                loop_payload=loop_payload,
            )

        if loop_type == "loop_results":
            return self._execute_from_loop_results_payload(
                node_impl=node_impl,
                node_def=node_def,
                inputs=inputs,
                context=context,
                upstream_node_id=upstream_node_id,
                loop_payload=loop_payload,
            )

        raise WorkflowExecutionError(f"Unsupported loop source type: {loop_type}")

    def _execute_from_apply_to_each_payload(
        self,
        node_impl,
        node_def,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext,
        loop_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        items = loop_payload.get("items", [])
        keys = loop_payload.get("keys", [])
        item_alias = loop_payload.get("item_alias", "current_item")
        index_alias = loop_payload.get("index_alias", "current_index")
        key_alias = loop_payload.get("key_alias", "current_key")

        iteration_results = []
        aggregated_artifacts = []

        for idx, item in enumerate(items):
            current_key = keys[idx] if idx < len(keys) else None

            loop_context = {
                item_alias: item,
                index_alias: idx,
                key_alias: current_key,
                "total_items": len(items),
            }

            loop_inputs = {
                **inputs,
                "loop": loop_context,
            }

            per_item_result = node_impl.execute(
                inputs=loop_inputs,
                config=node_def.config,
                context=self._build_template_context(
                    context,
                    extra={"loop": loop_context},
                ),
            )

            iteration_results.append({
                "index": idx,
                "item": item,
                "key": current_key,
                "loop": loop_context,
                "node_result": per_item_result,
            })

            if per_item_result.get("artifacts"):
                aggregated_artifacts.extend(per_item_result["artifacts"])

        return {
            "status": "SUCCESS",
            "output": {
                "__loop_results__": iteration_results,
                "processed_count": len(iteration_results),
                "loop_origin": "apply_to_each",
                "item_alias": item_alias,
                "index_alias": index_alias,
                "key_alias": key_alias,
            },
            "artifacts": aggregated_artifacts,
        }

    def _execute_from_loop_results_payload(
        self,
        node_impl,
        node_def,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext,
        upstream_node_id: str,
        loop_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        loop_results = loop_payload.get("__loop_results__", [])

        iteration_results = []
        aggregated_artifacts = []

        for entry in loop_results:
            loop_context = entry.get("loop", {})
            upstream_per_item_result = entry.get("node_result")

            per_iteration_inputs = {
                **inputs,
                upstream_node_id: upstream_per_item_result,
                "loop": loop_context,
            }

            per_item_result = node_impl.execute(
                inputs=per_iteration_inputs,
                config=node_def.config,
                context=self._build_template_context(
                    context,
                    extra={"loop": loop_context},
                ),
            )

            iteration_results.append({
                "index": entry.get("index"),
                "item": entry.get("item"),
                "key": entry.get("key"),
                "loop": loop_context,
                "node_result": per_item_result,
            })

            if per_item_result.get("artifacts"):
                aggregated_artifacts.extend(per_item_result["artifacts"])

        return {
            "status": "SUCCESS",
            "output": {
                "__loop_results__": iteration_results,
                "processed_count": len(iteration_results),
                "loop_origin": "loop_results",
            },
            "artifacts": aggregated_artifacts,
        }

    def _detect_loop_source(
        self,
        inputs: Dict[str, Any],
    ) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        Returns one of:
          ("apply_to_each", upstream_node_id, loop_payload)
          ("loop_results", upstream_node_id, loop_payload)

        If multiple loop sources are found, raises an error.
        """
        detected = []

        for upstream_node_id, upstream_output in inputs.items():
            if not isinstance(upstream_output, dict):
                continue

            output = upstream_output.get("output", {})
            if not isinstance(output, dict):
                continue

            if output.get("__apply_to_each__") is True:
                detected.append(("apply_to_each", upstream_node_id, output))

            if "__loop_results__" in output:
                detected.append(("loop_results", upstream_node_id, output))

        if not detected:
            return None

        if len(detected) > 1:
            raise WorkflowExecutionError(
                "Multiple loop sources detected for the same node execution. "
                "Current runtime supports only one active loop source per path."
            )

        return detected[0]

    def _build_incoming_map(self, workflow) -> Dict[str, List[str]]:
        incoming = {node.id: [] for node in workflow.nodes}
        for edge in workflow.edges:
            incoming[edge.target].append(edge.source)
        return incoming

    def _collect_inputs(
        self,
        node_id: str,
        incoming_map: Dict[str, List[str]],
        context: WorkflowExecutionContext,
    ) -> Dict[str, Any]:
        upstream_nodes = incoming_map.get(node_id, [])

        if not upstream_nodes:
            return {
                "input_payload": context.input_payload,
            }

        inputs = {}
        for upstream_node_id in upstream_nodes:
            inputs[upstream_node_id] = context.get_node_output(upstream_node_id)

        return inputs

    def _build_template_context(
        self,
        context: WorkflowExecutionContext,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "input_payload": context.input_payload,
            "node_outputs": context.node_outputs,
            "variables": context.variables,
            "artifacts": context.artifacts,
            "errors": context.errors,
        }

        if extra:
            payload.update(extra)

        return payload
