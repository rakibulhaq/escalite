import pytest
from unittest.mock import patch, MagicMock

from escalite.notifiers.email_notifier import EmailNotifier


@pytest.fixture
def email_notifier():
    return EmailNotifier()


def test_set_config(email_notifier):
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "sender@example.com",
        "sender_password": "password",
        "recipient_emails": ["recipient@example.com"],
        "use_tls": True
    }
    email_notifier.set_config(config)
    assert email_notifier.config == config


def test_notify_without_config_raises(email_notifier):
    with pytest.raises(ValueError):
        email_notifier.notify("Test message", {})


@patch("smtplib.SMTP")
def test_notify_sends_email(mock_smtp, email_notifier):
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "sender@example.com",
        "sender_password": "password",
        "recipient_emails": ["recipient@example.com"],
        "use_tls": True
    }
    email_notifier.set_config(config)
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    email_notifier.notify("Hello", {"subject": "Test"})

    mock_smtp.assert_called_with("smtp.example.com", 587)
    mock_server.starttls.assert_called()
    mock_server.login.assert_called_with("sender@example.com", "password")
    mock_server.sendmail.assert_called()
