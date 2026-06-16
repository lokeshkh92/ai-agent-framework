from typing import Any, Dict

from nodes.base_node import BaseNode


class SendEmailNode(BaseNode):
    node_type = "send_email"

    def __init__(self, email_service, template_resolver):
        self.email_service = email_service
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "to" not in config:
            raise ValueError("send_email requires 'to'")
        if "subject" not in config:
            raise ValueError("send_email requires 'subject'")

    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)
        body = resolved_config.get("body")
        if body is None:
            body = str(inputs)

        self.email_service.send_email(
            recipients=resolved_config["to"],
            subject=resolved_config["subject"],
            body=body,
            attachments=resolved_config.get("attachments", []),
        )

        return {
            "status": "SUCCESS",
            "output": {
                "mail_sent": True,
            },
        }
