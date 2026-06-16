from typing import Any, Dict

from nodes.base_node import BaseNode


class HDFSListNode(BaseNode):
    node_type = "hdfs_list"

    def __init__(self, hdfs_service, template_resolver):
        self.hdfs_service = hdfs_service
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "path" not in config:
            raise ValueError("hdfs_list requires 'path'")

    def execute(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)

        result = self.hdfs_service.list_files(
            hdfs_path=resolved_config["path"]
        )

        return {
            "status": "SUCCESS",
            "output": result,
        }
