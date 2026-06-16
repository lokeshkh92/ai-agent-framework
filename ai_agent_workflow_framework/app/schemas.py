from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class RunWorkflowRequest(BaseModel):
    input_payload: Dict[str, Any] = {}


class RunWorkflowResponse(BaseModel):
    workflow_id: str
    execution_id: str
    node_outputs: Dict[str, Any]
    artifacts: list
    errors: list


class WorkflowTriggerSchema(BaseModel):
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowNodeSchema(BaseModel):
    id: str
    type: str
    label: str
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEdgeSchema(BaseModel):
    source: str
    target: str


class WorkflowDefinitionCreateRequest(BaseModel):
    workflow_id: str
    name: str
    version: str = "1.0.0"
    status: str = "DRAFT"
    trigger: WorkflowTriggerSchema
    nodes: List[WorkflowNodeSchema]
    edges: List[WorkflowEdgeSchema]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[str] = None


class WorkflowDefinitionUpdateRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    trigger: Optional[WorkflowTriggerSchema] = None
    nodes: Optional[List[WorkflowNodeSchema]] = None
    edges: Optional[List[WorkflowEdgeSchema]] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_by: Optional[str] = None


class ValidateWorkflowResponse(BaseModel):
    valid: bool
    message: str

