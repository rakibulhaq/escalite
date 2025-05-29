from escalite.notifiers.base_notifier import BaseNotifier

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailNotifier(BaseNotifier):
    def notify(self, message: str, data: dict):
        pass

    def set_config(self, config: dict):
        pass


