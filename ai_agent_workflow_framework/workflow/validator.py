from registry.node_registry import NodeRegistry
from workflow.models import WorkflowDefinition
from core.exceptions import WorkflowValidationError


class WorkflowValidator:
    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry

    def validate(self, workflow: WorkflowDefinition) -> None:
        node_ids = set()

        for node in workflow.nodes:
            if node.id in node_ids:
                raise WorkflowValidationError(f"Duplicate node id: {node.id}")
            node_ids.add(node.id)

            node_impl = self.node_registry.get(node.type)
            node_impl.validate_config(node.config)

        for edge in workflow.edges:
            if edge.source not in node_ids:
                raise WorkflowValidationError(f"Invalid edge source: {edge.source}")
            if edge.target not in node_ids:
                raise WorkflowValidationError(f"Invalid edge target: {edge.target}")

        self._validate_acyclic(workflow)

    def _validate_acyclic(self, workflow: WorkflowDefinition) -> None:
        graph = {node.id: [] for node in workflow.nodes}
        for edge in workflow.edges:
            graph[edge.source].append(edge.target)

        visited = set()
        stack = set()

        def dfs(node_id: str):
            if node_id in stack:
                raise WorkflowValidationError("Workflow graph contains a cycle")
            if node_id in visited:
                return

            stack.add(node_id)
            for nxt in graph[node_id]:
                dfs(nxt)
            stack.remove(node_id)
            visited.add(node_id)

        for node in workflow.nodes:
            dfs(node.id)
