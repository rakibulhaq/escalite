from typing import List

from escalite.notifiers.base_notifier import BaseNotifier
from escalite.notifiers.email_notifier import EmailNotifier
from escalite.notifiers.slack_notifier import SlackNotifier
from escalite.notifiers.telegram_notifier import TelegramNotifier
from escalite.notifiers.whatsapp_notifier import WhatsAppNotifier


class NotifierFactory:
    NOTIFIER_MAP = {
        "slack": SlackNotifier,
        "telegram": TelegramNotifier,
        "whatsapp": WhatsAppNotifier,
        "email": EmailNotifier,
    }

    @staticmethod
    def create_notifiers(config: dict):
        notifiers = []
        for notifier_cfg in config.get("notifiers", []):
            notifier_type = notifier_cfg.get("type")
            notifier_conf = notifier_cfg.get("config", {})
            notifier_cls = NotifierFactory.NOTIFIER_MAP.get(notifier_type)
            if notifier_cls is None:
                raise ValueError(f"Unknown notifier type: {notifier_type}")
            notifiers.append(notifier_cls(config=notifier_conf))
        return notifiers

    @staticmethod
    def notify(notifiers: List[BaseNotifier], message: str, data: dict):
        for notifier in notifiers:
            notifier.notify(message=message, data=data)
