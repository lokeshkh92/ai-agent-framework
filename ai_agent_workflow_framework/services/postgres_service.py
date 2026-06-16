import psycopg2
import psycopg2.extras
from typing import Any, Dict, List


POSTGRES_CONNECTION_TYPE = "postgres"


class PostgresService:
    def __init__(self, connection_repository):
        self.connection_repository = connection_repository

    def execute_query(self, connection_ref: str, query: str) -> List[Dict[str, Any]]:
        conn_cfg = self.connection_repository.get_connection(connection_ref)
        if conn_cfg["connection_type"] != POSTGRES_CONNECTION_TYPE:
            raise RuntimeError(f"Connection '{connection_ref}' is not a postgres connection")
        dsn = (
            f"dbname={conn_cfg['dbname']} "
            f"user={conn_cfg['user']} "
            f"password={conn_cfg['password']} "
            f"host={conn_cfg['host']} "
            f"port={conn_cfg['port']}"
        )

        with psycopg2.connect(dsn) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
