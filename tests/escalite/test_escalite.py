import logging
import threading
import time
import uuid

import pytest
from escalite.escalite import Escalite
from escalite.utils.constants import ALERT_ID
from contextlib import nullcontext as does_not_raise


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

    def test_add_to_log_raises_error_if_not_started(self):
        from escalite.escalite import _request_logs

        _request_logs.set(None)
        with pytest.raises(RuntimeError):
            Escalite.add_to_log("test_key", "test_value")

    def test_update_log_level(self):
        Escalite.start_logging()
        Escalite.update_log_level("debug", force=True)
        assert Escalite.get_log_level() == "debug"

        Escalite.update_log_level("error", tag="api_logs")
        assert Escalite.get_log_level(tag="api_logs") == "error"

        Escalite.end_logging()

    def test_update_log_level_does_not_change_if_no_logging_started(self):
        from escalite.escalite import _request_logs

        _request_logs.set(None)
        Escalite.update_log_level("debug")
        # Should remain 'info' since no logging has started
        assert Escalite.get_log_level() == "info"

    def test_update_log_level_does_not_change_if_a_downgrade(self):
        Escalite.start_logging()
        Escalite.update_log_level("debug")
        # Should remain 'info' since 'debug' is a lower level and force is False
        assert Escalite.get_log_level() == "info"

    def test_update_log_level_updates_if_force(self):
        Escalite.start_logging()
        Escalite.update_log_level("debug", force=True)
        assert Escalite.get_log_level() == "debug"

        Escalite.update_log_level("critical")
        Escalite.update_log_level("info", force=True)
        assert Escalite.get_log_level() == "info"

        Escalite.end_logging()

    def test_get_log_level_returns_info_if_no_logs_are_set(self):
        from escalite.escalite import _request_logs

        _request_logs.set(None)
        assert Escalite.get_log_level() == "info"

    def test_retrieves_log_by_key_when_key_exists(self):
        Escalite.start_logging()
        Escalite.add_to_log("key1", "value1")
        result = Escalite.get_log_by_key("key1")
        assert result["value"] == "value1"
        Escalite.end_logging()

    def test_retrieves_log_by_key_with_tag_when_key_exists(self):
        Escalite.start_logging()
        Escalite.add_to_log("key1", "value1", tag="API_LOGS")
        result = Escalite.get_log_by_key("key1", tag="API_LOGS")
        assert result["value"] == "value1"
        Escalite.end_logging()

    def test_returns_none_when_key_does_not_exist(self):
        Escalite.start_logging()
        result = Escalite.get_log_by_key("nonexistent_key")
        assert result is None
        Escalite.end_logging()

    def test_returns_none_when_key_does_not_exist_with_tag(self):
        Escalite.start_logging()
        result = Escalite.get_log_by_key("nonexistent_key", tag="API_LOGS")
        assert result is None
        Escalite.end_logging()

    def test_does_not_raise_error_when_logging_not_started(self):
        from escalite.escalite import _request_logs

        _request_logs.set(None)
        with does_not_raise():
            Escalite.get_log_by_key("key1")

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
        Escalite.add_service_log(
            "oauth_service", "another message", url="/logout", code=200
        )
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
            "alert_id": logs[ALERT_ID],
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

    def test_add_to_log_does_not_overwrite_existing_key_if_not_passed(self):
        Escalite.start_logging()
        Escalite.add_to_log(
            "test_key",
            "initial_value",
            tag="api_logs",
            code=200,
            message="Initial message",
            level="info",
        )
        Escalite.add_to_log(
            "test_key",
            None,  # This should not overwrite the existing value
            tag="api_logs",
            code=None,  # This should not overwrite the existing value
            message=None,  # This should not overwrite the existing value
            level="warning",
        )
        logs = Escalite.get_all_logs()
        entry = logs["api_logs"]["test_key"]

        assert entry["value"] == "initial_value"
        assert entry["code"] == 200
        assert entry["message"] == "Initial message"

    def test_start_service_log(self):
        Escalite.start_logging()
        Escalite.start_service_log(
            "oauth_service", "Starting service", url="/start", code=200
        )
        Escalite.end_logging()
        logs = Escalite.get_all_logs()
        assert "oauth_service" in logs["service_logs"]
        entry = logs["service_logs"]["oauth_service"]
        assert entry["url"] == "/start"
        assert entry["code"] == 200
        assert entry["message"] == "Starting service"
        assert "start_time" in entry
        assert "end_time" not in entry

    def test_stop_service_log(self):
        Escalite.start_logging()
        Escalite.start_service_log(
            "oauth_service", "Starting service", url="/start", code=200
        )
        Escalite.stop_service_log(
            "oauth_service",
            "Stopping service",
            url="/stop",
            code=500,
            error_trace="Traceback",
        )
        Escalite.end_logging()
        logs = Escalite.get_all_logs()

        assert "oauth_service" in logs["service_logs"]
        entry = logs["service_logs"]["oauth_service"]
        assert entry["url"] == "/stop"
        assert entry["code"] == 500
        assert entry["message"] == "Stopping service"
        assert entry["error_trace"] == "Traceback"
        assert "start_time" in entry
        assert "end_time" in entry

    @pytest.fixture
    def simulate_request(self):
        def _simulate_request(log_value, result_list, idx):
            Escalite.start_logging()
            Escalite.add_to_log("api_call", log_value, tag="api_logs")
            time.sleep(0.1)
            logs = Escalite.end_logging()
            result_list[idx] = logs["api_logs"]["api_call"]["value"]

        return _simulate_request

    def test_contextvar_is_isolated_across_threads(self, simulate_request):
        num_threads = 5
        results = [None] * num_threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(
                target=simulate_request, args=(f"value_{i}", results, i)
            )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        assert results == [f"value_{i}" for i in range(num_threads)]

    def test_alert_id_is_unique_and_valid(self):
        Escalite.start_logging()
        logs1 = Escalite.get_all_logs()
        alert_id1 = logs1[ALERT_ID]
        Escalite.end_logging()

        Escalite.start_logging()
        logs2 = Escalite.get_all_logs()
        alert_id2 = logs2[ALERT_ID]
        Escalite.end_logging()

        # Check both are valid UUIDs
        uuid_obj1 = uuid.UUID(alert_id1)
        uuid_obj2 = uuid.UUID(alert_id2)
        assert str(uuid_obj1) == alert_id1
        assert str(uuid_obj2) == alert_id2

        # Check they are unique
        assert alert_id1 != alert_id2

    def test_route_logging_decorator(self, monkeypatch):
        called = {}

        # Mock notifier and escalate
        class DummyNotifier:
            def notify(self, message, log_data):
                called["notified"] = True
                called["message"] = message
                called["log_data"] = log_data

        monkeypatch.setattr(
            "escalite.notifiers.notifier_factory.NotifierFactory.create_notifiers",
            lambda cfg: [DummyNotifier()],
        )
        monkeypatch.setattr(
            "escalite.notifiers.notifier_factory.NotifierFactory.notify",
            lambda notifiers, message, log_data: notifiers[0].notify(message, log_data),
        )

        configs = {"notifiers": [{"type": "dummy"}]}

        @Escalite.route_logging(configs=configs, log_level="info")
        def sample_route():
            Escalite.add_to_log("test_key", "test_value")
            return "ok"

        result = sample_route()
        logs = Escalite.get_all_logs()

        assert result == "ok"
        assert ALERT_ID in logs
        assert logs["test_key"]["value"] == "test_value"
        assert called.get("notified") is True
        assert "log_level" in called["log_data"]
