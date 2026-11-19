"""OS-backed storage for RBC Map credentials and session secrets."""

from __future__ import annotations

import hashlib

import keyring


SERVICE_NAME = "RBC Community Map"


class CredentialStoreError(RuntimeError):
    """Raised when the configured operating-system keyring cannot be used."""


def _username(namespace: str, identifier: str) -> str:
    """Return a stable, non-sensitive keyring account name."""
    digest = hashlib.sha256(f"{namespace}\0{identifier}".encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


def set_secret(namespace: str, identifier: str, value: str) -> None:
    """Store a secret and verify that the keyring can read it back."""
    if not isinstance(value, str) or not value:
        raise CredentialStoreError("refusing to store an empty or non-text secret")
    account = _username(namespace, identifier)
    try:
        keyring.set_password(SERVICE_NAME, account, value)
        if keyring.get_password(SERVICE_NAME, account) != value:
            raise CredentialStoreError("keyring write verification failed")
    except CredentialStoreError:
        raise
    except Exception as exc:  # keyring backends expose different exception types
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc


def get_secret(namespace: str, identifier: str) -> str | None:
    """Load a secret, or return ``None`` when no entry exists."""
    try:
        return keyring.get_password(SERVICE_NAME, _username(namespace, identifier))
    except Exception as exc:
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc


def delete_secret(namespace: str, identifier: str) -> None:
    """Delete a secret when the backend supports deletion of an existing entry."""
    account = _username(namespace, identifier)
    try:
        if keyring.get_password(SERVICE_NAME, account) is not None:
            keyring.delete_password(SERVICE_NAME, account)
    except Exception as exc:
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc
