from typing import Any, Dict

from workflow.models import WorkflowDefinition, WorkflowTrigger, WorkflowNode, WorkflowEdge


class WorkflowService:
    def __init__(self, workflow_repository, workflow_validator):
        self.workflow_repository = workflow_repository
        self.workflow_validator = workflow_validator

    def create_workflow(self, payload: Dict[str, Any]) -> WorkflowDefinition:
        workflow = self._payload_to_workflow(payload)
        self.workflow_validator.validate(workflow)
        self.workflow_repository.save_workflow(workflow, created_by=payload.get("created_by"))
        return workflow

    def update_workflow(self, workflow_id: str, patch: Dict[str, Any]) -> WorkflowDefinition:
        existing = self.workflow_repository.get_workflow(workflow_id)
        merged = {
            "workflow_id": existing.workflow_id,
            "name": patch.get("name", existing.name),
            "version": patch.get("version", existing.version),
            "status": patch.get("status", existing.status),
            "trigger": patch.get("trigger", {"type": existing.trigger.type, "config": existing.trigger.config}),
            "nodes": patch.get("nodes", [
                {"id": n.id, "type": n.type, "label": n.label, "config": n.config} for n in existing.nodes
            ]),
            "edges": patch.get("edges", [
                {"source": e.source, "target": e.target} for e in existing.edges
            ]),
            "metadata": patch.get("metadata", existing.metadata),
        }
        workflow = self._payload_to_workflow(merged)
        self.workflow_validator.validate(workflow)
        self.workflow_repository.save_workflow(workflow, created_by=patch.get("updated_by"))
        return workflow

    def validate_workflow(self, workflow_id: str) -> None:
        workflow = self.workflow_repository.get_workflow(workflow_id)
        self.workflow_validator.validate(workflow)

    def publish_workflow(self, workflow_id: str) -> None:
        workflow = self.workflow_repository.get_workflow(workflow_id)
        self.workflow_validator.validate(workflow)
        self.workflow_repository.publish_workflow(workflow_id)

    def archive_workflow(self, workflow_id: str) -> None:
        self.workflow_repository.archive_workflow(workflow_id)

    def list_workflows(self, status=None):
        return self.workflow_repository.list_workflows(status=status)

    def get_workflow(self, workflow_id: str):
        return self.workflow_repository.get_workflow(workflow_id)

    def _payload_to_workflow(self, payload: Dict[str, Any]) -> WorkflowDefinition:
        return WorkflowDefinition(
            workflow_id=payload["workflow_id"],
            name=payload["name"],
            version=payload["version"],
            status=payload["status"],
            trigger=WorkflowTrigger(
                type=payload["trigger"]["type"],
                config=payload["trigger"].get("config", {}),
            ),
            nodes=[
                WorkflowNode(
                    id=node["id"],
                    type=node["type"],
                    label=node["label"],
                    config=node.get("config", {}),
                ) for node in payload.get("nodes", [])
            ],
            edges=[
                WorkflowEdge(source=edge["source"], target=edge["target"]) for edge in payload.get("edges", [])
            ],
            metadata=payload.get("metadata", {}),
        )
