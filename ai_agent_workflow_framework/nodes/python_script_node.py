from typing import Any, Dict

from nodes.base_node import BaseNode


class PythonScriptNode(BaseNode):
    node_type = "python_script"

    def __init__(self, script_runner_service, template_resolver):
        self.script_runner_service = script_runner_service
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "script" not in config:
            raise ValueError("python_script requires 'script'")

    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)
        result = self.script_runner_service.run_script(script=resolved_config["script"], inputs=inputs)
        return {
            "status": "SUCCESS",
            "output": {
                "result": result,
            },
        }
