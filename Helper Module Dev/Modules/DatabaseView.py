#!/usr/bin/env python3
# Filename: DatabaseView
# Copyright 2024 RBC Community Map Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import pymysql
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem)
from PySide6.QtGui import QAction

# Database connection constants
HOST = "127.0.0.1"  # or REMOTE_HOST if needed
USER = "rbc_maps"
PASSWORD = "RBC_Community_Map"
DATABASE = "city_map"


def connect_to_database():
    """
    Connect to the MySQL database and return the connection object.
    """
    try:
        connection = pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        logging.info("Connected to MySQL database")
        return connection
    except pymysql.MySQLError as err:
        logging.error(f"Connection failed: {err}")
        sys.exit(f"Connection failed: {err}")


class DatabaseViewer(QMainWindow):
    """
    Main application class for viewing database tables.
    """

    def __init__(self):
        """
        Initialize the DatabaseViewer and load table data.
        """
        super().__init__()
        self.setWindowTitle('MySQL Database Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.connection = connect_to_database()
        self.cursor = self.connection.cursor()

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.load_all_tables()

    def load_all_tables(self):
        """
        Load all tables from the database and create tabs for each table.
        """
        try:
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()

            for (table_name,) in tables:
                column_names, data = self.fetch_table_data(self.cursor, table_name)
                self.add_table_tab(table_name, column_names, data)

        except pymysql.MySQLError as e:
            logging.error(f"Failed to load tables: {e}")
            sys.exit(f"Failed to load tables: {e}")

    def fetch_table_data(self, cursor, table_name):
        """
        Fetch data from the specified table and return it as a list of tuples,
        including column names.

        Args:
            cursor: MySQL cursor object.
            table_name: Name of the table to fetch data from.

        Returns:
            List of tuples containing column names and table data.
        """
        cursor.execute(f"DESCRIBE `{table_name}`")
        column_names = [col[0] for col in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()

        return column_names, data

    def add_table_tab(self, table_name, column_names, data):
        """
        Add a new tab for a table.

        Args:
            table_name: The name of the table.
            column_names: List of column names for the table.
            data: The data to display in the table.
        """
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(column_names))
        table_widget.setHorizontalHeaderLabels(column_names)

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        self.tab_widget.addTab(table_widget, table_name)

    def closeEvent(self, event):
        """
        Ensure the database connection is closed when the application is closed.
        """
        self.cursor.close()
        self.connection.close()
        event.accept()


def main():
    """
    Main function to run the application.
    """
    app = QApplication(sys.argv)
    viewer = DatabaseViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
