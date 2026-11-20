"""Regression checks for startup state and responsive navigation wiring."""

from __future__ import annotations

import ast
import contextlib
import io
import logging
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main_1.0.2.py"


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(matches) == 1, f"expected one {name} function"
    return matches[0]


def check_pending_destination_initialization(tree: ast.Module) -> None:
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
    assert any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Attribute)
            and target.attr == "pending_character_id_for_map"
            for target in node.targets
        )
        for node in ast.walk(init)
    ), "pending_character_id_for_map must be initialized in __init__"


def load_logging_helper(tree: ast.Module):
    helper = _function(tree, "get_logging_level_from_db")
    namespace = {
        "sqlite3": sqlite3,
        "sys": __import__("sys"),
        "logging": logging,
        "DB_PATH": ":memory:",
    }
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["get_logging_level_from_db"]


def check_missing_settings_table_is_quiet(tree: ast.Module) -> None:
    helper = load_logging_helper(tree)
    # An in-memory database starts without the settings table and avoids
    # platform-specific cleanup/locking behavior in the regression check.
    helper.__globals__["DB_PATH"] = ":memory:"
    output = io.StringIO()
    with contextlib.redirect_stderr(output):
        level = helper(17)
    assert level == 17
    assert output.getvalue() == "", "missing settings table should not print a startup error"


def check_other_operational_errors_are_reported(tree: ast.Module) -> None:
    helper = load_logging_helper(tree)

    class LockedConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def cursor(self):
            return self

        def execute(self, *_args):
            raise sqlite3.OperationalError("database is locked")

        def fetchone(self):
            return None

    class FakeSqlite:
        OperationalError = sqlite3.OperationalError

        @staticmethod
        def connect(_path):
            return LockedConnection()

    helper.__globals__["sqlite3"] = FakeSqlite
    output = io.StringIO()
    helper.__globals__["sys"].stderr = output
    assert helper(23) == 23
    assert "database is locked" in output.getvalue()


def check_splitter_resizes_navigation(tree: ast.Module) -> None:
    setup = _function(tree, "setup_ui_components")
    source = ast.unparse(setup)
    assert "splitter.splitterMoved.connect" in source
    assert "_schedule_navigation_resize" in source
    assert "_navigation_resize_timer" in source


def main() -> int:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    check_pending_destination_initialization(tree)
    check_missing_settings_table_is_quiet(tree)
    check_other_operational_errors_are_reported(tree)
    check_splitter_resizes_navigation(tree)
    print("startup/layout checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
