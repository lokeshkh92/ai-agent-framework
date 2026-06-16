ADDITIONAL_NODE_SPECS = [
    {
        "type": "trino_read",
        "label": "Trino Read",
        "category": "source",
        "inputs": ["optional any"],
        "outputs": ["rows"],
        "config_schema": {
            "connection_ref": {"type": "string", "required": True},
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
    },
{
        "type": "lambda",
        "label": "Lambda Node",
        "category": "control",
        "inputs": ["any"],
        "outputs": ["results"],
        "config_schema": {
            "to_apply": {"type": str, "required": True},
            "map": {"type": dict, "required": True},
            "input": {}

        },
    },
]
