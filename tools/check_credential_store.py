"""Dependency-light regression checks for the credential-store adapter."""

from __future__ import annotations

import ast
import gc
import logging
import sqlite3
import sys
import tempfile
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


class FakeByteValue:
    def __init__(self, value: str):
        self.value = value

    def data(self) -> bytes:
        return self.value.encode()


class FakeDate:
    def toString(self, *_args) -> str:
        return ""


class FakeCookie:
    def __init__(self, value: str):
        self._value = value

    def name(self) -> FakeByteValue:
        return FakeByteValue("ip")

    def value(self) -> FakeByteValue:
        return FakeByteValue(self._value)

    def domain(self) -> str:
        return "quiz.ravenblack.net"

    def path(self) -> str:
        return "/"

    def isSessionCookie(self) -> bool:
        return True

    def expirationDate(self) -> FakeDate:
        return FakeDate()

    def isSecure(self) -> bool:
        return False

    def isHttpOnly(self) -> bool:
        return False


def load_migration_helpers() -> dict[str, object]:
    tree = ast.parse((Path(__file__).resolve().parents[1] / "main_1.0.1.py").read_text(encoding="utf-8"))
    names = {
        "CHARACTER_SECRET_NAMESPACE",
        "COOKIE_SECRET_NAMESPACE",
        "SECRETS_MIGRATED",
        "character_secret_id",
        "cookie_secret_id",
        "load_character_secret",
        "load_cookie_secret",
        "vacuum_migrated_secrets",
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


def load_cookie_callback() -> tuple[object, dict[str, object]]:
    tree = ast.parse((Path(__file__).resolve().parents[1] / "main_1.0.1.py").read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "on_cookie_added")
    namespace = {
        "sqlite3": sqlite3,
        "DB_PATH": ":memory:",
        "logging": logging,
        "CredentialStoreError": CredentialStoreError,
        "store_cookie_secret": lambda cookie_id, value: set_secret("cookie-value", str(cookie_id), value),
        "Qt": type("Qt", (), {"DateFormat": type("DateFormat", (), {"ISODate": object()})}),
    }
    exec(compile(ast.Module(body=[method], type_ignores=[]), "main_1.0.1.py", "exec"), namespace)
    return namespace["on_cookie_added"], namespace


def check_cookie_callback() -> None:
    callback, namespace = load_cookie_callback()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    try:
        connection = sqlite3.connect(db_path)
        connection.executescript(
            """
            CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, active_cookie INTEGER);
            CREATE TABLE cookies (id INTEGER PRIMARY KEY, name TEXT, value TEXT,
                                  domain TEXT, path TEXT, expiration TEXT,
                                  secure INTEGER, httponly INTEGER);
            INSERT INTO characters VALUES (1, 'Alice', NULL);
            INSERT INTO characters VALUES (2, 'Bob', NULL);
            """
        )
        connection.commit()
        connection.close()

        namespace["DB_PATH"] = str(db_path)
        FakeKeyring.values.clear()
        FakeKeyring.available = True
        callback(object(), FakeCookie("Alice#pwA"))
        callback(object(), FakeCookie("Bob#pwB"))

        connection = sqlite3.connect(db_path)
        rows = connection.execute("SELECT id, name FROM cookies ORDER BY id").fetchall()
        assert len(rows) == 2
        linked = connection.execute("SELECT active_cookie FROM characters ORDER BY id").fetchall()
        assert linked == [(rows[0][0],), (rows[1][0],)]
        connection.close()

        callback(object(), FakeCookie("Carol#pwC"))
        callback(object(), FakeCookie("Alice#"))
        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT COUNT(*) FROM cookies").fetchone()[0] == 2
        assert get_secret("cookie-value", str(rows[0][0])) == "Alice#pwA"
        connection.close()
    finally:
        gc.collect()
        db_path.unlink(missing_ok=True)


def check_migrations() -> None:
    namespace = load_migration_helpers()
    load_character_secret = namespace["load_character_secret"]
    load_cookie_secret = namespace["load_cookie_secret"]
    vacuum_migrated_secrets = namespace["vacuum_migrated_secrets"]

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
    vacuum_migrated_secrets(connection)
    assert namespace["SECRETS_MIGRATED"] is False

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
        check_cookie_callback()
    finally:
        FakeKeyring.available = True
        credential_store.keyring = original_keyring
    print("credential-store checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
