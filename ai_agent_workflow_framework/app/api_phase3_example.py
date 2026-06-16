from fastapi import FastAPI
from app.dependencies_phase3 import build_phase3_components
from app.workflow_api import build_workflow_router

components = build_phase3_components()

app = FastAPI(title="Workflow-Based AI Framework - Phase 3")
app.include_router(
    build_workflow_router(
        workflow_service=components["workflow_service"],
        workflow_runtime=components["workflow_runtime"],
        workflow_execution_repository=components["workflow_execution_repository"],
        node_execution_repository=components["node_execution_repository"],
    )
)


@app.get("/node-catalog")
def node_catalog():
    return components["node_catalog_service"].list_nodes()


@app.get("/health")
def health():
    return {"status": "ok"}
