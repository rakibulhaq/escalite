from typing import List

from escalite.notifiers.base_notifier import BaseNotifier


class NotifyManager:
    @classmethod
    def notify(cls, notifiers: List[BaseNotifier], message: str, data: dict):
        for notifier in notifiers:
            notifier.notify(message=message, data=data)
