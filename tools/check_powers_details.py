"""Check that power selection fills values without repeating field captions."""

from __future__ import annotations

import ast
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Type
from unittest.mock import Mock

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QVBoxLayout,
)

MAIN = Path(__file__).resolve().parents[1] / "main_1.0.4.py"


def main() -> None:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    dialog = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "PowersDialog")
    names = {"_build_ui", "_create_labeled_field", "load_power_info"}
    methods = [node for node in dialog.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {**globals(), "T": object}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)

    class TestPanel(QDialog):
        _build_ui = namespace["_build_ui"]
        _create_labeled_field = namespace["_create_labeled_field"]
        load_power_info = namespace["load_power_info"]

        def set_destination(self):
            raise AssertionError("the rendering test must not set a destination")

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.execute("CREATE TABLE powers (name, guild, cost, quest_info, skill_info)")
        conn.executemany(
            "INSERT INTO powers VALUES (?, ?, ?, ?, ?)",
            [("Power A", "Guild A", 0, "Quest", "Skill"), ("Power B", None, None, None, None)],
        )
        panel = TestPanel()
        panel.db_connection = conn
        panel._resolve_destination_for_power = Mock()
        panel._build_ui()
        widgets = [
            panel.details_panel.itemAt(i).widget()
            for i in range(panel.details_panel.count())
        ]
        captions = (
            ("<b>Power:</b>", panel.power_name_label),
            ("<b>Guild:</b>", panel.guild_label),
            ("<b>Cost:</b>", panel.cost_label),
        )
        for caption, value_widget in captions:
            matches = [i for i, widget in enumerate(widgets) if isinstance(widget, QLabel) and widget.text() == caption]
            assert len(matches) == 1, caption
            assert widgets[matches[0] + 1] is value_widget, caption

        for name, guild, cost, quest, skill in (
            ("Power A", "Guild A", "0 coins", "Quest", "Skill"),
            ("Power B", "Unknown", "Unknown", "None", "None"),
        ):
            panel.load_power_info(QListWidgetItem(name))
            assert panel.power_name_label.text() == name
            assert panel.guild_label.text() == guild
            assert panel.cost_label.text() == cost
            assert panel.quest_info_text.toPlainText() == quest
            assert panel.skill_info_text.toPlainText() == skill
        panel._resolve_destination_for_power.assert_called_with("Power B", None)
        panel.close()
    app.processEvents()
    print("powers details checks passed")


if __name__ == "__main__":
    main()
