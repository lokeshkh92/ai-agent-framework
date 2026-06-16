from typing import Any, Dict
import json

from nodes.base_node import BaseNode


class LLMInferNode(BaseNode):
    node_type = "llm_infer"

    def __init__(self, llm_service, template_resolver):
        self.llm_service = llm_service
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "prompt_template" not in config:
            raise ValueError("llm_infer requires 'prompt_template'")

    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)

        prompt_template = resolved_config["prompt_template"]
        input_json = json.dumps(inputs, default=str)
        prompt = prompt_template.replace("{{input_json}}", input_json)

        output_mode = resolved_config.get("output_mode", "text")

        if output_mode == "json":
            result = self.llm_service.generate_json(prompt=prompt, model=resolved_config.get("model"))
        else:
            result = self.llm_service.generate(prompt=prompt, model=resolved_config.get("model"))

        return {
            "status": "SUCCESS",
            "output": {
                "result": result,
            },
        }
