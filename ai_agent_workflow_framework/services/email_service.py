from typing import List, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

SMTP_CONNECTION_TYPE = "smtp"

class EmailService:
    def __init__(self, connection_repository):
        self.connection_repository = connection_repository

    def create_message(self, TO, FROM, subject, body_content, content_type='text', attachments=None):
        message = MIMEMultipart('alternative')
        message['subject'] = subject
        message['To'] = ", ".join(TO)
        message['From'] = FROM
        if attachments:
            for _ in attachments:
                attachment = MIMEBase("application", "octet-stream")
                with open(_, 'rb') as file:
                    content = file.read()
                attachment.set_payload(content)
                encoders.encode_base64(attachment)
                attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(_))
                message.attach(attachment)

        body = MIMEText("")
        if content_type.lower() == 'html':
            body = MIMEText(body_content, 'html')
        elif content_type.lower() == 'text':
            body = MIMEText(body_content, 'text')
        message.attach(body)
        return message

    def send_email(self, connection_ref: str, recipients: List[str], subject: str, body: str,
                   attachments: Optional[List[str]] = None, content_type: str = 'text'):
        conn_cfg = self.connection_repository.get_connection(connection_ref)
        if conn_cfg["connection_type"] != SMTP_CONNECTION_TYPE:
            raise RuntimeError(f"Connection '{connection_ref}' is not a SMTP connection")

        smtp_client = smtplib.SMTP(conn_cfg["SMTP_HOST"], conn_cfg["SMTP_PORT"])
        smtp_client.login(conn_cfg["SMTP_USER"], conn_cfg["SMTP_PASSWORD"])
        message = self.create_message(recipients, conn_cfg["SMTP_SENDER"], subject, body, content_type, attachments)
        return smtp_client.send_message(message)
