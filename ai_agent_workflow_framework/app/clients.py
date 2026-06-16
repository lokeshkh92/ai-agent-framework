class SMTPClient:
    def send_email(self, recipients, subject, body, attachments=None):
        return True


class LLMClient:
    def generate(self, prompt):
        return f"LLM output for prompt: {prompt[:100]}"

    def generate_json(self, prompt):
        return {"summary": f"Structured output for prompt: {prompt[:100]}"}