from datetime import datetime, timezone
from typing import Any, Dict

import psycopg2
import psycopg2.extras

from utils.serialization import dumps_json


class NodeExecutionRepository:
    def __init__(self, dsn: str, table_name: str = "node_executions"):
        self.dsn = dsn
        self.table_name = table_name

    def _get_connection(self):
        return psycopg2.connect(self.dsn)

    def create_started_node_execution(self, execution_id: str, node_id: str, node_type: str, input_payload: Dict[str, Any]) -> None:
        query = f"""
            INSERT INTO {self.table_name} (execution_id, node_id, node_type, status, input_payload, started_at)
            VALUES (%s, %s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (execution_id, node_id, node_type, "STARTED", dumps_json(input_payload)))
            conn.commit()

    def mark_success(self, execution_id: str, node_id: str, output_payload: Dict[str, Any]) -> None:
        started_at = self._get_latest_started_at(execution_id, node_id)
        completed_at = datetime.now(timezone.utc)
        duration_ms = self._compute_duration_ms(started_at, completed_at)
        query = f"""
            UPDATE {self.table_name}
            SET status = 'SUCCESS', output_payload = %s::jsonb, completed_at = %s, duration_ms = %s
            WHERE node_execution_id = (
                SELECT node_execution_id FROM {self.table_name}
                WHERE execution_id = %s AND node_id = %s
                ORDER BY node_execution_id DESC LIMIT 1
            )
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (dumps_json(output_payload), completed_at, duration_ms, execution_id, node_id))
            conn.commit()

    def mark_failed(self, execution_id: str, node_id: str, error_message: str) -> None:
        started_at = self._get_latest_started_at(execution_id, node_id)
        completed_at = datetime.now(timezone.utc)
        duration_ms = self._compute_duration_ms(started_at, completed_at)
        query = f"""
            UPDATE {self.table_name}
            SET status = 'FAILED', error_message = %s, completed_at = %s, duration_ms = %s
            WHERE node_execution_id = (
                SELECT node_execution_id FROM {self.table_name}
                WHERE execution_id = %s AND node_id = %s
                ORDER BY node_execution_id DESC LIMIT 1
            )
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (error_message, completed_at, duration_ms, execution_id, node_id))
            conn.commit()

    def list_node_executions(self, execution_id: str):
        query = f"SELECT * FROM {self.table_name} WHERE execution_id = %s ORDER BY node_execution_id ASC"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (execution_id,))
                return [dict(row) for row in cur.fetchall()]

    def _get_latest_started_at(self, execution_id: str, node_id: str):
        query = f"SELECT started_at FROM {self.table_name} WHERE execution_id = %s AND node_id = %s ORDER BY node_execution_id DESC LIMIT 1"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (execution_id, node_id))
                row = cur.fetchone()
                return row[0] if row else None

    def _compute_duration_ms(self, started_at, completed_at):
        if not started_at:
            return None
        return int((completed_at - started_at).total_seconds() * 1000)
