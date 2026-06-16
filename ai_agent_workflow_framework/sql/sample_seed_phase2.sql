INSERT INTO connection_registry (connection_ref, connection_type, config_json, created_by, is_active)
VALUES (
    'postgres_monitoring',
    'postgres',
    '{"dbname": "monitoring", "user": "monitor_user", "password": "monitor_password", "host": "127.0.0.1", "port": 5432}',
    'system',
    TRUE
)
ON CONFLICT (connection_ref) DO NOTHING;
