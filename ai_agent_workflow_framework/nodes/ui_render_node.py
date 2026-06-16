from typing import Any, Dict

from nodes.base_node import BaseNode


class UIRenderNode(BaseNode):
    node_type = "ui_render"

    def __init__(self, template_resolver):
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "component" not in config:
            raise ValueError("ui_render requires 'component'")

    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)
        return {
            "status": "SUCCESS",
            "output": {
                "component": resolved_config["component"],
                "data": inputs,
            },
        }
