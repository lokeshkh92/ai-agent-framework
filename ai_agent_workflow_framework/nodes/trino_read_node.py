from typing import Any, Dict

from nodes.base_node import BaseNode


class TrinoReadNode(BaseNode):
    node_type = "trino_read"

    def __init__(self, trino_service, template_resolver):
        self.trino_service = trino_service
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "connection_ref" not in config:
            raise ValueError("trino_read requires 'connection_ref'")
        if "query" not in config:
            raise ValueError("trino_read requires 'query'")

    def execute(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)

        rows = self.trino_service.execute_query(
            connection_ref=resolved_config["connection_ref"],
            query=resolved_config["query"]
        )

        return {
            "status": "SUCCESS",
            "output": {
                "rows": rows,
                "row_count": len(rows),
            },
        }
