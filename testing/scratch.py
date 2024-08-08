#!/usr/bin/env python3
# Filename: scratch.py

import sys
import pickle
import logging
import os
import pymysql
import requests
import re
import time
import sqlite3
import webbrowser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QListWidget, QListWidgetItem, QSplitter,
    QComboBox, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt, QDateTime, QTimer

from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Define the parent directory path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(CURRENT_DIR, 'sessions')  # Directory to store session data

def ensure_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
        logging.debug(f"Created sessions directory at {SESSIONS_DIR}")
    else:
        logging.debug(f"Sessions directory already exists at {SESSIONS_DIR}")

LOCAL_HOST = "127.0.0.1"
REMOTE_HOST = "lollis-home.ddns.net"
USER = "rbc_maps"
PASSWORD = "RBC_Community_Map"
DATABASE = "city_map"

def connect_to_database():
    """
    Connect to the MySQL database.

    Returns:
        pymysql.Connection: Database connection object.
    """
    try:
        connection = pymysql.connect(
            host=LOCAL_HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        logging.debug("Connected to local MySQL instance")
        return connection
    except pymysql.MySQLError as err:
        logging.error(f"Connection to local MySQL instance failed: {err}")
        try:
            connection = pymysql.connect(
                host=REMOTE_HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
            )
            logging.debug("Connected to remote MySQL instance")
            return connection
        except pymysql.MySQLError as err:
            logging.error(f"Connection to remote MySQL instance failed: {err}")
            return None

connection = connect_to_database()
if not connection:
    sys.exit("Failed to connect to the database.")

def load_data():
    """
    Load data from the database and return it as various dictionaries and lists.

    Returns:
        tuple: Contains columns, rows, banks_coordinates, taverns_coordinates,
               transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates
    """
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `columns`")
    columns_data = cursor.fetchall()
    columns = {name: coordinate for _, name, coordinate in columns_data}

    cursor.execute("SELECT * FROM `rows`")
    rows_data = cursor.fetchall()
    rows = {name: coordinate for _, name, coordinate in rows_data}

    cursor.execute("SELECT `Column`, `Row` FROM banks")
    banks_data = cursor.fetchall()
    banks_coordinates = [(columns[col] + 1, rows[row] + 1) for col, row in banks_data]

    cursor.execute("SELECT * FROM taverns")
    taverns_data = cursor.fetchall()
    taverns_coordinates = {name: (columns.get(col) + 1, rows.get(row) + 1) for _, col, row, name in taverns_data if columns.get(col) is not None and rows.get(row) is not None}

    cursor.execute("SELECT * FROM transits")
    transits_data = cursor.fetchall()
    transits_coordinates = {name: (columns.get(col) + 1, rows.get(row) + 1) for _, col, row, name in transits_data if columns.get(col) is not None and rows.get(row) is not None}

    cursor.execute("SELECT * FROM userbuildings")
    user_buildings_data = cursor.fetchall()
    user_buildings_coordinates = {name: (columns.get(col) + 1, rows.get(row) + 1) for _, name, col, row in user_buildings_data if columns.get(col) is not None and rows.get(row) is not None}

    cursor.execute("SELECT * FROM color_mappings")
    color_mappings_data = cursor.fetchall()
    color_mappings = {type_: QColor(color) for _, type_, color in color_mappings_data}

    cursor.execute("SELECT * FROM shops")
    shops_data = cursor.fetchall()
    shops_coordinates = {name: (columns.get(col) + 1, rows.get(row) + 1) for _, name, col, row, next_update in shops_data if columns.get(col) is not None and rows.get(row) is not None}

    cursor.execute("SELECT * FROM guilds")
    guilds_data = cursor.fetchall()
    guilds_coordinates = {name: (columns.get(col) + 1, rows.get(row) + 1) for _, name, col, row, next_update in guilds_data if columns.get(col) is not None and rows.get(row) is not None}

    cursor.execute("SELECT * FROM placesofinterest")
    places_of_interest_data = cursor.fetchall()
    places_of_interest_coordinates = {name: (columns.get(col) + 1, rows.get(row) + 1) for _, name, col, row in places_of_interest_data if columns.get(col) is not None and rows.get(row) is not None}

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates

def get_next_update_times():
    """
    Retrieve the next update times for guilds and shops from the database.

    Returns:
        tuple: The next update times for guilds and shops.
    """
    cursor = connection.cursor()

    cursor.execute("SELECT next_update FROM guilds ORDER BY next_update DESC LIMIT 1")
    guilds_next_update = cursor.fetchone()
    if guilds_next_update:
        guilds_next_update = guilds_next_update[0]

    cursor.execute("SELECT next_update FROM shops ORDER BY next_update DESC LIMIT 1")
    shops_next_update = cursor.fetchone()
    if shops_next_update:
        shops_next_update = shops_next_update[0]

    return guilds_next_update, shops_next_update

columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()

class NewUserDialog(QDialog):
    def __init__(self, parent=None, user_info=None):
        super().__init__(parent)
        self.setWindowTitle("New User" if user_info is None else "Modify User")
        self.setModal(True)

        self.form_layout = QFormLayout(self)
        self.display_name_input = QLineEdit(self)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        if user_info:
            self.display_name_input.setText(user_info['display_name'])
            self.username_input.setText(user_info['username'])
            self.password_input.setText(user_info['password'])

        self.form_layout.addRow("Display Name:", self.display_name_input)
        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.form_layout.addRow(self.button_box)

    def get_user_info(self):
        return {
            'display_name': self.display_name_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text()
        }

class CityMapApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        self.profile = QWebEngineProfile.defaultProfile()
        self.cookie_store = self.profile.cookieStore()

        self.zoom_level = 3
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.color_mappings = color_mappings
        self.load_destination()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create the splitter to divide the left and right columns
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left column for minimap and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Frame for the minimap
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)
        minimap_frame.setLayout(minimap_layout)

        # Label to display the minimap
        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Information frame to display closest locations and AP costs
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Box)
        info_frame.setFixedHeight(195)
        info_layout = QVBoxLayout()
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Labels to display closest locations and destination
        self.bank_label = QLabel()
        self.bank_label.setAlignment(Qt.AlignLeft)
        self.bank_label.setStyleSheet("background-color: blue; color: white;font-weight: bold;")
        self.bank_label.setWordWrap(True)
        self.bank_label.setFixedHeight(40)
        info_layout.addWidget(self.bank_label)

        self.transit_label = QLabel()
        self.transit_label.setAlignment(Qt.AlignLeft)
        self.transit_label.setStyleSheet("background-color: red; color: white;font-weight: bold;")
        self.transit_label.setWordWrap(True)
        self.transit_label.setFixedHeight(40)
        info_layout.addWidget(self.transit_label)

        self.tavern_label = QLabel()
        self.tavern_label.setAlignment(Qt.AlignLeft)
        self.tavern_label.setStyleSheet("background-color: orange; color: white;font-weight: bold;")
        self.tavern_label.setWordWrap(True)
        self.tavern_label.setFixedHeight(40)
        info_layout.addWidget(self.tavern_label)

        self.destination_label = QLabel()
        self.destination_label.setAlignment(Qt.AlignLeft)
        self.destination_label.setStyleSheet("background-color: green; color: white;font-weight: bold;")
        self.destination_label.setWordWrap(True)
        self.destination_label.setFixedHeight(40)
        info_layout.addWidget(self.destination_label)

        # Layout for column and row selection with Go button
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_columns.addItems(columns.keys())

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_rows.addItems(rows.keys())

        go_button = QPushButton('Go')
        go_button.setFixedSize(25, 25)
        go_button.clicked.connect(self.go_to_location)

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        # Layout for zoom and set destination buttons
        zoom_layout = QHBoxLayout()
        button_size = (self.minimap_size - 10) // 3

        zoom_in_button = QPushButton('Zoom in')
        zoom_in_button.setFixedSize(button_size, 25)
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton('Zoom out')
        zoom_out_button.setFixedSize(button_size, 25)
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_button)

        set_destination_button = QPushButton('Set Destination')
        set_destination_button.setFixedSize(button_size, 25)
        set_destination_button.clicked.connect(self.set_destination)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        # Layout for refresh, discord, and website buttons
        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 25)
        refresh_button.clicked.connect(self.refresh_webview)
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 25)
        discord_button.clicked.connect(self.open_discord)
        action_layout.addWidget(discord_button)

        website_button = QPushButton('Website')
        website_button.setFixedSize(button_size, 25)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        # Frame for character list and management buttons
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        self.character_list = QListWidget()
        self.character_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.character_list.setFixedHeight(150)
        self.character_list.itemClicked.connect(self.login_character)
        character_layout.addWidget(self.character_list)

        character_buttons_layout = QHBoxLayout()
        new_button = QPushButton('New')
        new_button.setFixedSize(75, 25)
        new_button.clicked.connect(self.new_character)
        modify_button = QPushButton('Modify')
        modify_button.setFixedSize(75, 25)
        modify_button.clicked.connect(self.modify_character)
        delete_button = QPushButton('Delete')
        delete_button.setFixedSize(75, 25)
        delete_button.clicked.connect(self.delete_character)
        character_buttons_layout.addWidget(new_button)
        character_buttons_layout.addWidget(modify_button)
        character_buttons_layout.addWidget(delete_button)
        character_layout.addLayout(character_buttons_layout)

        left_layout.addWidget(character_frame)

        splitter.addWidget(left_widget)
        left_widget.setFixedWidth(300)

        # Right column for web view
        self.webview = QWebEngineView()
        self.webview.load(QUrl('https://quiz.ravenblack.net/blood.pl?action=city'))
        splitter.addWidget(self.webview)

        logging.debug("Webview added to layout and shown")

        self.load_user_list()
        self.load_active_user()

        self.show()
        self.update_minimap()

    def on_webview_load_finished(self):
        """
        Handle the event when the webview finishes loading.
        """
        self.webview.page().toHtml(self.process_html)

    def process_html(self, html):
        """
        Process the HTML content of the webview.

        Args:
            html (str): HTML content as a string.
        """
        x_coord, y_coord = self.extract_coordinates_from_html(html)
        if x_coord is not None and y_coord is not None:
            self.column_start = x_coord
            self.row_start = y_coord
            self.update_minimap()

    def extract_coordinates_from_html(self, html):
        """
        Extract coordinates from the HTML content.

        Args:
            html (str): HTML content as a string.

        Returns:
            tuple: x and y coordinates.
        """
        soup = BeautifulSoup(html, 'html.parser')
        x_input = soup.find('input', {'name': 'x'})
        y_input = soup.find('input', {'name': 'y'})
        if x_input and y_input:
            return int(x_input['value']), int(y_input['value'])

        current_location_td = soup.find('td', {'class': 'street', 'style': 'border: solid 1px white;'})

        if current_location_td:
            form = current_location_td.find('form')
            if form:
                x_value = int(form.find('input', {'name': 'x'})['value'])
                y_value = int(form.find('input', {'name': 'y'})['value'])
                return x_value, y_value

        return None, None

    def refresh_webview(self):
        """
        Refresh the webview content.
        """
        self.webview.reload()

    def draw_minimap(self):
        """
        Draws the minimap with various features such as special locations and lines to nearest locations.
        """
        pixmap = QPixmap(self.minimap_size, self.minimap_size)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, self.minimap_size, self.minimap_size, QColor('lightgrey'))

        block_size = self.minimap_size // self.zoom_level
        border_size = 1  # Size of the border around each cell
        font = painter.font()
        font.setPointSize(8)  # Adjust font size as needed
        painter.setFont(font)

        # Calculate font metrics for centering text
        font_metrics = QFontMetrics(font)

        def draw_location(column_index, row_index, color, label_text=None):
            """
            Draws a location on the minimap.

            Args:
                column_index (int): Column index of the location.
                row_index (int): Row index of the location.
                color (QColor): Color to fill the location.
                label_text (str, optional): Label text to draw at the location. Defaults to None.
            """
            x0 = (column_index - self.column_start) * block_size
            y0 = (row_index - self.row_start) * block_size

            # Draw a smaller rectangle within the cell
            inner_margin = block_size // 4
            painter.fillRect(x0 + inner_margin, y0 + inner_margin,
                             block_size - 2 * inner_margin, block_size - 2 * inner_margin, color)

            if label_text:
                text_rect = font_metrics.boundingRect(label_text)
                text_x = x0 + (block_size - text_rect.width()) // 2
                text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()
                painter.setPen(QColor('white'))
                painter.drawText(text_x, text_y, label_text)

        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                column_index = self.column_start + j
                row_index = self.row_start + i

                x0, y0 = j * block_size, i * block_size

                # Draw the cell background
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                column_name = next((name for name, coord in columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in rows.items() if coord == row_index), None)

                # Draw cell background color
                if column_index < min(columns.values()) or column_index > max(columns.values()) or row_index < min(
                        rows.values()) or row_index > max(rows.values()):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["edge"])
                elif (column_index % 2 == 1) or (row_index % 2 == 1):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["alley"])
                else:
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["default"])

                # Draw labels only at intersections of named streets
                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"
                    text_rect = font_metrics.boundingRect(label_text)
                    text_x = x0 + (block_size - text_rect.width()) // 2
                    text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()
                    painter.setPen(QColor('white'))
                    painter.drawText(text_x, text_y, label_text)

        # Draw special locations
        for (column_index, row_index) in banks_coordinates:
            draw_location(column_index, row_index, self.color_mappings["bank"], "Bank")

        for name, (column_index, row_index) in taverns_coordinates.items():
            draw_location(column_index, row_index, self.color_mappings["tavern"], name)

        for name, (column_index, row_index) in transits_coordinates.items():
            draw_location(column_index, row_index, self.color_mappings["transit"], name)

        for name, (column_index, row_index) in user_buildings_coordinates.items():
            draw_location(column_index, row_index, self.color_mappings["user_building"], name)

        for name, (column_index, row_index) in shops_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["shop"], name)
            else:
                logging.debug(f"Skipping shop '{name}' due to missing coordinates")

        for name, (column_index, row_index) in guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["guild"], name)
            else:
                logging.debug(f"Skipping guild '{name}' due to missing coordinates")

        for name, (column_index, row_index) in places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["placesofinterest"], name)
            else:
                logging.debug(f"Skipping place of interest '{name}' due to missing coordinates")

        # Get current location
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find and draw lines to nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        if nearest_tavern:
            nearest_tavern = nearest_tavern[0][1]
            painter.setPen(QPen(QColor('orange'), 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_tavern[0] - self.column_start) * block_size + block_size // 2,
                (nearest_tavern[1] - self.row_start) * block_size + block_size // 2
            )

        if nearest_bank:
            nearest_bank = nearest_bank[0][1]
            painter.setPen(QPen(QColor('blue'), 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank[0] - self.column_start) * block_size + block_size // 2,
                (nearest_bank[1] - self.row_start) * block_size + block_size // 2
            )

        if nearest_transit:
            nearest_transit = nearest_transit[0][1]
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit[0] - self.column_start) * block_size + block_size // 2,
                (nearest_transit[1] - self.row_start) * block_size + block_size // 2
            )

        # Draw destination line
        if self.destination:
            painter.setPen(QPen(QColor('green'), 3))  # Set pen color to green and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (self.destination[0] - self.column_start) * block_size + block_size // 2,
                (self.destination[1] - self.row_start) * block_size + block_size // 2
            )

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        """
        Update the minimap.
        """
        self.draw_minimap()
        self.update_info_frame()

    def find_nearest_location(self, x, y, locations):
        """
        Find the nearest location to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            locations (list): List of location coordinates.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        distances = []
        for loc in locations:
            lx, ly = loc
            dist = max(abs(lx - x), abs(ly - y))  # Using Chebyshev distance
            distances.append((dist, (lx, ly)))
        distances.sort()
        return distances

    def find_nearest_tavern(self, x, y):
        """
        Find the nearest tavern to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, list(taverns_coordinates.values()))

    def find_nearest_bank(self, x, y):
        """
        Find the nearest bank to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, banks_coordinates)

    def find_nearest_transit(self, x, y):
        """
        Find the nearest transit station to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, list(transits_coordinates.values()))

    def set_destination(self):
        """
        Set the destination to the current location.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2
        if self.destination == (current_x, current_y):
            self.destination = None
        else:
            self.destination = (current_x, current_y)
        self.save_destination()
        self.update_minimap()

    def save_destination(self):
        """
        Save the destination to a file.
        """
        with open('destination.pkl', 'wb') as f:
            pickle.dump(self.destination, f)
            pickle.dump(datetime.now(), f)

    def load_destination(self):
        """
        Load the destination from a file.
        """
        try:
            with open('destination.pkl', 'rb') as f:
                self.destination = pickle.load(f)
                self.scrape_timestamp = pickle.load(f)
        except FileNotFoundError:
            self.destination = None
            self.scrape_timestamp = datetime.min

    def zoom_in(self):
        """
        Zoom in the minimap.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_minimap()

    def zoom_out(self):
        """
        Zoom out the minimap.
        """
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()
        if column_name in columns:
            self.column_start = columns[column_name] - self.zoom_level // 2
        if row_name in rows:
            self.row_start = rows[row_name] - self.zoom_level // 2
        self.update_minimap()

    def mousePressEvent(self, event):
        """
        Handle mouse press event to update the minimap location.

        Args:
            event (QMouseEvent): Mouse event.
        """
        if event.x() < self.minimap_label.width() and event.y() < self.minimap_label.height():
            x = event.x()
            y = event.y()

            block_size = self.minimap_size // self.zoom_level
            col_clicked = x // block_size
            row_clicked = y // block_size

            new_column_start = self.column_start + col_clicked - self.zoom_level // 2
            new_row_start = self.row_start + row_clicked - self.zoom_level // 2

            if -1 <= new_column_start <= 201 - self.zoom_level + 1:
                self.column_start = new_column_start
            if -1 <= new_row_start <= 201 - self.zoom_level + 1:
                self.row_start = new_row_start

            self.update_minimap()

    def calculate_ap_cost(self, start, end):
        """
        Calculate the AP cost of moving from start to end using the Chebyshev distance.

        Args:
            start (tuple): Starting coordinates (x, y).
            end (tuple): Ending coordinates (x, y).

        Returns:
            int: AP cost of moving from start to end.
        """
        return max(abs(start[0] - end[0]), abs(start[1] - end[1]))  # Using Chebyshev distance

    def update_info_frame(self):
        """
        Update the information frame with the closest locations and AP costs.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        # Get details for nearest tavern
        if nearest_tavern:
            tavern_coords = nearest_tavern[0][1]
            tavern_name = next(name for name, coords in taverns_coordinates.items() if coords == tavern_coords)
            tavern_ap_cost = self.calculate_ap_cost((current_x, current_y), tavern_coords)
            tavern_intersection = self.get_intersection_name((tavern_coords[0] - 1, tavern_coords[1] - 1))
            self.tavern_label.setText(f"{tavern_name}\n{tavern_intersection}\nAP: {tavern_ap_cost}")

        # Get details for nearest bank
        if nearest_bank:
            bank_coords = nearest_bank[0][1]
            bank_ap_cost = self.calculate_ap_cost((current_x, current_y), bank_coords)
            bank_intersection = self.get_intersection_name((bank_coords[0] - 1, bank_coords[1] - 1))
            self.bank_label.setText(f"OmniBank\n{bank_intersection}\nAP: {bank_ap_cost}")

        # Get details for nearest transit
        if nearest_transit:
            transit_coords = nearest_transit[0][1]
            transit_name = next(name for name, coords in transits_coordinates.items() if coords == transit_coords)
            transit_ap_cost = self.calculate_ap_cost((current_x, current_y), transit_coords)
            transit_intersection = self.get_intersection_name((transit_coords[0] - 1, transit_coords[1] - 1))
            self.transit_label.setText(f"{transit_name}\n{transit_intersection}\nAP: {transit_ap_cost}")

        # Get details for set destination
        if self.destination:
            destination_coords = self.destination
            destination_ap_cost = self.calculate_ap_cost((current_x, current_y), destination_coords)
            destination_intersection = self.get_intersection_name((destination_coords[0] - 1, destination_coords[1] - 1))
            self.destination_label.setText(f"Destination\n{destination_intersection}\nAP: {destination_ap_cost}")
        else:
            self.destination_label.setText("No Destination Set")

    def get_intersection_name(self, coords):
        """
        Get the intersection name for the given coordinates.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: Intersection name.
        """
        x, y = coords
        column_name = next((name for name, coord in columns.items() if coord == x), "")
        row_name = next((name for name, coord in rows.items() if coord == y), "")
        return f"{column_name} & {row_name}"

    def open_discord(self):
        """
        Open the Discord link in the default web browser.
        """
        webbrowser.open("https://discord.gg/ktdG9FZ")

    def load_user_list(self):
        self.character_list.clear()
        users = load_user_info()
        for user in users:
            item = QListWidgetItem(user['display_name'])
            item.setData(Qt.UserRole, user)
            self.character_list.addItem(item)
        logging.debug("User list loaded")

    def new_character(self):
        dialog = NewUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_info = dialog.get_user_info()
            users = load_user_info()
            users.append(user_info)
            save_user_info(users)
            self.load_user_list()

    def modify_character(self):
        current_item = self.character_list.currentItem()
        if current_item:
            user_info = current_item.data(Qt.UserRole)
            dialog = NewUserDialog(self, user_info)
            if dialog.exec_() == QDialog.Accepted:
                new_user_info = dialog.get_user_info()
                users = load_user_info()
                for i, user in enumerate(users):
                    if user == user_info:
                        users[i] = new_user_info
                        break
                save_user_info(users)
                self.load_user_list()

    def delete_character(self):
        current_item = self.character_list.currentItem()
        if current_item:
            user_info = current_item.data(Qt.UserRole)
            users = load_user_info()
            users = [user for user in users if user != user_info]
            save_user_info(users)
            self.load_user_list()
            save_active_user(None)

    def login_character(self, item):
        user_info = item.data(Qt.UserRole)
        self.set_active_user(user_info)

    def set_active_user(self, user_info):
        """
        Set the specified user as active, saving the current session data and loading the new user's session.
        """
        logging.debug(f"Setting active user: {user_info}")
        # Save session for the currently active user
        current_active_user = load_active_user()
        if current_active_user:
            self.save_session(current_active_user['username'])

        # Set the new active user
        save_active_user(user_info)
        self.load_session(user_info['username'])
        self.webview.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=city'))

    def load_active_user(self):
        user_info = load_active_user()
        if user_info:
            self.set_active_user(user_info)

    def load_session(self, username):
        """
        Load session for the specified user and set it in the web engine profile.
        """
        ensure_sessions_dir()
        session_file = os.path.join(SESSIONS_DIR, f'session_{username}.pkl')
        logging.debug(f"Attempting to load session file: {session_file}")
        if os.path.exists(session_file):
            try:
                with open(session_file, 'rb') as file:
                    session_data = pickle.load(file)
                    logging.debug(f"Loaded session data for user {username}: {session_data}")
                    self.apply_session_data(session_data)
            except Exception as e:
                logging.error(f"Failed to load session data for user {username}: {e}")
                logging.debug(f"Session data may be corrupted or incomplete.")
        else:
            logging.debug(f"No session file found for user {username}. Logging in normally.")

    def save_session(self, username):
        """
        Save session for the specified user from the web engine profile.
        """
        profile = self.webview.page().profile()  # Get QWebEngineProfile
        cookie_store = profile.cookieStore()  # Get QWebEngineCookieStore

        def handle_cookie(cookie):
            logging.debug(f"Cookie: {cookie}")  # Print cookie for debugging
            self._extract_and_save_session([cookie], username)  # Process cookie

        # Connect the signal to the slot
        cookie_store.cookieAdded.connect(handle_cookie)

        # Reload the page to trigger the cookieAdded signal
        self.webview.reload()

        # Disconnect the signal after processing to prevent memory leaks or unintended behavior
        QTimer.singleShot(5000, lambda: cookie_store.cookieAdded.disconnect(handle_cookie))

    def _extract_and_save_session(self, cookies, username):
        """
        Extract session data and save it for the specified user.
        """
        session_data = {
            'cookies': []
        }
        for cookie in cookies:
            session_data['cookies'].append({
                'name': cookie.name().data().decode(),
                'value': cookie.value().data().decode(),
                'domain': cookie.domain(),
                'path': cookie.path(),
                'expires': cookie.expirationDate().toMSecsSinceEpoch(),
                'is_secure': cookie.isSecure(),
                'is_httponly': cookie.isHttpOnly()
            })
        ensure_sessions_dir()
        session_file = os.path.join(SESSIONS_DIR, f'session_{username}.pkl')
        logging.debug(f"Saving session data to file: {session_file}")
        with open(session_file, 'wb') as file:
            pickle.dump(session_data, file)
        logging.debug(f"Session data saved for user {username}: {session_data}")

    def apply_session_data(self, session_data):
        """
        Apply session data to the web engine profile.
        """
        self.clear_cookies()
        profile = self.webview.page().profile()  # Get QWebEngineProfile
        cookie_jar = profile.cookieStore()  # Get QNetworkCookieStore

        for cookie_data in session_data.get('cookies', []):
            q_cookie = QNetworkCookie(cookie_data['name'].encode(), cookie_data['value'].encode())
            q_cookie.setDomain(cookie_data['domain'])
            q_cookie.setPath(cookie_data['path'])
            q_cookie.setExpirationDate(QDateTime.fromMSecsSinceEpoch(cookie_data['expires']))
            q_cookie.setSecure(cookie_data['is_secure'])
            q_cookie.setHttpOnly(cookie_data['is_httponly'])
            cookie_jar.setCookie(q_cookie)
        logging.debug("Session data applied")

    def clear_cookies(self):
        """
        Clear all cookies in the cookie store.
        """
        logging.debug("Clearing cookies")
        self.cookie_store.deleteAllCookies()


def scrape_avitd_data():
    """
    Scrape guilds and shops data from A View in the Dark and update the database with next update timestamps.
    """
    url = "https://aviewinthedark.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    cursor = connection.cursor()

    # Extract the time for next update
    guilds_next_update_text = None
    shops_next_update_text = None

    next_change_divs = soup.find_all('div', class_='next_change')
    for div in next_change_divs:
        if "Guilds" in div.text:
            guilds_next_update_text = div.text
        elif "Shops" in div.text:
            shops_next_update_text = div.text

    if not guilds_next_update_text or not shops_next_update_text:
        sys.exit("Failed to find the next update times for guilds and shops.")

    logging.debug("Guilds next update text: %s", guilds_next_update_text)
    logging.debug("Shops next update text: %s", shops_next_update_text)

    guilds_next_update_time = extract_next_update_time(guilds_next_update_text)
    shops_next_update_time = extract_next_update_time(shops_next_update_text)

    update_guilds(cursor, soup, guilds_next_update_time)
    update_shops(cursor, soup, shops_next_update_time)

    connection.commit()

def extract_next_update_time(text):
    """
    Extract the next update time from the text and calculate the next update timestamp.

    Args:
        text (str): Text containing the update time.

    Returns:
        datetime: The next update timestamp.
    """
    # Regular expression to find all integers followed by time units
    matches = re.findall(r'(\d+)\s*(days?|h|m|s)', text)

    # Initialize time components
    days = hours = minutes = seconds = 0

    # Assign values based on time units
    for value, unit in matches:
        value = int(value)
        if 'day' in unit:
            days = value
        elif 'h' in unit:
            hours = value
        elif 'm' in unit:
            minutes = value
        elif 's' in unit:
            seconds = value

    # Calculate the next update time
    next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    next_update = next_update.replace(second=0, microsecond=0) + timedelta(minutes=1)
    return next_update

def update_guild(cursor, name, location, next_update_time):
    """
    Update a single guild in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        name (str): Name of the guild.
        location (str): Location of the guild.
        next_update_time (datetime): The next update timestamp.
    """
    col, row = location.split(' and ')
    cursor.execute("""
        UPDATE guilds 
        SET `Column`=%s, `Row`=%s, next_update=%s 
        WHERE Name=%s
    """, (col, row, next_update_time, name))

def update_shop(cursor, name, location, next_update_time):
    """
    Update a single shop in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        name (str): Name of the shop.
        location (str): Location of the shop.
        next_update_time (datetime): The next update timestamp.
    """
    col, row = location.split(' and ')
    cursor.execute("""
        UPDATE shops 
        SET `Column`=%s, `Row`=%s, next_update=%s 
        WHERE Name=%s
    """, (col, row, next_update_time, name))

def update_guilds(cursor, soup, next_update_time):
    """
    Update the guilds data in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        soup (BeautifulSoup): BeautifulSoup object containing the HTML data.
        next_update_time (datetime): The next update timestamp.
    """
    for name in guilds_coordinates:
        location_tag = soup.find('td', string=name)
        if location_tag:
            location = location_tag.find_next_sibling('td').text.replace('SE of ', '').strip()
            update_guild(cursor, name, location, next_update_time)
        else:
            logging.debug(f"Guild '{name}' not found in the table.")

def update_shops(cursor, soup, next_update_time):
    """
    Update the shops data in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        soup (BeautifulSoup): BeautifulSoup object containing the HTML data.
        next_update_time (datetime): The next update timestamp.
    """
    for name in shops_coordinates:
        location_tag = soup.find('td', string=name)
        if location_tag:
            location = location_tag.find_next_sibling('td').text.replace('SE of ', '').strip()
            update_shop(cursor, name, location, next_update_time)
        else:
            logging.debug(f"Shop '{name}' not found in the table.")

def save_user_info(user_info):
    ensure_sessions_dir()
    users_file = os.path.join(SESSIONS_DIR, 'users.pkl')
    with open(users_file, 'wb') as file:
        pickle.dump(user_info, file)
    logging.debug(f"User info saved: {user_info}")

def load_user_info():
    ensure_sessions_dir()
    users_file = os.path.join(SESSIONS_DIR, 'users.pkl')
    logging.debug(f"Attempting to load user info from: {users_file}")
    try:
        with open(users_file, 'rb') as file:
            user_info = pickle.load(file)
            logging.debug(f"Loaded user info: {user_info}")
            return user_info
    except FileNotFoundError:
        logging.debug("User info file not found.")
        return []

def save_active_user(user):
    ensure_sessions_dir()
    active_user_file = os.path.join(SESSIONS_DIR, 'active_user.pkl')
    with open(active_user_file, 'wb') as file:
        pickle.dump(user, file)
    logging.debug(f"Active user saved: {user}")

def load_active_user():
    ensure_sessions_dir()
    active_user_file = os.path.join(SESSIONS_DIR, 'active_user.pkl')
    logging.debug(f"Attempting to load active user from: {active_user_file}")
    try:
        with open(active_user_file, 'rb') as file:
            active_user = pickle.load(file)
            logging.debug(f"Loaded active user: {active_user}")
            return active_user
    except FileNotFoundError:
        logging.debug("Active user file not found.")
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    guilds_next_update, shops_next_update = get_next_update_times()
    if datetime.now() >= guilds_next_update or datetime.now() >= shops_next_update:
        scrape_avitd_data()
    window = CityMapApp()
    window.show()
    sys.exit(app.exec_())
