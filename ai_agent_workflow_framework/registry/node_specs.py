NODE_SPECS = [
    {
        "type": "postgres_read",
        "label": "Postgres Read",
        "category": "source",
        "inputs": [],
        "outputs": ["rows"],
        "config_schema": {
            "connection_ref": {"type": "string", "required": True},
            "query": {"type": "string", "required": True},
        },
    },
    {
        "type": "python_script",
        "label": "Python Script",
        "category": "transform",
        "inputs": ["any"],
        "outputs": ["result"],
        "config_schema": {
            "script": {"type": "string", "required": True},
        },
    },
    {
        "type": "llm_infer",
        "label": "LLM Infer",
        "category": "ai",
        "inputs": ["any"],
        "outputs": ["result"],
        "config_schema": {
            "prompt_template": {"type": "string", "required": True},
            "model": {"type": "string", "required": False},
            "output_mode": {"type": "string", "required": False},
        },
    },
    {
        "type": "send_email",
        "label": "Send Email",
        "category": "sink",
        "inputs": ["any"],
        "outputs": ["mail_sent"],
        "config_schema": {
            "to": {"type": "array", "required": True},
            "subject": {"type": "string", "required": True},
            "body": {"type": "string", "required": False},
            "attachments": {"type": "array", "required": False},
        },
    },
    {
        "type": "ui_render",
        "label": "UI Render",
        "category": "sink",
        "inputs": ["any"],
        "outputs": ["component", "data"],
        "config_schema": {
            "component": {"type": "string", "required": True},
        },
    },
{
        "type": "trino_read",
        "label": "Trino Read",
        "category": "source",
        "inputs": ["optional any"],
        "outputs": ["rows"],
        "config_schema": {
            "query": {"type": "string", "required": True},
        },
    },
    {
        "type": "if_else",
        "label": "If / Else",
        "category": "control",
        "inputs": ["any"],
        "outputs": ["condition_result", "selected_branch", "next_node_hint"],
        "config_schema": {
            "condition": {
                "type": "object",
                "required": True,
                "example": {
                    "left": "{{node_outputs.node_1.output.row_count}}",
                    "operator": "gt",
                    "right": 0,
                },
            },
            "true_next": {"type": "string", "required": False},
            "false_next": {"type": "string", "required": False},
        },
    },
    {
        "type": "csv_writer",
        "label": "CSV Writer",
        "category": "sink",
        "inputs": ["rows"],
        "outputs": ["file_path", "row_count"],
        "config_schema": {
            "file_prefix": {"type": "string", "required": True},
            "sub_dir": {"type": "string", "required": False},
            "rows": {"type": "array", "required": False},
        },
    },
    {
        "type": "hdfs_list",
        "label": "HDFS List",
        "category": "source",
        "inputs": ["optional any"],
        "outputs": ["path", "exists", "file_count", "files"],
        "config_schema": {
            "path": {"type": "string", "required": True},
        },
    }
]
