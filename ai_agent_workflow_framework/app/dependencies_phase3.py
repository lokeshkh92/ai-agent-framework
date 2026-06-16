import os

from registry.node_registry import NodeRegistry
from registry.node_specs import NODE_SPECS
from workflow.dag_engine import DAGEngine
from workflow.validator import WorkflowValidator
from workflow.runtime import WorkflowRuntime

from nodes.postgres_read_node import PostgresReadNode
from nodes.python_script_node import PythonScriptNode
from nodes.llm_infer_node import LLMInferNode
from nodes.send_email_node import SendEmailNode
from nodes.ui_render_node import UIRenderNode

from services.postgres_service import PostgresService
from services.ollama_service import OllamaService
from services.email_service import EmailService
from services.script_runner_service import ScriptRunnerService
from services.workflow_service import WorkflowService

from repositories.workflow_repository import WorkflowRepository
from repositories.workflow_execution_repository import WorkflowExecutionRepository
from repositories.node_execution_repository import NodeExecutionRepository
from repositories.connection_repository import ConnectionRepository

from utils.templating import SimpleTemplateResolver


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
    return f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"


def build_phase3_components():
    postgres_dsn = _build_postgres_dsn()

    connection_repository = ConnectionRepository(dsn=postgres_dsn)
    workflow_repository = WorkflowRepository(dsn=postgres_dsn)
    workflow_execution_repository = WorkflowExecutionRepository(dsn=postgres_dsn)
    node_execution_repository = NodeExecutionRepository(dsn=postgres_dsn)

    template_resolver = SimpleTemplateResolver()
    postgres_service = PostgresService(connection_repository=connection_repository)
    llm_service = OllamaService(llm_client=DummyLLMClient())
    email_service = EmailService(smtp_client=DummySMTPClient())
    script_runner_service = ScriptRunnerService()

    node_registry = NodeRegistry()
    node_registry.register("postgres_read", PostgresReadNode(postgres_service, template_resolver))
    node_registry.register("python_script", PythonScriptNode(script_runner_service, template_resolver))
    node_registry.register("llm_infer", LLMInferNode(llm_service, template_resolver))
    node_registry.register("send_email", SendEmailNode(email_service, template_resolver))
    node_registry.register("ui_render", UIRenderNode(template_resolver))

    workflow_validator = WorkflowValidator(node_registry)
    dag_engine = DAGEngine()

    workflow_runtime = WorkflowRuntime(
        node_registry=node_registry,
        workflow_repository=workflow_repository,
        workflow_execution_repository=workflow_execution_repository,
        node_execution_repository=node_execution_repository,
        dag_engine=dag_engine,
    )

    workflow_service = WorkflowService(
        workflow_repository=workflow_repository,
        workflow_validator=workflow_validator,
    )

    node_catalog_service = NodeCatalogService()

    return {
        "workflow_runtime": workflow_runtime,
        "workflow_service": workflow_service,
        "workflow_execution_repository": workflow_execution_repository,
        "node_execution_repository": node_execution_repository,
        "node_catalog_service": node_catalog_service,
    }
