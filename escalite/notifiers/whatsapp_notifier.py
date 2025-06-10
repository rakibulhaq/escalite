import time

import requests

from escalite.formatters.base_formatter import Formatter
from escalite.formatters.dict_table_formatter import DictTableFormatter
from escalite.notifiers.base_notifier import BaseNotifier


class WhatsAppNotifier(BaseNotifier):

    _payload_template = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": None,
        "type": "template",
        "template": {
            "name": "escalite_alert",
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "parameter_name": "name", "text": ""},
                        {
                            "type": "text",
                            "parameter_name": "date",
                            "text": time.strftime("%Y-%m-%d %H:%M:%S"),
                        },
                        {"type": "text", "parameter_name": "message", "text": None},
                        {"type": "text", "parameter_name": "data", "text": ""},
                    ],
                }
            ],
        },
    }

    def __init__(
        self, config: dict = None, formatter: Formatter = DictTableFormatter()
    ):
        self.config = config
        self.formatter = formatter

    def set_config(self, config: dict):
        required = [
            "api_url",
            "token",
            "to",
        ]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing '{key}' in config")
        self.config = config

    def notify(self, message: str, data: dict):
        if not self.config:
            raise ValueError("Config not set")
        # Currently, the payload template is fixed, and we expect it to be matching the format specified in the issue#22
        payload = self.config.get(
            "payload_template", WhatsAppNotifier._payload_template
        )
        payload["to"] = self.config["to"]
        payload["template"]["components"][0]["parameters"][0]["text"] = self.config.get(
            "name", ""
        )
        payload["template"]["components"][0]["parameters"][1]["text"] = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        payload["template"]["components"][0]["parameters"][2]["text"] = message
        # TODO: Add alert id to the message and link to the Escalite dashboard
        details = self.config.get(
            "details_url", "https://escalite.com/escalite-alerts?id="
        )
        payload["template"]["components"][0]["parameters"][3]["text"] = details + str(
            data.get("alert_id", "")
        )

        headers = {"Authorization": f"Bearer {self.config['token']}"}
        response = requests.post(self.config["api_url"], json=payload, headers=headers)
        response.raise_for_status()
