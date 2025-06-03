import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from escalite.notifiers.base_notifier import BaseNotifier


class EmailNotifier(BaseNotifier):
    def __init__(self, config: dict = None):
        self.config = config

    def set_config(self, config: dict):
        # Expected keys: smtp_server, smtp_port, sender_email,
        # sender_password, recipient_emails (list or str), use_tls (bool)
        self.config = config

    def notify(self, message: str, data: dict):
        if not self.config:
            raise ValueError("EmailNotifier config not set. Call set_config first.")

        smtp_server = self.config.get("smtp_server")
        smtp_port = self.config.get("smtp_port", 587)
        sender_email = self.config.get("sender_email")
        sender_password = self.config.get("sender_password")
        recipient_emails = self.config.get("recipient_emails")
        use_tls = self.config.get("use_tls", True)

        if isinstance(recipient_emails, str):
            recipient_emails = [recipient_emails]

        subject = data.get("subject", "Notification")
        body = message

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipient_emails)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if use_tls:
                server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_emails, msg.as_string())
