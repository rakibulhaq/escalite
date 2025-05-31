from typing import List

from escalite.notifiers.base_notifier import BaseNotifier


class NotifyManager:

    def __init__(self):
        raise NotImplementedError("NotifyManager is a static class and cannot be instantiated.")

    @staticmethod
    def notify(notifiers: List[BaseNotifier], message: str, data: dict):
        for notifier in notifiers:
            notifier.notify(message=message, data=data)
