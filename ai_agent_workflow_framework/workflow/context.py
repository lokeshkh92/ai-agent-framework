from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class WorkflowExecutionContext:
    workflow_id: str
    execution_id: str
    trigger_type: str
    trigger_source: str

    input_payload: Dict[str, Any] = field(default_factory=dict)
    node_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def set_node_output(self, node_id: str, output: Dict[str, Any]) -> None:
        self.node_outputs[node_id] = output

    def get_node_output(self, node_id: str) -> Dict[str, Any]:
        return self.node_outputs.get(node_id, {})

    def add_artifact(self, artifact: Dict[str, Any]) -> None:
        self.artifacts.append(artifact)

    def add_error(self, error: Dict[str, Any]) -> None:
        self.errors.append(error)
