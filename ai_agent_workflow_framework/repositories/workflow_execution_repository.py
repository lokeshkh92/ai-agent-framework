from datetime import datetime, timezone
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extras

from utils.serialization import dumps_json


class WorkflowExecutionRepository:
    def __init__(self, dsn: str, table_name: str = "workflow_executions"):
        self.dsn = dsn
        self.table_name = table_name

    def _get_connection(self):
        return psycopg2.connect(self.dsn)

    def create_started_execution(self, execution_id: str, workflow_id: str, workflow_version: str, trigger_type: str, trigger_source: str, input_payload: Dict[str, Any]) -> None:
        query = f"""
            INSERT INTO {self.table_name} (
                execution_id, workflow_id, workflow_version, status,
                trigger_type, trigger_source, input_payload, started_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    execution_id, workflow_id, workflow_version, "STARTED",
                    trigger_type, trigger_source, dumps_json(input_payload),
                ))
            conn.commit()

    def mark_success(self, execution_id: str, output_payload: Dict[str, Any]) -> None:
        started_at = self._get_started_at(execution_id)
        completed_at = datetime.now(timezone.utc)
        duration_ms = self._compute_duration_ms(started_at, completed_at)
        query = f"""
            UPDATE {self.table_name}
            SET status = 'SUCCESS', output_payload = %s::jsonb, completed_at = %s, duration_ms = %s
            WHERE execution_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (dumps_json(output_payload), completed_at, duration_ms, execution_id))
            conn.commit()

    def mark_failed(self, execution_id: str, error_message: str, output_payload: Optional[Dict[str, Any]] = None) -> None:
        started_at = self._get_started_at(execution_id)
        completed_at = datetime.now(timezone.utc)
        duration_ms = self._compute_duration_ms(started_at, completed_at)
        query = f"""
            UPDATE {self.table_name}
            SET status = 'FAILED', error_message = %s, output_payload = %s::jsonb, completed_at = %s, duration_ms = %s
            WHERE execution_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (error_message, dumps_json(output_payload or {}), completed_at, duration_ms, execution_id))
            conn.commit()

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        query = f"SELECT * FROM {self.table_name} WHERE execution_id = %s"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (execution_id,))
                row = cur.fetchone()
                if not row:
                    raise KeyError(f"Workflow execution '{execution_id}' not found")
                return dict(row)

    def list_executions_by_workflow(self, workflow_id: str, limit: int = 50):
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE workflow_id = %s
            ORDER BY started_at DESC
            LIMIT %s
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (workflow_id, limit))
                return [dict(row) for row in cur.fetchall()]

    def _get_started_at(self, execution_id: str):
        query = f"SELECT started_at FROM {self.table_name} WHERE execution_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (execution_id,))
                row = cur.fetchone()
                return row[0] if row else None

    def _compute_duration_ms(self, started_at, completed_at):
        if not started_at:
            return None
        return int((completed_at - started_at).total_seconds() * 1000)
