import os

from registry.node_registry import NodeRegistry
from registry.node_specs import NODE_SPECS

from services.workflow_service import WorkflowService
from workflow.dag_engine import DAGEngine
from workflow.runtime import WorkflowRuntime
from workflow.validator import WorkflowValidator

from nodes.postgres_read_node import PostgresReadNode
from nodes.python_script_node import PythonScriptNode
from nodes.llm_infer_node import LLMInferNode
from nodes.send_email_node import SendEmailNode
from nodes.ui_render_node import UIRenderNode
from nodes.trino_read_node import TrinoReadNode
from nodes.if_else_node import IfElseNode
from nodes.csv_writer_node import CSVWriterNode
from nodes.hdfs_list_node import HDFSListNode
from nodes.apply_to_each_node import ApplyToEachNode

from services.postgres_service import PostgresService
from services.ollama_service import OllamaService
from services.email_service import EmailService
from services.script_runner_service import ScriptRunnerService
from services.hdfs_service import HDFSService
from services.trino_service import TrinoService
from services.file_service import FileService

from repositories.workflow_repository import WorkflowRepository
from repositories.workflow_execution_repository import WorkflowExecutionRepository
from repositories.node_execution_repository import NodeExecutionRepository
from repositories.connection_repository import ConnectionRepository

from utils.templating import SimpleTemplateResolver
from utils.safe_condition_evaluator import SafeConditionEvaluator


class DummySMTPClient:
    def send_email(self, recipients, subject, body, attachments=None):
        return True


class DummyLLMClient:
    def generate(self, prompt):
        return f"LLM output for prompt: {prompt[:100]}"

    def generate_json(self, prompt):
        return {"summary": f"Structured output for prompt: {prompt[:100]}"}


class NodeCatalogService:
    def list_nodes(self):
        return NODE_SPECS


def _build_postgres_dsn() -> str:
    db_name = os.getenv("POSTGRES_DB", "monitoring")
    db_user = os.getenv("POSTGRES_USER", "monitor_user")
    db_password = os.getenv("POSTGRES_PASSWORD", "monitor_password")
    db_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    return (
        f"dbname={db_name} "
        f"user={db_user} "
        f"password={db_password} "
        f"host={db_host} "
        f"port={db_port}"
    )


def get_workflow_runtime():
    postgres_dsn = _build_postgres_dsn()

    connection_repository = ConnectionRepository(dsn=postgres_dsn)
    template_resolver = SimpleTemplateResolver()

    ollama_host = os.getenv("OLLAMA_HOST", None)
    if not ollama_host:
        raise RuntimeError("'OLLAMA_HOST' is not set")
    output_base_dir = os.getenv("OUTPUT_BASE_DIRECTORY", "/opt/sasdisk02/output")

    postgres_service = PostgresService(connection_repository=connection_repository)
    llm_service = OllamaService(ollama_host=ollama_host)
    email_service = EmailService(connection_repository=connection_repository)
    script_runner_service = ScriptRunnerService()
    trino_service = TrinoService(connection_repository=connection_repository)
    hdfs_service = HDFSService()
    file_service = FileService(base_dir=output_base_dir)

    registry = NodeRegistry()
    print(id(registry))
    registry.register("postgres_read", PostgresReadNode(postgres_service, template_resolver))
    registry.register("python_script", PythonScriptNode(script_runner_service, template_resolver))
    registry.register("llm_infer", LLMInferNode(llm_service, template_resolver))
    registry.register("send_email", SendEmailNode(email_service, template_resolver))
    registry.register("ui_render", UIRenderNode(template_resolver))

    registry.register("trino_read", TrinoReadNode(trino_service, template_resolver))
    # registry.register("if_else", IfElseNode(template_resolver, safe_condition_evaluator))
    registry.register("if_else", IfElseNode(template_resolver, SafeConditionEvaluator()))
    registry.register("csv_writer", CSVWriterNode(file_service, template_resolver))
    registry.register("hdfs_list", HDFSListNode(hdfs_service, template_resolver))
    registry.register("apply_to_each", ApplyToEachNode(template_resolver))

    workflow_repository = WorkflowRepository(dsn=postgres_dsn)
    workflow_execution_repository = WorkflowExecutionRepository(dsn=postgres_dsn)
    node_execution_repository = NodeExecutionRepository(dsn=postgres_dsn)
    dag_engine = DAGEngine()

    workflow_validator = WorkflowValidator(registry)

    workflow_runtime = WorkflowRuntime(
        node_registry=registry,
        workflow_repository=workflow_repository,
        workflow_execution_repository=workflow_execution_repository,
        node_execution_repository=node_execution_repository,
        dag_engine=dag_engine,
    )
    workflow_service = WorkflowService(
        workflow_repository=workflow_repository,
        workflow_validator=workflow_validator,
    )
    node_catalog_service = get_node_catalog_service()
    return {
        "workflow_runtime": workflow_runtime,
        "workflow_service": workflow_service,
        "workflow_execution_repository": workflow_execution_repository,
        "node_execution_repository": node_execution_repository,
        "node_catalog_service": node_catalog_service,
    }


def get_node_catalog_service():
    return NodeCatalogService()
