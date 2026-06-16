from typing import Any, Dict, Optional
import ollama
import json


class OllamaService:
    def __init__(self, ollama_host):
        self.llm_client = ollama.Client(host=ollama_host)

    def generate(self, prompt: str, model: Optional[str] = None,
                 client_params: Dict[str, Any] = None, model_options: Dict[str, Any] = None) -> str:
        response = self.llm_client.generate(model=model, prompt=prompt,
                                            options=model_options, **client_params)
        return response.response

    def generate_json(self, prompt: str, model: Optional[str] = None,
                      client_params: Dict[str, Any] = None, model_options: Dict[str, Any] = None) -> Dict[str, Any]:
        response = self.llm_client.generate(model=model, prompt=prompt,
                                            options=model_options, **client_params)
        try:
            parsed_json = json.loads(response.response)
        except Exception:
            parsed_json = {"json_parse_status": "FAILED",
                           "raw_response": response.response}
        return parsed_json
