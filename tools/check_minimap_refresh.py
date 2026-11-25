"""Regression checks for in-session learned-location minimap refreshes."""

import ast
import logging
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from types import MethodType, SimpleNamespace

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main_1.0.5.py"


def _load_methods(names):
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    wanted = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in wanted} == set(names)
    building_map = next(
        ast.literal_eval(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "BUILDING_CLASS_MAP" for target in node.targets)
    )
    namespace = {
        "BeautifulSoup": BeautifulSoup,
        "BUILDING_CLASS_MAP": building_map,
        "datetime": datetime,
        "logging": logging,
        "re": re,
        "sqlite3": sqlite3,
        "timezone": timezone,
    }
    exec(compile(ast.Module(body=wanted, type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace


def _load_function(name):
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == name)
    namespace = {
        "logging": logging,
        "sqlite3": sqlite3,
        "SimpleNamespace": SimpleNamespace,
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace


def _make_db(conn) -> None:
    conn.execute('CREATE TABLE shops (Name TEXT PRIMARY KEY, "Column" TEXT, Row TEXT)')
    conn.commit()


def _learner_app(conn, refresh_error=None):
    namespace = _load_methods({
        "_building_display_name",
        "_building_game_coord",
        "_is_curated_poi",
        "_upsert_building",
        "learn_buildings_from_html",
        "normalize_building_name",
    })
    namespace["sqlite3"] = SimpleNamespace(Cursor=sqlite3.Cursor, connect=lambda _path: conn)
    namespace["DB_PATH"] = ":memory:"
    reports = []
    refreshes = []
    app = SimpleNamespace(
        _BUILDING_NAME_OVERRIDES={},
        _CURATED_POI_NAME_MARKERS=("kindred hospital", "cloister of secrets", "requiem of hades"),
        _seen_buildings=set(),
        character_x=0,
        character_y=0,
        columns={"Vexation": 1},
        rows={"16th": 2},
    )
    for name in (
        "_building_display_name",
        "_building_game_coord",
        "_is_curated_poi",
        "_upsert_building",
        "learn_buildings_from_html",
        "normalize_building_name",
    ):
        setattr(app, name, MethodType(namespace[name], app))
    app._flush_reports = reports.extend

    def refresh():
        refreshes.append(True)
        if refresh_error:
            raise refresh_error

    app.refresh_map_data_from_db = refresh
    return app, reports, refreshes


def _shop_html() -> str:
    return '<table><tr><td><input name="x" value="1"><input name="y" value="2"><span class="shop">Checkers Pawn Shop</span></td></tr></table>'


def learned_shop_refreshes_once_and_reports_once() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        _make_db(conn)
        app, reports, refreshes = _learner_app(conn)
        app.learn_buildings_from_html(_shop_html())
        assert len(reports) == 1
        assert len(refreshes) == 1
        assert conn.execute('SELECT "Column", Row FROM shops').fetchone() == ("Vexation", "16th")

        app.learn_buildings_from_html(_shop_html())
        assert len(reports) == 1, "repeat sightings must not be reported"
        assert len(refreshes) == 1, "repeat sightings must not redraw"
    finally:
        conn.close()


def refresh_failure_does_not_drop_report() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        _make_db(conn)
        app, reports, _refreshes = _learner_app(conn, RuntimeError("simulated refresh failure"))
        app.learn_buildings_from_html(_shop_html())
        assert len(reports) == 1, "map refresh failure must not suppress reporting"
    finally:
        conn.close()


def map_refresh_uses_map_only_load() -> None:
    map_namespace = _load_methods({"refresh_map_data_from_db"})
    load_namespace = _load_function("load_data")

    class FakeColor:
        def __init__(self, value):
            self.value = value

        def isValid(self):
            return True

    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(
            """
            CREATE TABLE columns (Name TEXT, Coordinate INTEGER);
            CREATE TABLE rows (Name TEXT, Coordinate INTEGER);
            CREATE TABLE banks ("Column" TEXT, Row TEXT);
            CREATE TABLE taverns (Name TEXT, "Column" TEXT, Row TEXT);
            CREATE TABLE transits (Name TEXT, "Column" TEXT, Row TEXT);
            CREATE TABLE userbuildings (Name TEXT, "Column" TEXT, Row TEXT);
            CREATE TABLE color_mappings (type TEXT, color TEXT);
            CREATE TABLE shops (Name TEXT, "Column" TEXT, Row TEXT);
            CREATE TABLE guilds (Name TEXT, "Column" TEXT, Row TEXT);
            CREATE TABLE placesofinterest (Name TEXT, "Column" TEXT, Row TEXT);
            CREATE TABLE settings (setting_name TEXT, setting_value TEXT);
            """
        )
        conn.executemany("INSERT INTO columns VALUES (?, ?)", [("Vexation", 1)])
        conn.executemany("INSERT INTO rows VALUES (?, ?)", [("16th", 2)])
        conn.executemany("INSERT INTO shops VALUES (?, ?, ?)", [("Checkers Pawn Shop", "Vexation", "16th")])
        conn.executemany("INSERT INTO settings VALUES (?, ?)", [("keybind_config", "1"), ("css_profile", "Default")])
        conn.commit()

        class SQLiteProxy:
            Cursor = sqlite3.Cursor

            @staticmethod
            def connect(_path):
                return conn

        load_namespace.update(
            DB_PATH=":memory:",
            sqlite3=SQLiteProxy,
            PySide6=SimpleNamespace(QtGui=SimpleNamespace(QColor=FakeColor)),
            load_character_secret=lambda *_args: (_ for _ in ()).throw(AssertionError("secret loader called")),
        )
        load_data = load_namespace["load_data"]
        map_namespace["load_data"] = load_data
        map_namespace["sqlite3"] = sqlite3
        method = map_namespace["refresh_map_data_from_db"]
        method.__globals__.update(map_namespace)
        app = SimpleNamespace(
            character_x=1,
            character_y=1,
            apply_minimap_colors_from_css=lambda: None,
            update_minimap=lambda: None,
        )
        method(app)
        assert app.shops_coordinates == {"Checkers Pawn Shop": (2, 3)}
    finally:
        conn.close()


def main() -> None:
    learned_shop_refreshes_once_and_reports_once()
    refresh_failure_does_not_drop_report()
    map_refresh_uses_map_only_load()
    print("all minimap-refresh checks passed")


if __name__ == "__main__":
    main()
