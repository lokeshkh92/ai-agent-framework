from typing import Any, Dict


class ScriptRunnerService:
    def run_script(self, script: str, inputs: Dict[str, Any]) -> Any:
        """
        Placeholder only. Replace with a sandboxed subprocess / isolated runner in production.
        """
        local_vars = {
            "inputs": inputs,
            "result": None,
        }
        exec(script, {"__builtins__": {}}, local_vars)
        return local_vars.get("result")
