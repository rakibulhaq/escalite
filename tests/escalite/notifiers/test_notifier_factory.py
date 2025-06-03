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
            {"type": "slack", "config": {"webhook_url": "https://hooks.slack.com/services/xxx"}},
            {"type": "whatsapp", "config": {"api_url": "http://api", "token": "abc", "to": "+123"}}
        ]
    }
    notifiers = NotifierFactory.create_notifiers(config)
    assert len(notifiers) == 2
    assert isinstance(notifiers[0], NotifierFactory.NOTIFIER_MAP["slack"])
    assert isinstance(notifiers[1], NotifierFactory.NOTIFIER_MAP["whatsapp"])
