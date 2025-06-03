import pytest
from unittest.mock import patch, MagicMock

from escalite.formatters.dict_table_formatter import DictTableFormatter
from escalite.notifiers.whatsapp_notifier import WhatsAppNotifier


@pytest.fixture
def whatsapp_notifier():
    return WhatsAppNotifier()


def test_set_config_success(whatsapp_notifier):
    config = {"api_url": "http://api", "token": "abc", "to": "+123"}
    whatsapp_notifier.set_config(config)
    assert whatsapp_notifier.config == config


@pytest.mark.parametrize("missing", ["api_url", "token", "to"])
def test_set_config_missing_key(whatsapp_notifier, missing):
    config = {"api_url": "http://api", "token": "abc", "to": "+123"}
    config.pop(missing)
    with pytest.raises(ValueError) as exc:
        whatsapp_notifier.set_config(config)
    assert missing in str(exc.value)


def test_notify_without_config_raises(whatsapp_notifier):
    whatsapp_notifier.config = None  # Ensure the notifier is un-configured
    with pytest.raises(ValueError):
        whatsapp_notifier.notify("msg", {})


@patch("escalite.notifiers.whatsapp_notifier.requests.post")
def test_notify_sends_request(mock_post, whatsapp_notifier):
    config = {"api_url": "http://api", "token": "abc", "to": "+123"}
    whatsapp_notifier.set_config(config)
    mock_response = MagicMock()
    mock_post.return_value = mock_response

    whatsapp_notifier.notify("Hello", {"foo": "bar"})
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://api"
    assert kwargs["headers"]["Authorization"] == "Bearer abc"
    assert kwargs["json"]["to"] == "+123"
    assert "Hello" in kwargs["json"]["message"]
    mock_response.raise_for_status.assert_called_once()


def test_init_with_config_sets_config_and_default_formatter():
    config = {"api_url": "http://api", "token": "abc", "to": "+123"}
    notifier = WhatsAppNotifier(config=config)
    assert notifier.config == config
    assert isinstance(notifier.formatter, DictTableFormatter)


def test_init_without_config_sets_none_and_default_formatter():
    notifier = WhatsAppNotifier()
    assert notifier.config is None
    assert isinstance(notifier.formatter, DictTableFormatter)
