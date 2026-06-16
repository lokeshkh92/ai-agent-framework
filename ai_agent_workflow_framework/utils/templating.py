from typing import Any, Dict


class SimpleTemplateResolver:
    def resolve(self, value: Any, runtime_context: Dict[str, Any]) -> Any:
        if isinstance(value, dict):
            return {k: self.resolve(v, runtime_context) for k, v in value.items()}
        if isinstance(value, list):
            return [self.resolve(v, runtime_context) for v in value]
        if not isinstance(value, str):
            return value

        stripped = value.strip()
        if stripped.startswith("{{") and stripped.endswith("}}"):
            expr = stripped[2:-2].strip()
            return self._resolve_path(expr, runtime_context)
        return value

    def _resolve_path(self, path: str, obj: Dict[str, Any]):
        current = obj
        for part in path.split("."):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
