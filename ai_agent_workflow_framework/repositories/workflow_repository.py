from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras

from workflow.models import WorkflowDefinition, WorkflowTrigger, WorkflowNode, WorkflowEdge
from utils.serialization import dumps_json


class WorkflowRepository:
    def __init__(self, dsn: str, table_name: str = "workflow_definitions"):
        self.dsn = dsn
        self.table_name = table_name

    def _get_connection(self):
        return psycopg2.connect(self.dsn)

    def save_workflow(self, workflow: WorkflowDefinition, created_by: Optional[str] = None) -> None:
        definition_json = self._workflow_to_definition_json(workflow)
        query = f"""
            INSERT INTO {self.table_name} (
                workflow_id, name, version, status, definition_json, created_by, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (workflow_id) DO UPDATE
            SET name = EXCLUDED.name,
                version = EXCLUDED.version,
                status = EXCLUDED.status,
                definition_json = EXCLUDED.definition_json,
                created_by = COALESCE(EXCLUDED.created_by, {self.table_name}.created_by),
                updated_at = CURRENT_TIMESTAMP
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    workflow.workflow_id,
                    workflow.name,
                    workflow.version,
                    workflow.status,
                    dumps_json(definition_json),
                    created_by,
                ))
            conn.commit()

    def get_published_workflow(self, workflow_id: str) -> WorkflowDefinition:
        query = f"""
            SELECT definition_json
            FROM {self.table_name}
            WHERE workflow_id = %s AND status = 'PUBLISHED'
            ORDER BY updated_at DESC
            LIMIT 1
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (workflow_id,))
                row = cur.fetchone()
                if not row:
                    raise KeyError(f"Published workflow '{workflow_id}' not found")
                return self._definition_json_to_workflow(dict(row)["definition_json"])

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition:
        query = f"""
            SELECT definition_json
            FROM {self.table_name}
            WHERE workflow_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (workflow_id,))
                row = cur.fetchone()
                if not row:
                    raise KeyError(f"Workflow '{workflow_id}' not found")
                return self._definition_json_to_workflow(dict(row)["definition_json"])

    def list_workflows(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = f"""
            SELECT workflow_id, name, version, status, created_by, created_at, updated_at
            FROM {self.table_name}
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND status = %s"
            params.append(status)
        query += " ORDER BY updated_at DESC"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                return [dict(r) for r in cur.fetchall()]

    def publish_workflow(self, workflow_id: str) -> None:
        query = f"""
            UPDATE {self.table_name}
            SET status = 'PUBLISHED',
                last_published_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE workflow_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (workflow_id,))
            conn.commit()

    def archive_workflow(self, workflow_id: str) -> None:
        query = f"""
            UPDATE {self.table_name}
            SET status = 'ARCHIVED', updated_at = CURRENT_TIMESTAMP
            WHERE workflow_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (workflow_id,))
            conn.commit()

    def _workflow_to_definition_json(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "version": workflow.version,
            "status": workflow.status,
            "trigger": {"type": workflow.trigger.type, "config": workflow.trigger.config},
            "nodes": [{"id": n.id, "type": n.type, "label": n.label, "config": n.config} for n in workflow.nodes],
            "edges": [{"source": e.source, "target": e.target} for e in workflow.edges],
            "metadata": workflow.metadata,
        }

    def _definition_json_to_workflow(self, definition_json: Dict[str, Any]) -> WorkflowDefinition:
        return WorkflowDefinition(
            workflow_id=definition_json["workflow_id"],
            name=definition_json["name"],
            version=definition_json["version"],
            status=definition_json["status"],
            trigger=WorkflowTrigger(type=definition_json["trigger"]["type"], config=definition_json["trigger"].get("config", {})),
            nodes=[WorkflowNode(id=n["id"], type=n["type"], label=n["label"], config=n.get("config", {})) for n in definition_json.get("nodes", [])],
            edges=[WorkflowEdge(source=e["source"], target=e["target"]) for e in definition_json.get("edges", [])],
            metadata=definition_json.get("metadata", {}),
        )
