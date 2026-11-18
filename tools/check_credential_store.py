"""Dependency-light regression checks for the credential-store adapter."""

from __future__ import annotations

import ast
import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import credential_store
from credential_store import CredentialStoreError, delete_secret, get_secret, set_secret


class FakeKeyring:
    values: dict[tuple[str, str], str] = {}
    available = True

    @classmethod
    def set_password(cls, service: str, account: str, value: str) -> None:
        if not cls.available:
            raise RuntimeError("simulated unavailable keyring")
        cls.values[(service, account)] = value

    @classmethod
    def get_password(cls, service: str, account: str) -> str | None:
        if not cls.available:
            raise RuntimeError("simulated unavailable keyring")
        return cls.values.get((service, account))

    @classmethod
    def delete_password(cls, service: str, account: str) -> None:
        if not cls.available:
            raise RuntimeError("simulated unavailable keyring")
        del cls.values[(service, account)]


def load_migration_helpers() -> dict[str, object]:
    tree = ast.parse((Path(__file__).resolve().parents[1] / "main_1.0.1.py").read_text(encoding="utf-8"))
    names = {
        "CHARACTER_SECRET_NAMESPACE",
        "COOKIE_SECRET_NAMESPACE",
        "character_secret_id",
        "cookie_secret_id",
        "load_character_secret",
        "load_cookie_secret",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    namespace = {
        "CredentialStoreError": CredentialStoreError,
        "get_secret": get_secret,
        "set_secret": set_secret,
        "logging": logging,
        "sqlite3": sqlite3,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "main_1.0.1.py", "exec"), namespace)
    return namespace


def check_migrations() -> None:
    namespace = load_migration_helpers()
    load_character_secret = namespace["load_character_secret"]
    load_cookie_secret = namespace["load_cookie_secret"]

    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT);
        CREATE TABLE cookies (id INTEGER PRIMARY KEY, name TEXT, value TEXT,
                              domain TEXT, path TEXT, expiration TEXT,
                              secure INTEGER, httponly INTEGER);
        INSERT INTO characters VALUES (1, 'Alice', 'pwA');
        INSERT INTO cookies VALUES (10, 'ip', 'Alice#pwA', 'quiz.ravenblack.net', '/', NULL, 0, 0);
        INSERT INTO cookies VALUES (11, 'ip', 'Bob#pwB', 'quiz.ravenblack.net', '/', NULL, 0, 0);
        """
    )

    FakeKeyring.available = True
    FakeKeyring.values.clear()
    assert load_character_secret(connection, 1, "pwA") == "pwA"
    assert connection.execute("SELECT password FROM characters WHERE id = 1").fetchone()[0] is None

    rows = connection.execute("SELECT id, name, value, domain, path FROM cookies ORDER BY id").fetchall()
    for cookie_id, name, value, domain, path in rows:
        assert load_cookie_secret(connection, cookie_id, name, domain, path, value) == value
    assert get_secret("cookie-value", "10") == "Alice#pwA"
    assert get_secret("cookie-value", "11") == "Bob#pwB"
    assert connection.execute("SELECT value FROM cookies ORDER BY id").fetchall() == [(None,), (None,)]

    connection.execute("INSERT INTO characters VALUES (2, 'Bob', 'pwB')")
    FakeKeyring.available = False
    assert load_character_secret(connection, 2, "pwB") is None
    assert connection.execute("SELECT password FROM characters WHERE id = 2").fetchone()[0] == "pwB"
    connection.close()


def main() -> int:
    original_keyring = credential_store.keyring
    credential_store.keyring = FakeKeyring
    try:
        set_secret("test", "account", "secret")
        assert get_secret("test", "account") == "secret"
        delete_secret("test", "account")
        assert get_secret("test", "account") is None
        try:
            set_secret("test", "account", "")
        except CredentialStoreError:
            pass
        else:
            raise AssertionError("empty secrets must be rejected")
        check_migrations()
    finally:
        FakeKeyring.available = True
        credential_store.keyring = original_keyring
    print("credential-store checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
