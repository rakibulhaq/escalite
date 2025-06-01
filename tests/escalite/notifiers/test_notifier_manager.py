from escalite.notifiers.notifier_manager import NotifyManager


class DummyNotifier:
    def __init__(self):
        self.called = False
        self.last_message = None
        self.last_data = None

    def notify(self, message, data):
        self.called = True
        self.last_message = message
        self.last_data = data


def test_notify_manager_calls_all():
    n1 = DummyNotifier()
    n2 = DummyNotifier()
    NotifyManager.notify([n1, n2], "msg", {"foo": "bar"})
    assert n1.called
    assert n2.called
    assert n1.last_message == "msg"
    assert n1.last_data == {"foo": "bar"}


def test_notify_manager_not_instantiable():
    from pytest import raises
    with raises(NotImplementedError):
        NotifyManager()
