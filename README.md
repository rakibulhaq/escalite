# Escalite
![Escalite Logo](https://raw.githubusercontent.com/rakibulhaq/escalite/main/logo.png)
[![PyPI version](https://img.shields.io/pypi/v/escalite.svg)](https://pypi.org/project/escalite/)
[![Python versions](https://img.shields.io/pypi/pyversions/escalite.svg)](https://pypi.org/project/escalite/)
[![codecov](https://codecov.io/gh/rakibulhaq/escalite/branch/main/graph/badge.svg)](https://codecov.io/gh/rakibulhaq/escalite)
[![Snyk](https://github.com/rakibulhaq/escalite/actions/workflows/snyk.yml/badge.svg?branch=main)](https://github.com/rakibulhaq/escalite/actions/workflows/snyk.yml)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/escalite.svg?label=PyPI%20downloads)](https://pypistats.org/packages/escalite)
[![Downloads](https://pepy.tech/badge/escalite)](https://pepy.tech/project/escalite)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



A Python library for per-request logging and escalation, designed for API services.

## Features
- Supports multiple notifiers (Email, Slack, Telegram, WhatsApp)
- Per-request logging using `contextvars`
- Unique `alert_id` generation for each log session
- Pluggable notifiers: Email, Slack, Telegram, WhatsApp and can be extended with custom notifiers
- Flexible escalation with severity filtering (`from_level`)
- Easy integration with FastAPI and other Python frameworks
- Service call lifecycle logging (`start_service_log`/`stop_service_log`)
- Context manager and manual logging support


## Installation

**Using pip:**
```bash
pip install escalite
```

**Using Poetry:**
```bash
poetry add escalite
```

## Configuration

Configure notifiers (e.g., email) in a dictionary format. Example:

```python
notifier_configs = {
    "notifiers": [
        {
            "type": "email",
            "config": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "your@email.com",
                "sender_password": "yourpassword",
                "recipient_emails": ["admin@example.com"],
                "use_tls": True
            }
        }
    ]
}
```

## Usage Example with FastAPI

```python
from fastapi import FastAPI, Request
from escalite.escalite import Escalite

app = FastAPI()
notifier_configs = {
    "notifiers": [
        {
            "type": "email",
            "config": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "your@email.com",
                "sender_password": "yourpassword",
                "recipient_emails": ["admin@example.com"],
                "use_tls": True
            }
        }
    ]
}

@app.middleware("http")
async def escalite_logging_middleware(request: Request, call_next):
    with Escalite().logging_context(notifier_configs):
        Escalite.add_to_log("request_path", str(request.url.path), tag="api_logs")
        response = await call_next(request)
        Escalite.add_to_log("response_status", response.status_code, tag="api_logs")
        return response

@app.get("/")
def read_root():
    Escalite.add_service_log("root_service", "Root endpoint accessed")
    return {"Hello": "World"}
```

**Manual Usage Example**

Here is an additional usage example for showing how to use `Escalite` without the `logging_context()` context manager. This demonstrates manual configuration, starting and ending logging, and triggering escalation.
```python
from escalite.escalite import Escalite

notifier_configs = {
    "notifiers": [
        {
            "type": "email",
            "config": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "your@email.com",
                "sender_password": "yourpassword",
                "recipient_emails": ["admin@example.com"],
                "use_tls": True
            }
        }
    ]
}

# Set up notifiers from configs
Escalite.set_notifiers_from_configs(notifier_configs)

# Start logging for a request or operation
Escalite.start_logging()

# Add logs as needed
Escalite.add_to_log("event", "User login", tag="api_logs")
Escalite.add_service_log("auth_service", "User authenticated", level="info")

# End logging and collect logs
logs = Escalite.end_logging()
print("Collected logs:", logs)

# Trigger escalation (e.g., send notifications)
Escalite.escalate()
```

This example shows explicit control over the logging lifecycle and escalation, suitable for use outside of context managers or in custom workflows.

## Usage Example - Service Call Logging

We can use `start_service_log` and `stop_service_log` to track the lifecycle of a service call:

```python
from escalite import Escalite

# Start logging for the request
Escalite.start_logging()

# Log the start of a service call
Escalite.start_service_log(
    "oauth_service",
    "Starting OAuth service",
    url="/oauth/start",
    code=200
)

# ... your service logic here ...

# Log the end of a service call
Escalite.stop_service_log(
    "oauth_service",
    "OAuth service completed",
    url="/oauth/start",
    code=200
)

# End logging and retrieve logs
Escalite.end_logging()
logs = Escalite.get_all_logs()
print(logs)
```

**Notifiers**

Here are some notifier configuration examples that are currently supported. Replace the configuration values with your actual credentials or endpoints.

**Telegram Notifier**

```python
from escalite.escalite import Escalite

notifier_configs = {
    "notifiers": [
        {
            "type": "telegram",
            "config": {
                "bot_token": "your-telegram-bot-token",
                "chat_id": "your-chat-id"
            }
        }
    ]
}

Escalite.set_notifiers_from_configs(notifier_configs)
Escalite.start_logging()
Escalite.add_to_log("event", "Telegram notifier test", tag="api_logs")
Escalite.end_logging()
Escalite.escalate()
```

**WhatsApp Notifier**

```python
from escalite.escalite import Escalite

notifier_configs = {
    "notifiers": [
        {
            "type": "whatsapp",
            "config": {
                "api_url": "https://graph.facebook.com/[version]/[phone_number_id]/messages", # Replace with your actual API URL
                "details_url": "https://escalite.com/escalite-alerts?id=", # Replace with your actual URL, Optional
                "token": "your-access-token", # Replace with your actual access token
                "to": "recipient-phone-number", # Replace with the recipient's phone number
                "payload_template": {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": "PHONE_NUMBER", # Will be replaced with the recipient's phone number from above
                    "type": "template",
                    "template": {
                        "name": "TEMPLATE_NAME", # Replace with your actual template name
                        "language": {
                            "code": "LANGUAGE_AND_LOCALE_CODE" # Replace with your actual language and locale code, e.g., "en_US"
                        },
                        "components": [
                            # Replace with your named and positional parameter inputs
                            # Currently we only support the following parameters:
                            # name, date, message, data
                            # name, data are optional
                            # message is the message generated when escalite.escalate() is called
                            # date is the current date and time when the message is sent, auto generated
                            # Format the template following this example:
                            # {
                                #"type": "body",
                                #"parameters": [
                                #    {"type": "text", "parameter_name": "name", "text": ""},
                                #    {
                                #        "type": "text",
                                #        "parameter_name": "date",
                                #        "text": time.strftime("%Y-%m-%d %H:%M:%S"),
                                #   },
                                #   {"type": "text", "parameter_name": "message", "text": None},
                                #   {"type": "text", "parameter_name": "data", "text": ""},
                                # ],
                            # }
                       ]
                     }
                }
            }
        }
    ]
}

Escalite.set_notifiers_from_configs(notifier_configs)
Escalite.start_logging()
Escalite.add_to_log("event", "WhatsApp notifier test", tag="api_logs")
Escalite.end_logging()
Escalite.escalate()
```

**Slack Notifier**

```python
from escalite.escalite import Escalite

notifier_configs = {
    "notifiers": [
        {
            "type": "slack",
            "config": {
                "webhook_url": "https://hooks.slack.com/services/your/webhook/url"
            }
        }
    ]
}

Escalite.set_notifiers_from_configs(notifier_configs)
Escalite.start_logging()
Escalite.add_to_log("event", "Slack notifier test", tag="api_logs")
Escalite.end_logging()
Escalite.escalate()
```

**Email Notifier**

```python
from escalite.escalite import Escalite

notifier_configs = {
    "notifiers": [
        {
            "type": "email",
            "config": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "your@email.com",
                "sender_password": "yourpassword",
                "recipient_emails": ["admin@example.com"],
                "use_tls": True
            }
        }
    ]
}

Escalite.set_notifiers_from_configs(notifier_configs)
Escalite.start_logging()
Escalite.add_to_log("event", "Email notifier test", tag="api_logs")
Escalite.end_logging()
Escalite.escalate()
```

**`Escalite.escalate()` with the `from_level` argument:**  
- The `from_level` parameter controls the minimum log level required to trigger escalation (e.g., "warning", "error", "critical").
- In this example, escalation will only occur if the log level is "error" or higher.

Here is an example showing how to use  This allows escalation to be triggered only if the log level is equal to or higher than the specified level.
```python
from escalite.escalite import Escalite

notifier_configs = {
    "notifiers": [
        {
            "type": "email",
            "config": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "your@email.com",
                "sender_password": "yourpassword",
                "recipient_emails": ["admin@example.com"],
                "use_tls": True
            }
        }
    ]
}

Escalite.set_notifiers_from_configs(notifier_configs)
Escalite.start_logging()
Escalite.add_to_log("event", "Something went wrong", tag="api_logs")
Escalite.add_service_log("my_service", "An error occurred", level="error")
Escalite.end_logging()

# Only escalate if the log level is "error" or higher
Escalite.escalate(from_level="error")
```

This ensures notifications are sent only for logs at the specified severity or above.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

MIT

---