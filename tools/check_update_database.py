"""Regression checks for update-database validation and error propagation."""

import ast
import gc
import logging
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main_1.0.1.py"
BUILDING_TABLES = ("banks", "taverns", "transits", "userbuildings", "placesofinterest")


class FakeRequests:
    class RequestException(Exception):
        pass


class FakeRequestExceptions:
    RequestException = FakeRequests.RequestException


FakeRequests.exceptions = FakeRequestExceptions


class FakeMessageBox:
    critical_calls = []

    @classmethod
    def critical(cls, *args):
        cls.critical_calls.append(args)


def load_update_method():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    methods = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "update_database_with_json"
    ]
    assert len(methods) == 1, "expected one update_database_with_json method"
    map_assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "BUILDING_CLASS_MAP"
            for target in node.targets
        )
    ]
    assert len(map_assignments) == 1, "expected one BUILDING_CLASS_MAP assignment"
    building_map = ast.literal_eval(map_assignments[0].value)
    namespace = {
        "sqlite3": sqlite3,
        "datetime": datetime,
        "timezone": timezone,
        "logging": logging,
        "requests": FakeRequests,
        "QMessageBox": FakeMessageBox,
        "DB_PATH": None,
        "BUILDING_CLASS_MAP": building_map,
    }
    exec(compile(ast.Module(body=[methods[0]], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["update_database_with_json"], namespace


def load_function(function_name: str):
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    methods = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    assert len(methods) == 1, f"expected one {function_name} method"
    node = methods[0]
    node.decorator_list = []
    namespace = {
        "logging": logging,
        "requests": FakeRequests,
        "QMessageBox": FakeMessageBox,
        "fetch_location_update": lambda **kwargs: {},
        "DB_PATH": None,
        "BUILDING_CLASS_MAP": {},
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace[function_name], namespace


def load_startup_run():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "StartupUpdateWorker"
    ]
    assert len(classes) == 1, "expected one StartupUpdateWorker class"
    methods = [node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == "run"]
    assert len(methods) == 1, "expected one StartupUpdateWorker.run method"
    node = methods[0]
    node.decorator_list = []
    namespace = {
        "logging": logging,
        "requests": FakeRequests,
        "fetch_location_update": lambda **kwargs: {"guilds": {}, "shops": {}},
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["run"], namespace


def make_database(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE guilds (Name TEXT PRIMARY KEY, "Column" TEXT, "Row" TEXT,
                                 next_update TEXT, last_scraped TEXT);
            CREATE TABLE shops (Name TEXT PRIMARY KEY, "Column" TEXT, "Row" TEXT,
                                next_update TEXT, last_scraped TEXT);
            CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value TEXT);
            CREATE TABLE banks (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE taverns (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE transits (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE userbuildings (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE placesofinterest (Name TEXT, "Column" TEXT, "Row" TEXT);
            """
        )
        for table in BUILDING_TABLES:
            conn.execute(
                f'INSERT INTO {table} (Name, "Column", "Row") VALUES (?, ?, ?)',
                (f"Existing {table}", "A", "1st"),
            )
        conn.commit()
    finally:
        conn.close()


class FakeMap:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def update(self, data):
        method, namespace = load_update_method()
        namespace["DB_PATH"] = self.db_path
        method(self, data)

    def _upsert_building(self, cursor, kind, name, column, row):
        table = {
            "bank": "banks",
            "pub": "taverns",
            "transit": "transits",
            "arena": "placesofinterest",
            "grave": "placesofinterest",
            "lair": "userbuildings",
            "alchemy": "placesofinterest",
        }[kind]
        cursor.execute(
            f'INSERT INTO {table} (Name, "Column", "Row") VALUES (?, ?, ?)',
            (name, column, row),
        )


def count_rows(db_path: Path, table: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def malformed_payload_is_reported(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    try:
        FakeMap(db).update({"guilds": []})
    except AttributeError:
        return
    raise AssertionError("malformed guild payload was swallowed")


def manual_update_reports_database_failure(root: Path) -> None:
    method, namespace = load_function("update_data")
    FakeMessageBox.critical_calls.clear()
    namespace["fetch_location_update"] = lambda **kwargs: {"guilds": [], "shops": {}}

    class FailingApp:
        def update_database_with_json(self, data):
            raise sqlite3.DatabaseError("simulated database failure")

        def fetch_and_merge_community_buildings(self, **kwargs):
            raise AssertionError("community merge should not run after database failure")

        def refresh_map_data_from_db(self):
            raise AssertionError("map refresh should not run after database failure")

        def get_locations_last_updated(self):
            return None

    assert method(FailingApp()) is False
    assert FakeMessageBox.critical_calls, "manual failure should show an error"


def dialog_stops_before_success_path() -> None:
    source = MAIN.read_text(encoding="utf-8")
    guard = "if not self.parent.update_data():"
    assert guard in source
    guard_start = source.index(guard)
    step_two = source.index("# Step 2: Reload from DB", guard_start)
    assert "return" in source[guard_start:step_two]


def startup_worker_reports_database_failure(root: Path) -> None:
    method, namespace = load_startup_run()
    events = []

    class Signal:
        def emit(self, *args):
            events.append(args)

    class FailingApp:
        def get_locations_last_updated(self):
            return None

        def update_database_with_json(self, data):
            raise sqlite3.DatabaseError("simulated database failure")

        def fetch_and_merge_community_buildings(self, **kwargs):
            raise AssertionError("community merge should not run after database failure")

    worker = type("Worker", (), {})()
    worker.started = Signal()
    worker.finished = Signal()
    worker.app = FailingApp()
    worker.REQUEST_TIMEOUT = 10
    namespace["fetch_location_update"] = lambda **kwargs: {"guilds": {}, "shops": {}}
    method(worker)
    assert events[-1][0] is False
    assert "Startup update failed" in events[-1][1]


def missing_buildings_preserves_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update({"guilds": {}, "shops": {}})
    assert count_rows(db, "banks") == 1


def empty_buildings_preserves_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update({"buildings": {}})
    assert count_rows(db, "taverns") == 1


def shop_only_buildings_preserve_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update(
        {"buildings": {"shop": {"kind": "shop", "name": "Shop", "column": "B", "row": "2nd"}}}
    )
    assert count_rows(db, "transits") == 1


def mixed_valid_and_malformed_preserves_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update(
        {
            "buildings": {
                "valid": {"kind": "bank", "name": "New Bank", "column": "B", "row": "2nd"},
                "malformed": {"kind": "pub", "name": "Missing Row", "column": "C"},
            }
        }
    )
    assert count_rows(db, "banks") == 1
    assert count_rows(db, "taverns") == 1


def valid_buildings_replace_snapshot(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update(
        {"buildings": {"new": {"kind": "bank", "name": "New Bank", "column": "B", "row": "2nd"}}}
    )
    assert count_rows(db, "banks") == 1
    conn = sqlite3.connect(db)
    try:
        assert conn.execute("SELECT Name FROM banks").fetchone()[0] == "New Bank"
    finally:
        conn.close()


def run_case(name, case) -> None:
    temp = tempfile.mkdtemp()
    try:
        case(Path(temp))
    finally:
        gc.collect()
        shutil.rmtree(temp, ignore_errors=True)
    print(f"ok   {name}")


for case in (
    malformed_payload_is_reported,
    manual_update_reports_database_failure,
    startup_worker_reports_database_failure,
    missing_buildings_preserves_local_data,
    empty_buildings_preserves_local_data,
    shop_only_buildings_preserve_local_data,
    mixed_valid_and_malformed_preserves_local_data,
    valid_buildings_replace_snapshot,
):
    run_case(case.__name__, case)

dialog_stops_before_success_path()
print("ok   dialog_stops_before_success_path")

print("all update-database checks passed")
