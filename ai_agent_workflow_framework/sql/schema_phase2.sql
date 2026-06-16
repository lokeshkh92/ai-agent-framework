CREATE TABLE IF NOT EXISTS workflow_definitions (
    workflow_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    definition_json JSONB NOT NULL,
    created_by VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_executions (
    execution_id VARCHAR PRIMARY KEY,
    workflow_id VARCHAR NOT NULL,
    workflow_version VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    trigger_type VARCHAR,
    trigger_source VARCHAR,
    input_payload JSONB,
    output_payload JSONB,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms BIGINT
);

CREATE TABLE IF NOT EXISTS node_executions (
    node_execution_id BIGSERIAL PRIMARY KEY,
    execution_id VARCHAR NOT NULL,
    node_id VARCHAR NOT NULL,
    node_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    input_payload JSONB,
    output_payload JSONB,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms BIGINT
);

CREATE TABLE IF NOT EXISTS connection_registry (
    connection_ref VARCHAR PRIMARY KEY,
    connection_type VARCHAR NOT NULL,
    config_json JSONB NOT NULL,
    created_by VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_definitions_status ON workflow_definitions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_node_executions_execution_id ON node_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_connection_registry_active ON connection_registry(is_active);
