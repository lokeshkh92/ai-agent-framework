from typing import Any, Dict, List
import trino
from trino.auth import BasicAuthentication


TRINO_CONNECTION_TYPE = "trino"
SUPPORTED_AUTHS = {"basic": BasicAuthentication}
KEYS_TO_REMOVE = ["connection_ref", "connection_type"]

class TrinoService:
    def __init__(self, connection_repository):
        self.connection_repository = connection_repository

    def execute_query(self, connection_ref: str, query: str) -> List[Dict[str, Any]]:
        conn_cfg = self.connection_repository.get_connection(connection_ref)
        if conn_cfg["connection_type"] != TRINO_CONNECTION_TYPE:
            raise RuntimeError(f"Connection '{connection_ref}' is not a trino connection")
        connection_config = {k: v for k, v in conn_cfg.items() if k not in KEYS_TO_REMOVE}
        auth_config = connection_config["auth"]
        if auth_config["type"] not in SUPPORTED_AUTHS:
            raise RuntimeError(f"Invalid trino auth type: {auth_config['type']}")
        connection_auth = SUPPORTED_AUTHS[auth_config["type"]](**auth_config["params"])
        connection_params = connection_config["config"]
        with trino.dbapi.connect(auth=connection_auth, **connection_params) as trino_connection:
            cursor = trino_connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        return rows
