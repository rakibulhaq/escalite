import requests
from escalite.notifiers.base_notifier import BaseNotifier


class WhatsAppNotifier(BaseNotifier):

    def __init__(self):
        self.config = None

    def set_config(self, config: dict):
        required = ["api_url", "token", "to"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing '{key}' in config")
        self.config = config

    def notify(self, message: str, data: dict):
        if not self.config:
            raise ValueError("Config not set")
        payload = {
            "to": self.config["to"],
            "message": f"{message}\n{data}"
        }
        headers = {
            "Authorization": f"Bearer {self.config['token']}"
        }
        response = requests.post(self.config["api_url"], json=payload, headers=headers)
        response.raise_for_status()
