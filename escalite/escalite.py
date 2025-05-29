import time
from typing import Any

from escalite.utils.constants import LOG_LEVEL, LOG_LEVELS, API_LOGS, START_TIME, END_TIME, SERVICE_LOGS, ERROR_LOGS, \
    TIME_ELAPSED, LOG_DATE


class Escalite:
    """
    Escalite is a Python library for managing and interacting with the Escalite API.
    It provides methods to fetch data from the API, handle pagination, and manage
    API keys securely.
    """

    _logs: dict = {}
    _logging_started: bool = False

    def __init__(self, api_key: str):
        """
        Initializes the Escalite instance with the provided API key.

        :param api_key: Your Escalite API key.
        """
        self.api_key = api_key
        # Additional initialization code can go here
        self.logs = {}

    @classmethod
    def start_logging(cls):
        """
        Starts the logging process for the Escalite instance.
        This method can be used to set up logging configurations.
        """
        # Logging setup code can go here
        print("Logging started for Escalite instance.")
        cls._logs = {
            API_LOGS: {},
            SERVICE_LOGS: {},
            ERROR_LOGS: {},
            'log_level': 'info',  # Default log level
            START_TIME: time.time(),
            END_TIME: None,
            LOG_DATE: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        cls._logging_started = True

    @classmethod
    def end_logging(cls):
        """
        Ends the logging process for the Escalite instance.
        This method can be used to clean up logging configurations.
        """
        if not cls._logging_started:
            print("Logging has not been started yet.")
            raise RuntimeError("Logging has not been started. Call start_logging() first.")
        # Logging cleanup code can go here
        print("Logging ended for Escalite instance.")
        cls._logs[END_TIME] = time.time()
        cls._logs[TIME_ELAPSED] = cls._logs[END_TIME] - cls._logs[START_TIME]

    @classmethod
    def add_to_log(cls,
                   key: str, value: Any, tag: str = None, code: int = None,
                   message: str = None, level: LOG_LEVEL = "info", extras: dict = None) -> None:
        """
        Adds a key-value pair to the log.

        :param key: The key to be added to the log.
        :param value: The value associated with the key.
        :param tag: The tag to categorize the log entry.
        :param code: The code associated with the log entry.
        :param message: The message to be logged.
        :param level: The log level (e.g., "info", "debug", "error").
        :param extras: Additional key-value pairs to be added to the log entry.
        """
        # Code to add the key-value pair to the log
        print(f"Added to log: {key} = {value}")
        if tag:
            current_time = time.time()
            cls._logs[tag][key] = {
                'value': value,
                'code': code,
                'message': message,
                'level': cls.set_log_level(level),
                'log_time': current_time,
                **(extras or {})
            }
            # check if start_time exists, if not create it
            cls._logs[tag].setdefault(START_TIME, current_time)
            # check if end_time exists, if not create it
            cls._logs[tag].setdefault(END_TIME, current_time)
            cls._logs[tag].setdefault(TIME_ELAPSED, cls._logs[tag][END_TIME] - cls._logs[tag][START_TIME])
        else:
            cls._logs[key] = {
                'value': value,
                'code': code,
                'message': message,
                'level': cls.set_log_level(level),
                'log_time': time.time(),
                **(extras or {})
            }

    @classmethod
    def get_log_level(cls, tag: str = None) -> str:
        """
        Returns the current log level.

        :return: The current log level as a string.
        """
        # Code to retrieve the current log level
        return cls._logs[tag].get('log_level', 'info') if tag else cls._logs.get('log_level', 'info')

    @classmethod
    def set_log_level(cls, new_level: LOG_LEVEL, tag: str = None, force: bool = False) -> None:
        """
        Sets the log level for the Escalite instance.

        :param force:
        :param tag:
        :param new_level: The log level to be set (e.g., "info", "debug", "error").
        """

        current_level = cls._logs[tag].get('log_level', 'info') if tag else cls._logs.get('log_level', 'info')

        if force:
            print(f"Forcefully setting log level to: {new_level}")
            cls._logs['log_level'] = new_level  # Update the global log level as well
            if tag:
                cls._logs[tag]['log_level'] = new_level

        if LOG_LEVELS[new_level] >= LOG_LEVELS[current_level]:
            cls._logs['log_level'] = new_level  # Update the global log level as well
            if tag:
                cls._logs[tag]['log_level'] = new_level
            print(f"Log level updated to: {new_level}")
        else:
            print(f"Log level '{new_level}' is not higher than current level '{current_level}'. No change made.")

    @classmethod
    def get_all_logs(cls) -> dict:
        """
        Retrieves all logs from the Escalite instance.

        :return: A list of all logs.
        """
        return cls._logs

    @classmethod
    def get_log_by_key(cls, key: str, tag: str = None) -> Any:
        """
        Retrieves a specific log entry from the Escalite instance.

        :param tag:
        :param key: The key of the log entry to be retrieved.
        :return: The log entry associated with the specified key.
        """
        return cls._logs[tag].get(key, None) if tag else cls._logs.get(key, None)

    @classmethod
    def add_service_log(cls, service_name: str, message: str, level: LOG_LEVEL = "info", url: str = None, code: int = None) -> None:
        """
        Adds a service log entry to the Escalite instance.

        :param code:
        :param service_name: The name of the service.
        :param message: The log message.
        :param level: The log level (e.g., "info", "debug", "error").
        :param url: The URL associated with the service log (optional).
        """
        cls.add_to_log(service_name, value=None, message=message, tag=SERVICE_LOGS, level=level, extras={"url": url}, code=code)
