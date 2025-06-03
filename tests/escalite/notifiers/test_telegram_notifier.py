import pytest
from unittest.mock import patch, MagicMock

from escalite.formatters.dict_table_formatter import DictTableFormatter
from escalite.notifiers.telegram_notifier import TelegramNotifier


@pytest.fixture
def telegram_notifier():
    return TelegramNotifier()


def test_set_config_success(telegram_notifier):
    config = {"bot_token": "token", "chat_id": "12345"}
    telegram_notifier.set_config(config)
    assert telegram_notifier.config == config


def test_set_config_missing_key(telegram_notifier):
    with pytest.raises(ValueError):
        telegram_notifier.set_config({"bot_token": "token"})


def test_notify_without_config_raises(telegram_notifier):
    with pytest.raises(ValueError):
        telegram_notifier.notify("msg", {})


@patch("escalite.notifiers.telegram_notifier.requests.post")
def test_notify_sends_message(mock_post, telegram_notifier):
    config = {"bot_token": "token", "chat_id": "12345"}
    telegram_notifier.set_config(config)
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    data = {"foo": "bar"}
    telegram_notifier.notify("Hello", data)

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert "https://api.telegram.org/bot" in args[0]
    assert kwargs["data"]["chat_id"] == "12345"
    assert "Hello" in kwargs["data"]["text"]
    assert "foo" in kwargs["data"]["text"]


def test_init_with_config_sets_config_and_default_formatter():
    config = {"bot_token": "token", "chat_id": "12345"}
    notifier = TelegramNotifier(config=config)
    assert notifier.config == config
    assert isinstance(notifier.formatter, DictTableFormatter)


def test_init_without_config_sets_none_and_default_formatter():
    notifier = TelegramNotifier()
    assert notifier.config is None
    assert isinstance(notifier.formatter, DictTableFormatter)
