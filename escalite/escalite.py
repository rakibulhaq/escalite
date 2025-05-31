import time
import contextvars
from typing import Any

from escalite.utils.constants import LOG_LEVEL, LOG_LEVELS, API_LOGS, START_TIME, END_TIME, SERVICE_LOGS, ERROR_LOGS, \
    TIME_ELAPSED, LOG_DATE

# Context variable for per-request logs
_request_logs = contextvars.ContextVar("_request_logs", default=None)


class Escalite:
    """
    Escalite is a Python library for managing and interacting with the Escalite API.
    Provides per-request logging using contextvars.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def start_logging():
        """
        Starts per-request logging by initializing the context variable.
        """
        logs = {
            API_LOGS: {},
            SERVICE_LOGS: {},
            ERROR_LOGS: {},
            'log_level': 'info',
            START_TIME: time.time(),
            END_TIME: None,
            LOG_DATE: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        _request_logs.set(logs)

    @staticmethod
    def end_logging():
        """
        Ends per-request logging and returns the collected logs.
        """
        logs = _request_logs.get()
        if logs is None:
            raise RuntimeError("Logging has not been started. Call start_logging() first.")
        logs[END_TIME] = time.time()
        logs[TIME_ELAPSED] = logs[END_TIME] - logs[START_TIME]
        return logs

    @staticmethod
    def add_to_log(
            key: str, value: Any, tag: str = None, code: int = None,
            message: str = None, level: LOG_LEVEL = "info", extras: dict = None
    ) -> None:
        """
        Adds a key-value pair to the per-request log.
        """
        logs = _request_logs.get()
        if logs is None:
            raise RuntimeError("Logging has not been started. Call start_logging() first.")
        if tag:
            current_time = time.time()
            logs[tag][key] = {
                'value': value,
                'code': code,
                'message': message,
                'level': Escalite.set_log_level(level, tag=tag),
                'log_time': current_time,
                **(extras or {})
            }
            logs[tag].setdefault(START_TIME, current_time)
            logs[tag].setdefault(END_TIME, current_time)
            logs[tag].setdefault(TIME_ELAPSED, logs[tag][END_TIME] - logs[tag][START_TIME])
        else:
            logs[key] = {
                'value': value,
                'code': code,
                'message': message,
                'level': Escalite.set_log_level(level),
                'log_time': time.time(),
                **(extras or {})
            }

    @staticmethod
    def get_log_level(tag: str = None) -> str:
        logs = _request_logs.get()
        if logs is None:
            return 'info'
        return logs[tag].get('log_level', 'info') if tag else logs.get('log_level', 'info')

    @staticmethod
    def set_log_level(new_level: LOG_LEVEL, tag: str = None, force: bool = False) -> str:
        logs = _request_logs.get()
        if logs is None:
            return new_level
        current_level = logs[tag].get('log_level', 'info') if tag else logs.get('log_level', 'info')
        if force or LOG_LEVELS[new_level] >= LOG_LEVELS[current_level]:
            logs['log_level'] = new_level
            if tag:
                logs[tag]['log_level'] = new_level
        return new_level

    @staticmethod
    def get_all_logs() -> dict:
        logs = _request_logs.get()
        return logs if logs is not None else {}

    @staticmethod
    def get_log_by_key(key: str, tag: str = None) -> Any:
        logs = _request_logs.get()
        if logs is None:
            return None
        return logs[tag].get(key, None) if tag else logs.get(key, None)

    @staticmethod
    def add_service_log(service_name: str, message: str, level: LOG_LEVEL = "info", url: str = None,
                        code: int = None) -> None:
        Escalite.add_to_log(service_name, value=None, message=message, tag=SERVICE_LOGS, level=level,
                            extras={"url": url}, code=code)
