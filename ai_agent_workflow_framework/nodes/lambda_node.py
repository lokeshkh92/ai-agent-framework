from typing import Any, Dict

from nodes.base_node import BaseNode
from registry.node_registry import NodeRegistry
from utils.safe_condition_evaluator import SafeConditionEvaluator


class LambdaNode(BaseNode):
    node_type = "lambda"

    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry
        print(id(self.node_registry))

    def validate_config(self, config: Dict[str, Any]) -> None:
        pass

    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:

        return {"status": "", "output": {}}
