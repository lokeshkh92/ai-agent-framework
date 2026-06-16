from fastapi import FastAPI
from app.dependencies import get_workflow_runtime, get_node_catalog_service
import uvicorn
from app.workflow_api import build_workflow_router


app = FastAPI(title="Workflow-Based AI Framework")

runtime = get_workflow_runtime()
node_catalog_service = get_node_catalog_service()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/node-catalog")
def node_catalog():
    return node_catalog_service.list_nodes()

app.include_router(
    build_workflow_router(
        workflow_service=runtime["workflow_service"],
        workflow_runtime=runtime["workflow_runtime"],
        workflow_execution_repository=runtime["workflow_execution_repository"],
        node_execution_repository=runtime["node_execution_repository"],
    )
)


@app.get("/node-catalog")
def node_catalog():
    return runtime["node_catalog_service"].list_nodes()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # app.run(debug=True, port=6000, host="0.0.0.0")
