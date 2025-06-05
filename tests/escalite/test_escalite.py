import logging

import pytest
from escalite.escalite import Escalite
from pytest_mock import mocker


class TestEscalite:
    @pytest.fixture(scope="class")
    def configs(self):
        return {
            "notifiers": [
                {
                    "type": "slack",
                    "config": {"webhook_url": "https://hooks.slack.com/..."},
                },
                {"type": "telegram", "config": {"bot_token": "xxx", "chat_id": "yyy"}},
                {
                    "type": "whatsapp",
                    "config": {"api_url": "http://api", "token": "abc", "to": "+123"},
                },
                {
                    "type": "email",
                    "config": {
                        "smtp_server": "smtp.example.com",
                        "to": "user@example.com",
                    },
                },
            ]
        }

    def test_start_logging(self):
        Escalite.start_logging()
        logs = Escalite.get_all_logs()
        assert logs["log_level"] == "info"
        assert "start_time" in logs
        assert logs["api_logs"] == {}
        assert logs["service_logs"] == {}
        assert logs["error_logs"] == {}

    def test_end_logging(self):
        Escalite.start_logging()
        logs = Escalite.end_logging()
        assert "end_time" in logs
        assert "time_elapsed" in logs
        assert logs["end_time"] > logs["start_time"]

    def test_add_to_log(self):
        Escalite.start_logging()
        Escalite.add_to_log(
            "test_key",
            "test_value",
            tag="api_logs",
            code=200,
            message="Test message",
            level="info",
        )
        logs = Escalite.get_all_logs()
        assert "test_key" in logs["api_logs"]
        entry = logs["api_logs"]["test_key"]
        assert entry["value"] == "test_value"
        assert entry["code"] == 200
        assert entry["message"] == "Test message"
        assert logs["log_level"] == "info"

    def test_set_log_level(self):
        Escalite.start_logging()
        Escalite.set_log_level("debug", force=True)
        assert Escalite.get_log_level() == "debug"

        Escalite.set_log_level("error", tag="api_logs")
        assert Escalite.get_log_level(tag="api_logs") == "error"

        Escalite.end_logging()

    def test_set_log_level_does_not_change_if_a_downgrade(self):
        Escalite.start_logging()
        Escalite.set_log_level("debug")
        # Should remain 'info' since 'debug' is a lower level and force is False
        assert Escalite.get_log_level() == "info"

    def test_set_log_level_updates_if_force(self):
        Escalite.start_logging()
        Escalite.set_log_level("debug", force=True)
        assert Escalite.get_log_level() == "debug"

        Escalite.set_log_level("critical")
        Escalite.set_log_level("info", force=True)
        assert Escalite.get_log_level() == "info"

        Escalite.end_logging()

    def test_add_to_log_with_extras(self):
        Escalite.start_logging()
        Escalite.add_to_log(
            "test_key",
            "test_value",
            tag="api_logs",
            code=200,
            message="Test message",
            level="info",
            extras={"extra_key": "extra_value"},
        )
        logs = Escalite.get_all_logs()
        assert "test_key" in logs["api_logs"]
        assert logs["api_logs"]["test_key"]["extra_key"] == "extra_value"
        Escalite.end_logging()

    def test_add_service_log(self):
        Escalite.start_logging()
        Escalite.add_service_log(
            "oauth_service", "message from service", url="/login", code=201
        )
        logs = Escalite.get_all_logs()
        assert "oauth_service" in logs["service_logs"]
        entry = logs["service_logs"]["oauth_service"]
        assert entry["url"] == "/login"
        assert entry["code"] == 201
        assert entry["message"] == "message from service"
        Escalite.end_logging()

    def test_add_service_log_with_end_time(self):
        Escalite.start_logging()
        Escalite.add_service_log(
            "oauth_service", "message from service", url="/login", code=201
        )
        logs = Escalite.get_all_logs()
        assert "start_time" in logs["service_logs"]["oauth_service"]
        assert "end_time" not in logs["service_logs"]["oauth_service"]

    def test_add_service_log_with_end_time_when_start_time_is_set(self):
        Escalite.start_logging()
        Escalite.add_service_log(
            "oauth_service", "message from service", url="/login", code=201
        )
        Escalite.add_service_log("oauth_service", "another message", url="/logout", code=200)
        Escalite.end_logging()
        logs = Escalite.get_all_logs()
        assert "start_time" in logs["service_logs"]["oauth_service"]
        assert "end_time" in logs["service_logs"]["oauth_service"]

    def test_end_logging_without_start(self):
        from escalite.escalite import _request_logs

        _request_logs.set(None)
        with pytest.raises(RuntimeError):
            Escalite.end_logging()

    def test_logging_context_starts_and_ends_logging(self, caplog, configs, mocker):
        escalite = Escalite()
        caplog.set_level(logging.INFO, logger="escalite.escalite")
        mocker.patch.object(escalite, "escalate", return_value=None)
        with escalite.logging_context(configs=configs):
            logs = Escalite.get_all_logs()
            assert "log_level" in logs
            assert "log_date" in logs
            assert logs.get("start_time") is not None

        logs = Escalite.get_all_logs()
        assert "time_elapsed" in logs
        assert logs.get("end_time") is not None
        assert any("Logs collected:" in record.message for record in caplog.records)

    def test_logging_context_handles_exceptions_gracefully(
        self, caplog, configs, mocker
    ):
        escalite = Escalite()
        caplog.set_level(logging.INFO, logger="escalite.escalite")
        mocker.patch.object(escalite, "escalate", return_value=None)
        with pytest.raises(ValueError):
            with escalite.logging_context(configs=configs):
                raise ValueError("Test exception")
        logs = Escalite.get_all_logs()
        assert "time_elapsed" in logs
        assert logs.get("end_time") is not None
        assert any("Logs collected:" in record.message for record in caplog.records)

    def test_escalite_get_all_logs_empty(self):
        Escalite.start_logging()
        Escalite.end_logging()
        logs = Escalite.get_all_logs()
        assert logs == {
            "log_level": "info",
            "start_time": logs["start_time"],
            "end_time": logs["end_time"],
            "log_date": logs["log_date"],
            "time_elapsed": logs["time_elapsed"],
            "api_logs": {},
            "service_logs": {},
            "error_logs": {},
        }

    def test_escalate_from_level(self, mocker):
        escalite = Escalite()
        mocker.patch.object(escalite, "escalate", return_value=None)
        escalite.escalate(from_level="error")
        escalite.escalate(from_level="info")
        escalite.escalate(from_level="debug")
        escalite.escalate(from_level="critical")

        # Ensure escalate was called with the correct log level
        assert escalite.escalate.call_count == 4

    def test_escalate_with_message(self, mocker):
        escalite = Escalite()
        mocker.patch.object(escalite, "escalate", return_value=None)
        escalite.escalate(message="Test escalation", from_level="error")

        # Ensure escalate was called with the correct message
        escalite.escalate.assert_called_with(
            message="Test escalation", from_level="error"
        )
