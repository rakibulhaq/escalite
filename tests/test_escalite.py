import pytest
from escalite.escalite import Escalite


class TestEscalite:

    def test_escalite_initialization(self):
        api_key = "test_api_key"
        escalite_instance = Escalite(api_key)
        assert escalite_instance.api_key == api_key
        assert isinstance(escalite_instance.logs, dict)

    def test_start_logging(self):
        Escalite.start_logging()
        assert Escalite._logs['log_level'] == 'info'
        assert 'start_time' in Escalite._logs
        assert Escalite._logs['api_logs'] == {}
        assert Escalite._logs['service_logs'] == {}
        assert Escalite._logs['error_logs'] == {}

    def test_end_logging(self):
        Escalite.start_logging()
        Escalite.end_logging()
        assert 'end_time' in Escalite._logs
        assert 'time_elapsed' in Escalite._logs
        assert Escalite._logs['end_time'] > Escalite._logs['start_time']

    def test_add_to_log(self):
        Escalite.start_logging()
        Escalite.add_to_log("test_key", "test_value", tag="api_logs", code=200, message="Test message", level="info")

        assert "test_key" in Escalite._logs['api_logs']
        assert Escalite._logs['api_logs']["test_key"]['value'] == "test_value"
        assert Escalite._logs['api_logs']["test_key"]['code'] == 200
        assert Escalite._logs['api_logs']["test_key"]['message'] == "Test message"
        assert Escalite._logs['log_level'] == 'info'

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
        assert Escalite.get_log_level() == "info"  # Default log level is 'info' and it is not changed to 'debug'

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
        Escalite.add_to_log("test_key", "test_value", tag="api_logs", code=200, message="Test message",
                            level="info", extras={"extra_key": "extra_value"})

        assert "test_key" in Escalite._logs['api_logs']
        assert Escalite._logs['api_logs']["test_key"]['extra_key'] == "extra_value"
        Escalite.end_logging()

    def test_add_service_log(self):
        Escalite.start_logging()
        Escalite.add_service_log("oauth_service", "message from service", url="/login", code=201)

        assert "oauth_service" in Escalite._logs['service_logs']
        assert Escalite._logs['service_logs']["oauth_service"]['url'] == "/login"
        assert Escalite._logs['service_logs']["oauth_service"]['code'] == 201
        assert Escalite._logs['service_logs']["oauth_service"]['message'] == "message from service"
        Escalite.end_logging()
        print(Escalite.get_all_logs())

    def test_end_logging_without_start(self):
        with pytest.raises(RuntimeError):
            Escalite.end_logging()
