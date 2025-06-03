# Escalite

[![PyPI version](https://img.shields.io/pypi/v/escalite.svg)](https://pypi.org/project/escalite/)
[![Python versions](https://img.shields.io/pypi/pyversions/escalite.svg)](https://pypi.org/project/escalite/)

A Python library for per-request logging and escalation, designed for API services.

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
    "email": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "your@email.com",
        "sender_password": "yourpassword",
        "recipient_emails": ["admin@example.com"],
        "use_tls": True
    }
}
```

## Usage Example with FastAPI

```python
from fastapi import FastAPI, Request
from escalite.escalite import Escalite

app = FastAPI()
notifier_configs = {
    "email": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "your@email.com",
        "sender_password": "yourpassword",
        "recipient_emails": ["admin@example.com"],
        "use_tls": True
    }
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
    "email": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "your@email.com",
        "sender_password": "yourpassword",
        "recipient_emails": ["admin@example.com"],
        "use_tls": True
    }
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

**Notifiers**

Here are some notifier configuration examples that are currently supported. Replace the configuration values with your actual credentials or endpoints.

**Telegram Notifier**

```python
from escalite.escalite import Escalite

notifier_configs = {
    "telegram": {
        "bot_token": "your-telegram-bot-token",
        "chat_id": "your-chat-id"
    }
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
    "whatsapp": {
        "api_url": "https://your-whatsapp-api-endpoint.com/send",
        "access_token": "your-access-token",
        "phone_number": "recipient-phone-number"
    }
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
    "slack": {
        "webhook_url": "https://hooks.slack.com/services/your/webhook/url"
    }
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
    "email": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "your@email.com",
        "sender_password": "yourpassword",
        "recipient_emails": ["admin@example.com"],
        "use_tls": True
    }
}

Escalite.set_notifiers_from_configs(notifier_configs)
Escalite.start_logging()
Escalite.add_to_log("event", "Email notifier test", tag="api_logs")
Escalite.end_logging()
Escalite.escalate()
```

## Features

- Per-request logging using contextvars
- Pluggable notifiers (email, etc.)
- Easy integration with FastAPI and other frameworks

## License

MIT

---