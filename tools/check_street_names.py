"""Regression checks for canonical street ordering and city-limit aliases."""

import ast
import logging
import re
import sqlite3
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main_1.0.5.py"


def load_helpers():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    names = {
        "CITY_LIMIT_ALIASES",
        "visible_street_names",
        "canonical_street_label",
        "canonical_intersection_label",
        "canonical_street_names_by_coordinate",
    }
    nodes = [
        node
        for node in tree.body
        if (isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names
            for target in node.targets
        ))
        or (isinstance(node, ast.FunctionDef) and node.name in names)
    ]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace


def canonical_order_hides_only_full_aliases():
    namespace = load_helpers()
    rows = {
        "NCL": 0,
        "Northern City Limits": 0,
        "1st": 2,
        "2nd": 4,
        "10th": 20,
    }
    columns = {
        "WCL": 0,
        "Western City Limits": 0,
        "Aardvark": 2,
        "Alder": 4,
    }

    assert namespace["visible_street_names"](rows) == ["NCL", "1st", "2nd", "10th"]
    assert namespace["visible_street_names"](columns) == ["WCL", "Aardvark", "Alder"]

    row_by_coordinate = namespace["canonical_street_names_by_coordinate"](rows)
    column_by_coordinate = namespace["canonical_street_names_by_coordinate"](columns)
    assert row_by_coordinate[0] == "NCL"
    assert column_by_coordinate[0] == "WCL"
    assert row_by_coordinate[20] == "10th"
    assert namespace["canonical_intersection_label"]("Western City Limits", "1st") == "WCL & 1st"


def intersection_labels_use_canonical_boundary_names():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "get_intersection_name"
    )
    helpers = load_helpers()
    namespace = {
        "canonical_street_names_by_coordinate": helpers["canonical_street_names_by_coordinate"],
    }
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(MAIN), "exec"), namespace)
    app = SimpleNamespace(
        columns={"WCL": 0, "Western City Limits": 0, "Aardvark": 2},
        rows={"NCL": 0, "Northern City Limits": 0, "1st": 2},
    )
    assert namespace["get_intersection_name"](app, (0, 0)) == "WCL & NCL"
    assert namespace["get_intersection_name"](app, (2, 2)) == "Aardvark & 1st"


def legacy_border_rows_are_normalized_in_place():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_upsert_building"
    )
    helpers = load_helpers()
    namespace = {
        "BUILDING_CLASS_MAP": {"bank": {"table": "banks", "name_col": "Name"}},
        "canonical_street_label": helpers["canonical_street_label"],
        "logging": logging,
        "re": re,
    }
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(MAIN), "exec"), namespace)

    conn = sqlite3.connect(":memory:")
    try:
        conn.execute(
            'CREATE TABLE banks (ID INTEGER PRIMARY KEY, "Column" TEXT, Row TEXT, Name TEXT)'
        )
        conn.execute(
            'INSERT INTO banks (ID, "Column", Row, Name) VALUES (1, ?, ?, ?)',
            ("Western City Limits", "Northern City Limits", "OmniBank"),
        )
        action = namespace["_upsert_building"](
            SimpleNamespace(), conn.cursor(), "bank", "OmniBank", "WCL", "NCL"
        )
        assert action == "updated"
        assert conn.execute('SELECT "Column", Row FROM banks').fetchone() == ("WCL", "NCL")
        assert conn.execute("SELECT COUNT(*) FROM banks").fetchone() == (1,)
    finally:
        conn.close()


def recent_history_matches_legacy_border_rows():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_get_building_name"
    )
    helpers = load_helpers()
    namespace = {
        "canonical_street_label": helpers["canonical_street_label"],
        "sqlite3": sqlite3,
    }
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(MAIN), "exec"), namespace)
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute('CREATE TABLE banks (Name TEXT, "Column" TEXT, Row TEXT)')
        conn.execute(
            'INSERT INTO banks (Name, "Column", Row) VALUES (?, ?, ?)',
            ("OmniBank", "Western City Limits", "Northern City Limits"),
        )
        app = SimpleNamespace()
        assert namespace["_get_building_name"](app, conn.cursor(), "WCL", "NCL") == "OmniBank"
    finally:
        conn.close()


def ordered_database_queries_are_explicit():
    source = MAIN.read_text(encoding="utf-8")
    assert source.count("SELECT Name, Coordinate FROM columns ORDER BY ID") >= 2
    assert source.count("SELECT Name, Coordinate FROM rows ORDER BY ID") >= 2


if __name__ == "__main__":
    canonical_order_hides_only_full_aliases()
    intersection_labels_use_canonical_boundary_names()
    legacy_border_rows_are_normalized_in_place()
    recent_history_matches_legacy_border_rows()
    ordered_database_queries_are_explicit()
    print("all street-name checks passed")
