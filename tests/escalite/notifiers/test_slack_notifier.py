import pytest
from unittest.mock import patch, MagicMock

from escalite.formatters.dict_table_formatter import DictTableFormatter
from escalite.notifiers.slack_notifier import SlackNotifier


@pytest.fixture
def slack_notifier():
    return SlackNotifier()


def test_set_config_success(slack_notifier):
    config = {"webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"}
    slack_notifier.set_config(config)
    assert slack_notifier.config == config


def test_set_config_missing_key(slack_notifier):
    config = {}
    with pytest.raises(ValueError) as exc:
        slack_notifier.set_config(config)
    assert "webhook_url" in str(exc.value)


def test_notify_without_config_raises(slack_notifier):
    slack_notifier.config = None
    with pytest.raises(ValueError):
        slack_notifier.notify("Test message", {})


@patch("escalite.notifiers.slack_notifier.requests.post")
def test_notify_sends_request(mock_post, slack_notifier):
    config = {"webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"}
    slack_notifier.set_config(config)
    mock_response = MagicMock()
    mock_post.return_value = mock_response

    slack_notifier.notify("Hello", {"foo": "bar"})
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == config["webhook_url"]
    assert "Hello" in kwargs["json"]["text"]
    mock_response.raise_for_status.assert_called_once()


def test_init_with_config_sets_config_and_default_formatter():
    config = {"webhook_url": "https://hooks.slack.com/services/xxx"}
    notifier = SlackNotifier(config=config)
    assert notifier.config == config
    assert isinstance(notifier.formatter, DictTableFormatter)


def test_init_without_config_sets_none_and_default_formatter():
    notifier = SlackNotifier()
    assert notifier.config is None
    assert isinstance(notifier.formatter, DictTableFormatter)
