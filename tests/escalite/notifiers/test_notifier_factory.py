from escalite.notifiers.base_notifier import BaseNotifier
from escalite.notifiers.notifier_factory import NotifierFactory


class DummyNotifier:
    def __init__(self):
        self.called = False
        self.last_message = None
        self.last_data = None

    def notify(self, message, data):
        self.called = True
        self.last_message = message
        self.last_data = data


def test_notify_factory_calls_all():
    n1 = DummyNotifier()
    n2 = DummyNotifier()
    NotifierFactory.notify([n1, n2], "msg", {"foo": "bar"})
    assert n1.called
    assert n2.called
    assert n1.last_message == "msg"
    assert n1.last_data == {"foo": "bar"}


def test_create_notifiers():
    config = {
        "notifiers": [
            {
                "type": "slack",
                "config": {"webhook_url": "https://hooks.slack.com/services/xxx"},
            },
            {
                "type": "whatsapp",
                "config": {"api_url": "http://api", "token": "abc", "to": "+123"},
            },
            {
                "type": "telegram",
                "config": {"bot_token": "xxx", "chat_id": "yyy"},
            },
        ]
    }
    notifiers = NotifierFactory.create_notifiers(config)
    assert len(notifiers) == 3
    assert isinstance(notifiers[0], NotifierFactory.NOTIFIER_MAP["slack"])
    assert isinstance(notifiers[1], NotifierFactory.NOTIFIER_MAP["whatsapp"])
    assert isinstance(notifiers[2], NotifierFactory.NOTIFIER_MAP["telegram"])


def test_add_notifier_map_valid_notifier_type():
    class MockNotifier(BaseNotifier):
        def set_config(self, config: dict):
            pass

        def notify(self, message: str, data: dict):
            pass

    NotifierFactory.add_notifier_map("mock", MockNotifier)
    assert "mock" in NotifierFactory.NOTIFIER_MAP
    assert NotifierFactory.NOTIFIER_MAP["mock"] == MockNotifier


def test_add_notifier_map_invalid_notifier_type():
    class InvalidNotifier:
        def notify(self, message: str, data: dict):
            pass

    try:
        NotifierFactory.add_notifier_map("invalid", InvalidNotifier)
    except ValueError as e:
        assert (
            str(e)
            == "Notifier class <class 'tests.escalite.notifiers.test_notifier_factory"
            ".test_add_notifier_map_invalid_notifier_type.<locals>.InvalidNotifier'> must inherit from BaseNotifier"
        )
