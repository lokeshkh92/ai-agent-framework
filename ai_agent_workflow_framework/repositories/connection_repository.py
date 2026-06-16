import psycopg2
import psycopg2.extras

from utils.serialization import dumps_json


class ConnectionRepository:
    def __init__(self, dsn: str, table_name: str = "connection_registry"):
        self.dsn = dsn
        self.table_name = table_name

    def _get_connection(self):
        return psycopg2.connect(self.dsn)

    def get_connection(self, connection_ref: str):
        query = f"""
            SELECT connection_ref, connection_type, config_json
            FROM {self.table_name}
            WHERE connection_ref = %s AND is_active = TRUE
            LIMIT 1
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (connection_ref,))
                row = cur.fetchone()
                if not row:
                    raise KeyError(f"Connection ref '{connection_ref}' not found")
                data = dict(row)
                return {
                    "connection_ref": data["connection_ref"],
                    "connection_type": data["connection_type"],
                    **(data.get("config_json") or {}),
                }

    def save_connection(self, connection_ref: str, connection_type: str, config_json: dict, created_by: str | None = None, is_active: bool = True) -> None:
        query = f"""
            INSERT INTO {self.table_name} (
                connection_ref, connection_type, config_json, created_by, is_active, created_at, updated_at
            )
            VALUES (%s, %s, %s::jsonb, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (connection_ref) DO UPDATE
            SET connection_type = EXCLUDED.connection_type,
                config_json = EXCLUDED.config_json,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (connection_ref, connection_type, dumps_json(config_json), created_by, is_active))
            conn.commit()
