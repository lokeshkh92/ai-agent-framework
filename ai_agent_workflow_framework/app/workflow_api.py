from fastapi import APIRouter, HTTPException

from app.schemas import (
    WorkflowDefinitionCreateRequest,
    WorkflowDefinitionUpdateRequest,
    ValidateWorkflowResponse,
    RunWorkflowRequest,
)


def build_workflow_router(workflow_service, workflow_runtime, workflow_execution_repository, node_execution_repository):
    router = APIRouter()

    @router.get("/workflows")
    def list_workflows(status: str | None = None):
        return workflow_service.list_workflows(status=status)

    @router.post("/workflows")
    def create_workflow(request: WorkflowDefinitionCreateRequest):
        try:
            wf = workflow_service.create_workflow(request.model_dump())
            return {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "version": wf.version,
                "status": wf.status,
                "message": "Workflow created successfully",
            }
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/workflows/{workflow_id}")
    def get_workflow(workflow_id: str):
        try:
            wf = workflow_service.get_workflow(workflow_id)
            return {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "version": wf.version,
                "status": wf.status,
                "trigger": {"type": wf.trigger.type, "config": wf.trigger.config},
                "nodes": [
                    {"id": n.id, "type": n.type, "label": n.label, "config": n.config}
                    for n in wf.nodes
                ],
                "edges": [
                    {"source": e.source, "target": e.target}
                    for e in wf.edges
                ],
                "metadata": wf.metadata,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.put("/workflows/{workflow_id}")
    def update_workflow(workflow_id: str, request: WorkflowDefinitionUpdateRequest):
        try:
            wf = workflow_service.update_workflow(workflow_id, request.model_dump(exclude_unset=True))
            return {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "version": wf.version,
                "status": wf.status,
                "message": "Workflow updated successfully",
            }
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/workflows/{workflow_id}/publish")
    def publish_workflow(workflow_id: str):
        try:
            workflow_service.publish_workflow(workflow_id)
            return {"workflow_id": workflow_id, "message": "Workflow published successfully"}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/workflows/{workflow_id}/archive")
    def archive_workflow(workflow_id: str):
        try:
            workflow_service.archive_workflow(workflow_id)
            return {"workflow_id": workflow_id, "message": "Workflow archived successfully"}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/workflows/{workflow_id}/validate", response_model=ValidateWorkflowResponse)
    def validate_workflow(workflow_id: str):
        try:
            workflow_service.validate_workflow(workflow_id)
            return ValidateWorkflowResponse(valid=True, message="Workflow validation successful")
        except Exception as exc:
            return ValidateWorkflowResponse(valid=False, message=str(exc))

    @router.post("/workflows/{workflow_id}/run")
    def run_workflow(workflow_id: str, request: RunWorkflowRequest):
        try:
            return workflow_runtime.run_workflow(
                workflow_id=workflow_id,
                input_payload=request.input_payload,
                trigger_type="api",
                trigger_source="api.run_workflow",
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/workflow-executions/{execution_id}")
    def get_workflow_execution(execution_id: str):
        try:
            return workflow_execution_repository.get_execution(execution_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/workflow-executions/{execution_id}/nodes")
    def get_node_executions(execution_id: str):
        return node_execution_repository.list_node_executions(execution_id)

    @router.get("/workflows/{workflow_id}/executions")
    def list_workflow_executions(workflow_id: str, limit: int = 50):
        return workflow_execution_repository.list_executions_by_workflow(workflow_id, limit=limit)

    return router
