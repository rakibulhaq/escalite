from typing import Literal

START_TIME = "start_time"
END_TIME = "end_time"
API_LOGS = "api_logs"
SERVICE_LOGS = "service_logs"
ERROR_LOGS = "error_logs"
TIME_ELAPSED = "time_elapsed"
LOG_DATE = "log_date"
LOG_LEVEL = Literal["info", "warning", "error", "debug", "critical"]
LOG_LEVELS = {
    "info": 20,
    "warning": 30,
    "error": 40,
    "debug": 10,
    "critical": 50
}
