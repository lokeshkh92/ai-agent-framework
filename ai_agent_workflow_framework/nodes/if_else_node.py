from typing import Any, Dict

from nodes.base_node import BaseNode
from utils.safe_condition_evaluator import SafeConditionEvaluator


class IfElseNode(BaseNode):
    node_type = "if_else"

    def __init__(self, template_resolver, evaluator: SafeConditionEvaluator | None = None):
        self.template_resolver = template_resolver
        self.evaluator = evaluator or SafeConditionEvaluator()

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "condition" not in config:
            raise ValueError("if_else requires 'condition'")

        condition = config["condition"]
        if not isinstance(condition, dict):
            raise ValueError("if_else 'condition' must be a dict")

        operator = condition.get("operator")
        if not operator:
            raise ValueError("if_else condition requires 'operator'")

    def execute(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)
        condition = resolved_config["condition"]

        condition_result = self.evaluator.evaluate(condition)

        true_next = resolved_config.get("true_next")
        false_next = resolved_config.get("false_next")

        return {
            "status": "SUCCESS",
            "output": {
                "condition_result": condition_result,
                "selected_branch": "true" if condition_result else "false",
                "next_node_hint": true_next if condition_result else false_next,
            },
        }
