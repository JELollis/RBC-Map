"""Dependency-light regression checks for the credential-store adapter."""

from __future__ import annotations

import ast
import gc
import logging
import shutil
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
        "CREDENTIAL_NAMESPACE_SETTING",
        "CREDENTIAL_NAMESPACE",
        "SECRETS_MIGRATED",
        "ensure_credential_namespace",
        "_credential_namespace",
        "_migrate_legacy_secret",
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
        "delete_secret": delete_secret,
        "get_secret": get_secret,
        "set_secret": set_secret,
        "logging": logging,
        "os": __import__("os"),
        "Path": Path,
        "DB_PATH": ":memory:",
        "uuid": __import__("uuid"),
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
        "CHARACTER_SECRET_NAMESPACE": "character-password",
        "store_cookie_secret": lambda cookie_id, value: set_secret(
            "cookie-value", namespace["cookie_secret_id"](cookie_id), value
        ),
        "Qt": type("Qt", (), {"DateFormat": type("DateFormat", (), {"ISODate": object()})}),
    }
    helpers = load_migration_helpers()
    helpers["CREDENTIAL_NAMESPACE"] = "test-cookie-namespace"
    namespace.update({"_credential_namespace": helpers["_credential_namespace"]})
    namespace["CREDENTIAL_NAMESPACE"] = helpers["CREDENTIAL_NAMESPACE"]
    namespace["cookie_secret_id"] = helpers["cookie_secret_id"]
    exec(compile(ast.Module(body=[method], type_ignores=[]), "main_1.0.1.py", "exec"), namespace)
    return namespace["on_cookie_added"], namespace


def check_cookie_callback() -> None:
    callback, namespace = load_cookie_callback()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
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
        assert get_secret("cookie-value", namespace["cookie_secret_id"](rows[0][0])) == "Alice#pwA"
        connection.close()
    finally:
        if connection is not None:
            connection.close()
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
        CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB);
        CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT);
        CREATE TABLE cookies (id INTEGER PRIMARY KEY, name TEXT, value TEXT,
                              domain TEXT, path TEXT, expiration TEXT,
                              secure INTEGER, httponly INTEGER);
        INSERT INTO characters VALUES (1, 'Alice', 'pwA');
        INSERT INTO cookies VALUES (10, 'ip', 'Alice#pwA', 'quiz.ravenblack.net', '/', NULL, 0, 0);
        INSERT INTO cookies VALUES (11, 'ip', 'Bob#pwB', 'quiz.ravenblack.net', '/', NULL, 0, 0);
        """
    )
    namespace["CREDENTIAL_NAMESPACE"] = namespace["ensure_credential_namespace"](connection)

    FakeKeyring.available = True
    FakeKeyring.values.clear()
    assert load_character_secret(connection, 1, "pwA") == "pwA"
    assert connection.execute("SELECT password FROM characters WHERE id = 1").fetchone()[0] is None

    rows = connection.execute("SELECT id, name, value, domain, path FROM cookies ORDER BY id").fetchall()
    for cookie_id, name, value, domain, path in rows:
        assert load_cookie_secret(connection, cookie_id, name, domain, path, value) == value
    assert get_secret("cookie-value", namespace["cookie_secret_id"](10)) == "Alice#pwA"
    assert get_secret("cookie-value", namespace["cookie_secret_id"](11)) == "Bob#pwB"
    assert connection.execute("SELECT value FROM cookies ORDER BY id").fetchall() == [(None,), (None,)]
    vacuum_migrated_secrets(connection)
    assert namespace["SECRETS_MIGRATED"] is False

    connection.execute("INSERT INTO characters VALUES (2, 'Bob', 'pwB')")
    FakeKeyring.available = False
    assert load_character_secret(connection, 2, "pwB") is None
    assert connection.execute("SELECT password FROM characters WHERE id = 2").fetchone()[0] == "pwB"
    connection.close()


def check_database_secret_namespaces() -> None:
    namespace = load_migration_helpers()
    ensure_namespace = namespace["ensure_credential_namespace"]
    character_id = namespace["character_secret_id"]
    cookie_id = namespace["cookie_secret_id"]
    first = sqlite3.connect(":memory:")
    first.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
    first_namespace = ensure_namespace(first)
    first.commit()
    second = sqlite3.connect(":memory:")
    second.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
    second_namespace = ensure_namespace(second)
    assert first_namespace != second_namespace
    assert character_id(1, first_namespace) != character_id(1, second_namespace)
    assert cookie_id(1, first_namespace) != cookie_id(1, second_namespace)

    with tempfile.TemporaryDirectory() as temp_dir:
        original = Path(temp_dir) / "original.db"
        copied = Path(temp_dir) / "copied.db"
        connection = sqlite3.connect(original)
        connection.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
        original_namespace = ensure_namespace(connection)
        connection.commit()
        connection.close()
        shutil.copy2(original, copied)
        copied_connection = sqlite3.connect(copied)
        assert ensure_namespace(copied_connection) == original_namespace
        copied_connection.close()

    namespace["CREDENTIAL_NAMESPACE"] = "legacy-test"
    legacy_connection = sqlite3.connect(":memory:")
    legacy_connection.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
    set_secret("character-password", "7", "legacy-password")
    assert namespace["load_character_secret"](legacy_connection, 7, None) == "legacy-password"
    assert get_secret("character-password", character_id(7)) == "legacy-password"
    assert get_secret("character-password", "7") is None
    first.close()
    second.close()
    legacy_connection.close()


class FakeTextField:
    def __init__(self, value: str):
        self.value = value

    def text(self) -> str:
        return self.value


class FakeCharacterDialog:
    def __init__(self, name: str, password: str):
        self.name_edit = FakeTextField(name)
        self.password_edit = FakeTextField(password)

    def exec(self) -> bool:
        return True


class FakeMessageBox:
    @staticmethod
    def critical(*_args) -> None:
        return None

    @staticmethod
    def warning(*_args) -> None:
        return None


def load_character_mutation_methods() -> dict[str, object]:
    tree = ast.parse((Path(__file__).resolve().parents[1] / "main_1.0.1.py").read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    wanted = {"firstrun_character_creation", "add_new_character", "modify_character"}
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    namespace = {
        "sqlite3": sqlite3,
        "DB_PATH": ":memory:",
        "logging": logging,
        "CredentialStoreError": CredentialStoreError,
        "CHARACTER_SECRET_NAMESPACE": "character-password",
        "QMessageBox": FakeMessageBox,
        "sys": sys,
        "get_secret": get_secret,
        "set_secret": set_secret,
        "delete_secret": delete_secret,
        "store_character_secret": lambda _character_id, _password: (_ for _ in ()).throw(
            CredentialStoreError("simulated unavailable keyring")
        ),
        "CharacterDialog": lambda *_args: namespace["dialog"],
        "QTimer": type("QTimer", (), {"singleShot": staticmethod(lambda *_args: None)}),
        "QListWidgetItem": lambda *_args: object(),
        "QUrl": lambda value: value,
    }
    helpers = load_migration_helpers()
    helpers["CREDENTIAL_NAMESPACE"] = "character-test"
    namespace.update({
        "CREDENTIAL_NAMESPACE": helpers["CREDENTIAL_NAMESPACE"],
        "_credential_namespace": helpers["_credential_namespace"],
        "character_secret_id": helpers["character_secret_id"],
    })
    exec(compile(ast.Module(body=methods, type_ignores=[]), "main_1.0.1.py", "exec"), namespace)
    return namespace


def check_failed_character_creates_roll_back() -> None:
    namespace = load_character_mutation_methods()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.executescript(
            """
            CREATE TABLE characters (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT);
            CREATE TABLE coins (character_id INTEGER, pocket INTEGER, bank INTEGER);
            """
        )
        connection.commit()
        connection.close()
        namespace["DB_PATH"] = str(db_path)
        namespace["dialog"] = FakeCharacterDialog("Alice", "pwA")
        fake_self = type("FakeWindow", (), {})()
        fake_self.characters = []
        fake_self.character_list = type("FakeList", (), {"addItem": lambda *_args: None})()
        namespace["firstrun_character_creation"](fake_self)
        namespace["dialog"] = FakeCharacterDialog("Bob", "pwB")
        namespace["add_new_character"](fake_self)

        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT COUNT(*) FROM characters").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM coins").fetchone()[0] == 0
        connection.close()
        connection = None
    finally:
        if connection is not None:
            connection.close()
        gc.collect()
        db_path.unlink(missing_ok=True)


def check_modify_character_atomicity() -> None:
    namespace = load_character_mutation_methods()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.execute("CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
        connection.execute("INSERT INTO characters VALUES (1, 'Alice', NULL)")
        connection.commit()
        connection.close()
        connection = None
        namespace["DB_PATH"] = str(db_path)
        namespace["CREDENTIAL_NAMESPACE"] = "modify-test"
        set_secret("character-password", namespace["character_secret_id"](1), "old-password")

        character = {"id": 1, "name": "Alice", "password": "old-password"}
        item = type("FakeItem", (), {"text": lambda _self: "Alice", "setText": lambda *_args: None})()
        character_list = type("FakeList", (), {"currentItem": lambda _self: item})()
        fake_self = type("FakeWindow", (), {})()
        fake_self.characters = [character]
        fake_self.character_list = character_list

        holder = sqlite3.connect(db_path)
        holder.execute("BEGIN IMMEDIATE")
        namespace["dialog"] = FakeCharacterDialog("Alice-renamed", "new-password")
        namespace["modify_character"](fake_self)
        assert get_secret("character-password", namespace["character_secret_id"](1)) == "old-password"
        holder.rollback()
        holder.close()

        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TRIGGER reject_character_update BEFORE UPDATE ON characters "
            "BEGIN SELECT RAISE(ABORT, 'simulated update failure'); END"
        )
        connection.commit()
        connection.close()
        namespace["dialog"] = FakeCharacterDialog("Alice-renamed", "new-password")
        namespace["modify_character"](fake_self)
        assert get_secret("character-password", namespace["character_secret_id"](1)) == "old-password"
        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT name FROM characters WHERE id = 1").fetchone()[0] == "Alice"
        connection.close()
        connection = None
    finally:
        if connection is not None:
            connection.close()
        gc.collect()
        db_path.unlink(missing_ok=True)


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
        check_database_secret_namespaces()
        check_failed_character_creates_roll_back()
        check_modify_character_atomicity()
    finally:
        FakeKeyring.available = True
        credential_store.keyring = original_keyring
    print("credential-store checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
