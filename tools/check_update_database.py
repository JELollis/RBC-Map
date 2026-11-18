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
MAIN = ROOT / "main_1.0.0.py"
BUILDING_TABLES = ("banks", "taverns", "transits", "userbuildings", "placesofinterest")
BUILDING_KINDS = {
    "bank": "banks",
    "tavern": "taverns",
    "transit": "transits",
    "userbuilding": "userbuildings",
    "placeofinterest": "placesofinterest",
}


def load_update_method():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    methods = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "update_database_with_json"
    ]
    assert len(methods) == 1, "expected one update_database_with_json method"
    namespace = {
        "sqlite3": sqlite3,
        "datetime": datetime,
        "timezone": timezone,
        "logging": logging,
        "DB_PATH": None,
        "BUILDING_CLASS_MAP": BUILDING_KINDS,
    }
    exec(compile(ast.Module(body=[methods[0]], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["update_database_with_json"], namespace


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
        table = BUILDING_KINDS[kind]
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
    missing_buildings_preserves_local_data,
    empty_buildings_preserves_local_data,
    valid_buildings_replace_snapshot,
):
    run_case(case.__name__, case)

print("all update-database checks passed")
