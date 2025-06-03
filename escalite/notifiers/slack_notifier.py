import requests

from escalite.formatters.base_formatter import Formatter
from escalite.formatters.dict_table_formatter import DictTableFormatter
from escalite.notifiers.base_notifier import BaseNotifier


class SlackNotifier(BaseNotifier):

    def __init__(self, config: dict = None, formatter: Formatter = DictTableFormatter()):
        self.config = config
        self.formatter = formatter

    def set_config(self, config: dict):
        if "webhook_url" not in config:
            raise ValueError("Missing 'webhook_url' in config")
        self.config = config

    def notify(self, message: str, data: dict):
        if not self.config:
            raise ValueError("Config not set")
        payload = {
            "text": f"{message}\n{self.formatter.format(data)}"
        }
        response = requests.post(self.config["webhook_url"], json=payload)
        response.raise_for_status()
