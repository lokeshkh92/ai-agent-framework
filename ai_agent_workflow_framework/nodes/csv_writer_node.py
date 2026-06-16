from typing import Any, Dict, List

from nodes.base_node import BaseNode


class CSVWriterNode(BaseNode):
    node_type = "csv_writer"

    def __init__(self, file_service, template_resolver):
        self.file_service = file_service
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "file_prefix" not in config:
            raise ValueError("csv_writer requires 'file_prefix'")

    def execute(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)

        rows = resolved_config.get("rows")
        if rows is None:
            rows = self._extract_rows_from_inputs(inputs)

        if not isinstance(rows, list):
            raise ValueError("csv_writer expects 'rows' to be a list of dicts")

        file_path = self.file_service.write_csv(
            rows=rows,
            file_prefix=resolved_config["file_prefix"],
            sub_dir=resolved_config.get("sub_dir", ""),
        )

        artifact = {
            "type": "csv",
            "path": file_path,
            "row_count": len(rows),
        }

        return {
            "status": "SUCCESS",
            "output": {
                "file_path": file_path,
                "row_count": len(rows),
            },
            "artifacts": [artifact],
        }

    def _extract_rows_from_inputs(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Helpful default behavior: if exactly one upstream node produced rows, use them.
        candidate_rows = []
        for upstream_output in inputs.values():
            if isinstance(upstream_output, dict):
                output = upstream_output.get("output", {})
                rows = output.get("rows")
                if isinstance(rows, list):
                    candidate_rows.append(rows)

        if len(candidate_rows) == 1:
            return candidate_rows[0]

        raise ValueError(
            "csv_writer could not infer rows from inputs. Provide config.rows explicitly."
        )
