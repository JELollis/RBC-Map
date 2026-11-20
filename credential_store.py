"""OS-backed storage for RBC Map credentials and session secrets."""

from __future__ import annotations

import hashlib
import sys
from concurrent.futures import Future, TimeoutError
from threading import Lock, Thread

import keyring


SERVICE_NAME = "RBC Community Map"
KEYRING_TIMEOUT = 3
_linux_keyring_lock = Lock()
_linux_keyring_disabled = False


class CredentialStoreError(RuntimeError):
    """Raised when the configured operating-system keyring cannot be used."""


def _username(namespace: str, identifier: str) -> str:
    """Return a stable, non-sensitive keyring account name."""
    digest = hashlib.sha256(f"{namespace}\0{identifier}".encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


def _require_unlocked_secret_service() -> None:
    """Check the selected Secret Service collection without creating or unlocking it."""
    backend = keyring.get_keyring()
    if type(backend).__module__ != "keyring.backends.SecretService":
        return

    import secretstorage

    with secretstorage.dbus_init() as bus:
        collection = secretstorage.Collection(
            bus,
            getattr(backend, "preferred_collection", "/org/freedesktop/secrets/aliases/default"),
        )
        if collection.is_locked():
            raise CredentialStoreError("Unlock the Secret Service collection before using saved credentials.")


def _run_keyring(operation):
    """Bound Linux keyring calls and quarantine a backend that hangs."""
    global _linux_keyring_disabled
    if not sys.platform.startswith("linux"):
        return operation()

    with _linux_keyring_lock:
        if _linux_keyring_disabled:
            raise CredentialStoreError("OS credential store timed out earlier. Restart the app to retry.")
        result = Future()

        def run():
            try:
                _require_unlocked_secret_service()
                result.set_result(operation())
            except Exception as exc:
                result.set_exception(exc)

        Thread(target=run, daemon=True).start()
        try:
            return result.result(timeout=KEYRING_TIMEOUT)
        except TimeoutError as exc:
            _linux_keyring_disabled = True
            raise CredentialStoreError(
                "OS credential store did not respond. Check Secret Service and restart the app."
            ) from exc


def set_secret(namespace: str, identifier: str, value: str) -> None:
    """Store a secret and verify that the keyring can read it back."""
    if not isinstance(value, str) or not value:
        raise CredentialStoreError("refusing to store an empty or non-text secret")
    account = _username(namespace, identifier)
    def write_and_verify():
        keyring.set_password(SERVICE_NAME, account, value)
        if keyring.get_password(SERVICE_NAME, account) != value:
            raise CredentialStoreError("keyring write verification failed")

    try:
        _run_keyring(write_and_verify)
    except CredentialStoreError:
        raise
    except Exception as exc:  # keyring backends expose different exception types
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc


def get_secret(namespace: str, identifier: str) -> str | None:
    """Load a secret, or return ``None`` when no entry exists."""
    try:
        return _run_keyring(lambda: keyring.get_password(SERVICE_NAME, _username(namespace, identifier)))
    except Exception as exc:
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc


def delete_secret(namespace: str, identifier: str) -> None:
    """Delete a secret when the backend supports deletion of an existing entry."""
    account = _username(namespace, identifier)
    def delete_if_present():
        if keyring.get_password(SERVICE_NAME, account) is not None:
            keyring.delete_password(SERVICE_NAME, account)

    try:
        _run_keyring(delete_if_present)
    except Exception as exc:
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc
