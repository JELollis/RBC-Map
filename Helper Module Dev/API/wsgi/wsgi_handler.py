import os
import json
import secrets
from urllib.parse import parse_qs
from datetime import datetime, timedelta, UTC

# Base paths
WSGI_DIR = os.path.dirname(__file__)
API_DIR = os.path.abspath(os.path.join(WSGI_DIR, ".."))  # /api/

# File paths
TOKEN_FILE = os.path.join(API_DIR, "tokens.json")
TRIGGER_FILE = os.path.join(API_DIR, "trigger_update")

def load_tokens():
    """Load token data including tokens list and last_trigger_time."""
    if not os.path.exists(TOKEN_FILE):
        return {"tokens": [], "last_trigger_time": None}
    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Backward compatibility: convert old format
                return {"tokens": data, "last_trigger_time": None}
            return data
    except json.JSONDecodeError:
        return {"tokens": [], "last_trigger_time": None}


def save_tokens(data):
    """Save token data with tokens list and last_trigger_time."""
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def was_recently_triggered(data):
    """Check if the last trigger was within the cooldown period."""
    try:
        last_str = data.get("last_trigger_time")
        if not last_str:
            return False
        last = datetime.fromisoformat(last_str)
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        return (datetime.now(UTC) - last) < timedelta(minutes=5)
    except Exception:
        return False

def application(environ, start_response):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "")
    query = parse_qs(environ.get("QUERY_STRING", ""))

    if path.endswith("/request-token.py") and method == "GET":
        token = secrets.token_urlsafe(32)
        data = load_tokens()
        data["tokens"].append(token)
        save_tokens(data)

        start_response("200 OK", [("Content-Type", "text/plain")])
        return [token.encode("utf-8")]

    elif path.endswith("/trigger-update.py") and method == "GET":
        token = query.get("token", [""])[0]
        data = load_tokens()
        tokens = data.get("tokens", [])

        if token in tokens:
            if was_recently_triggered(data):
                start_response("200 OK", [("Content-Type", "text/plain")])
                return ["✅ Already triggered recently.\n".encode("utf-8")]

            tokens.remove(token)
            data["tokens"] = tokens
            data["last_trigger_time"] = datetime.now(UTC).isoformat()
            save_tokens(data)

            try:
                with open(TRIGGER_FILE, "w") as f:
                    f.write(datetime.now(UTC).isoformat())
            except Exception:
                pass

            start_response("200 OK", [("Content-Type", "text/plain")])
            return ["✅ Update triggered.\n".encode("utf-8")]
        else:
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return ["❌ Invalid or expired token.\n".encode("utf-8")]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return ["❓ Not found.\n".encode("utf-8")]
