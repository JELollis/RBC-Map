"""Check that power selection fills values without repeating field captions."""

from __future__ import annotations

import ast
import sqlite3
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

MAIN = Path(__file__).resolve().parents[1] / "main_1.0.4.py"


def main() -> None:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    dialog = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "PowersDialog")
    method = next(node for node in dialog.body if isinstance(node, ast.FunctionDef) and node.name == "load_power_info")
    namespace = {"QListWidgetItem": object, "sqlite3": sqlite3}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(MAIN), "exec"), namespace)

    with closing(sqlite3.connect(":memory:")) as conn:
        conn.execute("CREATE TABLE powers (name, guild, cost, quest_info, skill_info)")
        conn.executemany(
            "INSERT INTO powers VALUES (?, ?, ?, ?, ?)",
            [("Power A", "Guild A", 0, "Quest", "Skill"), ("Power B", None, None, None, None)],
        )
        panel = SimpleNamespace(
            db_connection=conn,
            power_name_label=Mock(),
            guild_label=Mock(),
            cost_label=Mock(),
            quest_info_text=Mock(),
            skill_info_text=Mock(),
            _resolve_destination_for_power=Mock(),
        )
        for name, guild, cost, quest, skill in (
            ("Power A", "Guild A", "0 coins", "Quest", "Skill"),
            ("Power B", "Unknown", "Unknown", "None", "None"),
        ):
            namespace["load_power_info"](panel, SimpleNamespace(text=lambda: name))
            panel.power_name_label.setText.assert_called_with(name)
            panel.guild_label.setText.assert_called_with(guild)
            panel.cost_label.setText.assert_called_with(cost)
            panel.quest_info_text.setPlainText.assert_called_with(quest)
            panel.skill_info_text.setPlainText.assert_called_with(skill)
        panel._resolve_destination_for_power.assert_called_with("Power B", None)
    print("powers details checks passed")


if __name__ == "__main__":
    main()
