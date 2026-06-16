"""
Example dependency wiring for the additional nodes.
Merge this logic into your real dependencies module.
"""

from registry.node_registry import NodeRegistry
from utils.templating import SimpleTemplateResolver
from utils.safe_condition_evaluator import SafeConditionEvaluator

from nodes.trino_read_node import TrinoReadNode
from nodes.if_else_node import IfElseNode
from nodes.csv_writer_node import CSVWriterNode
from nodes.hdfs_list_node import HDFSListNode

from services.trino_service import TrinoService
from services.hdfs_service import HDFSService
from services.file_service import FileService


def register_additional_nodes(node_registry: NodeRegistry, trino_client, output_base_dir: str = "/opt/ai-framework/output"):
    template_resolver = SimpleTemplateResolver()
    safe_condition_evaluator = SafeConditionEvaluator()

    trino_service = TrinoService(trino_client=trino_client)
    hdfs_service = HDFSService()
    file_service = FileService(base_dir=output_base_dir)

    node_registry.register("trino_read", TrinoReadNode(trino_service, template_resolver))
    node_registry.register("if_else", IfElseNode(template_resolver, safe_condition_evaluator))
    node_registry.register("csv_writer", CSVWriterNode(file_service, template_resolver))
    node_registry.register("hdfs_list", HDFSListNode(hdfs_service, template_resolver))
