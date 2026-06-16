from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class WorkflowTrigger:
    type: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowNode:
    id: str
    type: str
    label: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    source: str
    target: str


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    version: str
    status: str
    trigger: WorkflowTrigger
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)
