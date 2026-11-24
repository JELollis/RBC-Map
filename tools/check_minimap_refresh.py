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
    namespace = _load_methods({"refresh_map_data_from_db"})
    calls = []

    def map_only_load(**kwargs):
        calls.append(kwargs)
        return ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 1, "Default", None, None)

    app = SimpleNamespace(
        character_x=1,
        character_y=1,
        apply_minimap_colors_from_css=lambda: None,
        update_minimap=lambda: None,
    )
    namespace["load_data"] = map_only_load
    method = namespace["refresh_map_data_from_db"]
    method.__globals__.update(namespace)
    method(app)
    assert calls == [{"load_session": False}], "map refresh must not load session secrets"


def main() -> None:
    learned_shop_refreshes_once_and_reports_once()
    refresh_failure_does_not_drop_report()
    map_refresh_uses_map_only_load()
    print("all minimap-refresh checks passed")


if __name__ == "__main__":
    main()
