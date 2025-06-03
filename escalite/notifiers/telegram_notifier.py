import requests

from escalite.formatters.base_formatter import Formatter
from escalite.notifiers.base_notifier import BaseNotifier
from escalite.formatters.dict_table_formatter import DictTableFormatter


class TelegramNotifier(BaseNotifier):
    def __init__(self, config: dict = None, formatter: Formatter = DictTableFormatter()):
        self.config = config
        self.formatter = formatter

    def set_config(self, config: dict):
        required = ["bot_token", "chat_id"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required config: {key}")
        self.config = config

    def notify(self, message: str, data: dict):
        if not self.config:
            raise ValueError("TelegramNotifier config not set.")
        bot_token = self.config["bot_token"]
        chat_id = self.config["chat_id"]

        body = message
        if data:
            body += "\n\n" + self.formatter.format(data)

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": body
        }
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
