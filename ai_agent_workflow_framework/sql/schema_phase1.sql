CREATE TABLE workflow_definitions (
    workflow_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    definition_json JSONB NOT NULL,
    created_by VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_executions (
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

CREATE TABLE node_executions (
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
