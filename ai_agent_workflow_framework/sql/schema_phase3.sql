ALTER TABLE workflow_definitions
    ADD COLUMN IF NOT EXISTS last_published_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_workflow_definitions_updated_at ON workflow_definitions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_node_executions_node_id ON node_executions(node_id);
