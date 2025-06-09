import logging
import time
import contextvars
from contextlib import contextmanager
from typing import Any

from escalite.notifiers.notifier_factory import NotifierFactory
from escalite.utils.constants import (
    LOG_LEVEL,
    LOG_LEVELS,
    API_LOGS,
    START_TIME,
    END_TIME,
    SERVICE_LOGS,
    ERROR_LOGS,
    TIME_ELAPSED,
    LOG_DATE,
)

# Context variable for per-request logs
_request_logs = contextvars.ContextVar("_request_logs", default=None)

logger = logging.getLogger(__name__)


class Escalite:
    """
    Escalite is a Python library for per-request logging using contextvars.
    """

    notifiers = None

    @staticmethod
    def start_logging():
        """
        Starts per-request logging by initializing the context variable.
        """
        logs = {
            API_LOGS: {},
            SERVICE_LOGS: {},
            ERROR_LOGS: {},
            "log_level": "info",
            START_TIME: time.time(),
            END_TIME: None,
            LOG_DATE: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        _request_logs.set(logs)

    @staticmethod
    def end_logging():
        """
        Ends per-request logging and returns the collected logs.
        """
        logs = _request_logs.get()
        if logs is None:
            raise RuntimeError(
                "Logging has not been started. Call start_logging() first."
            )
        logs[END_TIME] = time.time()
        logs[TIME_ELAPSED] = logs[END_TIME] - logs[START_TIME]
        return logs

    @staticmethod
    def add_to_log(
        key: str,
        value: Any,
        tag: str = None,
        code: int = None,
        message: str = None,
        level: LOG_LEVEL = "info",
        extras: dict = None,
    ) -> None:
        """
        Adds a log entry to the current request's logs.
        Args:
            key (str): The key for the log entry.
            value (Any): The value associated with the key.
            tag (str, optional): The log section (e.g., API, service, error). Defaults to None.
            code (int, optional): An optional code to associate with the log entry. Defaults to None.
            message (str, optional): An optional message for the log entry. Defaults to None.
            level (LOG_LEVEL, optional): The log level (e.g., info, warning, error). Defaults to "info".
            extras (dict, optional): Additional data to include in the log entry. Defaults to None.
        """
        logs = _request_logs.get()
        if logs is None:
            raise RuntimeError(
                "Logging has not been started. Call start_logging() first."
            )
        if tag:
            current_time = time.time()
            # check if the key already exists in the logs for the given tag
            # if it does, we will update the existing log entry
            # otherwise, we will create a new one
            if tag not in logs:
                logs[tag] = {}
            if key in logs[tag]:
                # If the key already exists, we update the existing log entry
                logs[tag][key]["value"] = (
                    value if value is not None else logs[tag][key].get("value")
                )
                logs[tag][key]["code"] = (
                    code if code is not None else logs[tag][key].get("code")
                )
                logs[tag][key]["message"] = (
                    message if message is not None else logs[tag][key].get("message")
                )
                logs[tag][key]["log_level"] = Escalite.set_log_level(level, tag=tag)
                logs[tag][key]["log_time"] = current_time
                logs[tag][key].setdefault(START_TIME, current_time)
                logs[tag][key].setdefault(END_TIME, current_time)
                logs[tag][key].setdefault(
                    TIME_ELAPSED, logs[tag][key][END_TIME] - logs[tag][key][START_TIME]
                )
                reserved_keys = {START_TIME, END_TIME, TIME_ELAPSED}
                filtered_extras = {
                    k: v for k, v in (extras or {}).items() if k not in reserved_keys
                }
                logs[tag][key].update(filtered_extras)
            else:
                # If the key does not exist, we create a new log entry
                logs[tag][key] = {
                    "value": value,
                    "code": code,
                    "message": message,
                    "log_level": Escalite.set_log_level(level, tag=tag),
                    "log_time": current_time,
                    **(extras or {}),
                }

            # If START_TIME is already set, we update END_TIME and TIME_ELAPSED
            # to reflect the current time
            # This is useful for cases where the log entry is updated multiple times
            # during the request lifecycle, and we want to keep track of the latest timing.
            # If START_TIME is not set, it will be set later when the log entry is created
            # or updated.

            if START_TIME in logs[tag][key]:
                logs[tag][key].setdefault(END_TIME, current_time)
                logs[tag][key].setdefault(
                    TIME_ELAPSED, logs[tag][key][END_TIME] - logs[tag][key][START_TIME]
                )

            logs[tag][key].setdefault(START_TIME, current_time)

        else:
            logs[key] = {
                "value": value,
                "code": code,
                "message": message,
                "log_level": Escalite.set_log_level(level),
                "log_time": time.time(),
                **(extras or {}),
            }

    @staticmethod
    def get_log_level(tag: str = None) -> str:
        logs = _request_logs.get()
        if logs is None:
            return "info"
        return (
            logs[tag].get("log_level", "info") if tag else logs.get("log_level", "info")
        )

    @staticmethod
    def set_log_level(
        new_level: LOG_LEVEL, tag: str = None, force: bool = False
    ) -> str:
        logs = _request_logs.get()
        if logs is None:
            return new_level
        current_level = (
            logs[tag].get("log_level", "info") if tag else logs.get("log_level", "info")
        )
        if force or LOG_LEVELS[new_level] >= LOG_LEVELS[current_level]:
            logs["log_level"] = new_level
            if tag:
                logs[tag]["log_level"] = new_level
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
    def add_service_log(
        service_name: str,
        message: str,
        level: LOG_LEVEL = "info",
        url: str = None,
        code: int = None,
    ) -> None:
        Escalite.add_to_log(
            service_name,
            value=None,
            message=message,
            tag=SERVICE_LOGS,
            level=level,
            extras={"url": url},
            code=code,
        )

    @staticmethod
    def start_service_log(
        service_name: str,
        message: str,
        level: LOG_LEVEL = "info",
        url: str = None,
        code: int = None,
    ) -> None:
        Escalite.add_to_log(
            service_name,
            value=None,
            message=message,
            tag=SERVICE_LOGS,
            level=level,
            extras={"url": url},
            code=code,
        )

    @staticmethod
    def stop_service_log(
        service_name: str,
        message: str,
        level: LOG_LEVEL = "info",
        url: str = None,
        code: int = None,
        error_trace: str = None,
    ) -> None:
        Escalite.add_to_log(
            service_name,
            value=None,
            message=message,
            tag=SERVICE_LOGS,
            level=level,
            extras=(
                {"url": url}
                if error_trace is None
                else {"url": url, "error_trace": error_trace}
            ),
            code=code,
        )

    # function using contextmanager to start and end logging automatically
    @contextmanager
    def logging_context(self, configs: dict, log_level: LOG_LEVEL = "info"):
        """
        Context manager to automatically start and end logging.
        """
        self.set_notifiers_from_configs(configs)
        self.start_logging()
        try:
            yield
        finally:
            self.end_logging()
            # Here you can process the logs, e.g., save to a file or send to a server
            logger.info(
                f"Logs collected:  {Escalite.get_all_logs()}"
            )  # For demonstration purposes
            self.escalate(from_level=log_level)

    @staticmethod
    def set_notifiers_from_configs(configs: dict):
        """
        Sets the notifiers based on the provided configuration.
        """
        Escalite.notifiers = NotifierFactory.create_notifiers(configs)

    @staticmethod
    def escalate(message: str = None, from_level: LOG_LEVEL = "error"):
        """
        Placeholder for the escalate method.
        This can be used to trigger notifications or other actions based on the logs.
        """
        log_data = Escalite.get_all_logs()

        if not log_data:
            logger.info("No logs to escalate.")
            return

        if not (
            LOG_LEVELS[log_data.get("log_level", "info")] >= LOG_LEVELS[from_level]
        ):
            logger.info("No logs to escalate based on the specified level.")
            return

        message = (
            message
            if message
            else "Escalation triggered: "
            + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        if Escalite.notifiers is None:
            raise RuntimeError(
                "No notifiers set. Call set_notifiers_from_configs() first."
            )
        NotifierFactory.notify(Escalite.notifiers, message, log_data)
        logger.info(f"Escalation completed with data: {log_data}")
