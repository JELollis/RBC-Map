#!/usr/bin/env python3
# Filename: main_0.7.1

"""
RBC City Map Application
=========================
This application provides a graphical interface to view a city map of RavenBlack City.
It includes features such as viewing the map, zooming in and out, setting destinations,
and refreshing the map with updated data from the 'A View in the Dark' website.

Modules:
- sys
- pickle
- pymysql
- requests
- datetime
- bs4 (BeautifulSoup)
- PyQt6
- PyQt6.QtWebEngineWidgets
- PyQt6.QtWebChannel

Classes:
- CityMapApp: Main application class for the RBC City Map.

Functions:
- connect_to_database: Establish a connection to the MySQL database.
- load_data: Load data from the database and return it as various dictionaries and lists.
- scrape_avitd_data: Scrape guilds and shops data from 'A View in the Dark' and update the database with next update timestamps.
- extract_next_update_time: Extract the next update time from the text and calculate the next update timestamp.
- update_guild: Update a single guild in the database.
- update_shop: Update a single shop in the database.
- update_guilds: Update the guilds data in the database.
- update_shops: Update the shops data in the database.

To install all required modules, run the following command:
 pip install pymysql requests beautifulsoup4 PyQt6 PyQt6-WebEngine PyQt6-WebChannel
"""

# -----------------------
# Importing required modules
# -----------------------

import sys
import pickle
import pymysql
import requests
import re
import os
import webbrowser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem,
    QMessageBox, QScrollArea, QFileDialog, QTabWidget, QColorDialog, QGridLayout)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction
from PyQt6.QtCore import QUrl, Qt, QRect, QPropertyAnimation, QEasingCurve, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineSettings
import logging


# -----------------------
# Directory setup
# -----------------------

def ensure_directories_exist():
    """
    Ensure that the required directories exist. If they don't, create them.
    """
    required_dirs = ['logs', 'sessions', 'settings']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Call the function to ensure directories are present
ensure_directories_exist()

# -----------------------
# Logging setup
# -----------------------

def setup_logging():
    """
    Setup logging configuration to save logs in the 'logs' directory with the filename 'rbc_{date}.log'.
    """
    log_filename = datetime.now().strftime('logs/rbc_%Y-%m-%d.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filename,
        filemode='a'
    )
    print(f"Logging to: {log_filename}")

# Call the logging setup
setup_logging()

# -----------------------
# Database connection
# -----------------------

# Server information
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
        logging.info("Connected to local MySQL instance")
        return connection
    except pymysql.MySQLError as err:
        logging.error("Connection to local MySQL instance failed: %s", err)
        # Attempt to connect to the remote server
        try:
            connection = pymysql.connect(
                host=REMOTE_HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
            )
            logging.info("Connected to remote MySQL instance")
            return connection
        except pymysql.MySQLError as err:
            logging.error("Connection to remote MySQL instance failed: %s", err)
            return None

# -----------------------
# Load Data from Database
# -----------------------

def load_data():
    """
    Load data from the database and return it as various dictionaries and lists.

    Returns:
        tuple: Contains columns, rows, banks_coordinates, taverns_coordinates,
               transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates
    """
    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

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

    connection.close()

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates

# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()

# -----------------------
# CityMapApp Main Class
# -----------------------

class CityMapApp(QMainWindow):
    """
    Main application class for the RBC City Map.
    """

    def __init__(self):
        """
        Initialize the CityMapApp and its components.
        """
        super().__init__()

        self.setWindowIcon(QIcon('favicon.ico'))
        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        self.zoom_level = 3
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.color_mappings = color_mappings

        self.characters = []
        self.character_list = QListWidget()
        self.selected_character = None
        self.webview_loaded = False  # To prevent multiple loadFinished events

        self.load_characters()

        if not self.characters:
            self.add_new_character()
            if not self.characters:
                sys.exit("No characters added. Exiting the application.")

        self.setup_ui()
        self.setup_console_logging()
        self.show()
        self.update_minimap()

    def setup_ui(self):
        """
        Setup the main user interface for the application.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.create_menu_bar()

        map_layout = QHBoxLayout()
        main_layout.addLayout(map_layout)

        left_layout = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Shape.Box)
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left_layout)

        # Minimap setup
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Shape.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)
        minimap_frame.setLayout(minimap_layout)

        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Info frame setup
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setFixedHeight(80)
        info_layout = QVBoxLayout()
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        self.bank_label = QLabel()
        self.bank_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.bank_label.setStyleSheet("background-color: blue; color: white;font-weight: bold;")
        self.bank_label.setWordWrap(True)
        self.bank_label.setFixedHeight(15)
        info_layout.addWidget(self.bank_label)

        self.transit_label = QLabel()
        self.transit_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.transit_label.setStyleSheet("background-color: red; color: white;font-weight: bold;")
        self.transit_label.setWordWrap(True)
        self.transit_label.setFixedHeight(15)
        info_layout.addWidget(self.transit_label)

        self.tavern_label = QLabel()
        self.tavern_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tavern_label.setStyleSheet("background-color: orange; color: white;font-weight: bold;")
        self.tavern_label.setWordWrap(True)
        self.tavern_label.setFixedHeight(15)
        info_layout.addWidget(self.tavern_label)

        self.destination_label = QLabel()
        self.destination_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.destination_label.setStyleSheet("background-color: green; color: white;font-weight: bold;")
        self.destination_label.setWordWrap(True)
        self.destination_label.setFixedHeight(15)
        info_layout.addWidget(self.destination_label)

        # ComboBox and Go Button
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_columns.addItems(columns.keys())

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_rows.addItems(rows.keys())

        go_button = QPushButton('Go')
        go_button.setFixedSize(25, 25)
        go_button.clicked.connect(self.go_to_location)

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        # Zoom and action buttons
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

        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 25)
        refresh_button.clicked.connect(self.refresh_webview)
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 25)
        discord_button.clicked.connect(self.open_discord)
        action_layout.addWidget(discord_button)

        shops_guilds_button = QPushButton('Shops/Guilds')
        shops_guilds_button.setFixedSize(button_size, 25)
        shops_guilds_button.clicked.connect(self.open_shops_guilds)
        action_layout.addWidget(shops_guilds_button)

        left_layout.addLayout(action_layout)

        # Character list frame
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Shape.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        self.character_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.character_list.setFixedHeight(100)
        self.character_list.itemClicked.connect(self.on_character_selected)
        character_layout.addWidget(self.character_list)

        character_buttons_layout = QHBoxLayout()
        new_button = QPushButton('New')
        new_button.setFixedSize(75, 25)
        new_button.clicked.connect(self.add_new_character)
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

        # Web engine view
        map_layout.addWidget(left_frame)

        self.website_frame = QWebEngineView()
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)
        map_layout.addWidget(self.website_frame)

        self.show()
        self.update_minimap()

    def create_menu_bar(self):
        """
        Create the menu bar with File, Settings, and Help menus.
        """
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu('File')
        save_webpage_action = QAction('Save Webpage Screenshot', self)
        save_webpage_action.triggered.connect(self.save_webpage_screenshot)
        file_menu.addAction(save_webpage_action)

        save_app_action = QAction('Save App Screenshot', self)
        save_app_action.triggered.connect(self.save_app_screenshot)
        file_menu.addAction(save_app_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menu_bar.addMenu('Settings')
        theme_action = QAction('Change Theme', self)
        theme_action.triggered.connect(self.change_theme)
        settings_menu.addAction(theme_action)

        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in_browser)
        settings_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out_browser)
        settings_menu.addAction(zoom_out_action)

        # Help menu
        help_menu = menu_bar.addMenu('Help')
        faq_action = QAction('FAQ', self)
        faq_action.triggered.connect(lambda: webbrowser.open('https://quiz.ravenblack.net/faq.pl'))
        help_menu.addAction(faq_action)

        how_to_play_action = QAction('How to Play', self)
        how_to_play_action.triggered.connect(lambda: webbrowser.open('https://quiz.ravenblack.net/bloodhowto.html'))
        help_menu.addAction(how_to_play_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        credits_action = QAction('Credits', self)
        credits_action.triggered.connect(self.show_credits_dialog)
        help_menu.addAction(credits_action)

    def zoom_in_browser(self):
        """
        Zoom in on the web page displayed in the QWebEngineView.
        """
        self.website_frame.setZoomFactor(self.website_frame.zoomFactor() + 0.1)

    def zoom_out_browser(self):
        """
        Zoom out on the web page displayed in the QWebEngineView.
        """
        self.website_frame.setZoomFactor(self.website_frame.zoomFactor() - 0.1)

    def setup_console_logging(self):
        """
        Setup console logging within the web engine view.
        """
        self.web_channel = QWebChannel(self.website_frame.page())
        self.website_frame.page().setWebChannel(self.web_channel)
        self.web_channel.registerObject("qtHandler", self)

    def inject_console_logging(self):
        """
        Inject JavaScript into the web page to capture console logs and send them to PyQt.
        """
        script = """
            (function() {
                var console_log = console.log;
                console.log = function(message) {
                    console_log(message);
                    if (typeof qtHandler !== 'undefined' && qtHandler.handleConsoleMessage) {
                        qtHandler.handleConsoleMessage(message);
                    }
                };
            })();
        """
        self.website_frame.page().runJavaScript(script)

    @pyqtSlot(str)
    def handle_console_message(self, message):
        """
        Handle console messages from the web view and log them.

        Args:
            message (str): The console message.
        """
        print(f"Console message: {message}")
        logging.debug(f"Console message: {message}")

    # -----------------------
    # Web View Handling
    # -----------------------

    def on_webview_load_finished(self):
        """
        Handle the event when the webview finishes loading.
        """
        if not self.webview_loaded:
            self.webview_loaded = True
            self.inject_console_logging()

    def refresh_webview(self):
        """
        Refresh the webview content.
        """
        self.website_frame.reload()

    def save_webpage_screenshot(self):
        """
        Save the current webpage as a screenshot.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Webpage Screenshot", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.website_frame.grab().save(file_name)

    def save_app_screenshot(self):
        """
        Save the current application window as a screenshot.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save App Screenshot", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.grab().save(file_name)

    # -----------------------
    # Character Management
    # -----------------------

    def load_characters(self):
        """
        Load characters from a pickle file in the 'sessions' directory.
        """
        try:
            with open('sessions/characters.pkl', 'rb') as f:
                self.characters = pickle.load(f)
                self.character_list.clear()
                for character in self.characters:
                    self.character_list.addItem(QListWidgetItem(character['name']))
                logging.debug("Characters loaded successfully from file.")
        except FileNotFoundError:
            logging.warning("Characters file not found. No characters loaded.")
            self.characters = []
        except Exception as e:
            logging.error(f"Failed to load characters: {e}")
            self.characters = []

    def save_characters(self):
        """
        Save characters to a pickle file in the 'sessions' directory.
        """
        try:
            os.makedirs('sessions', exist_ok=True)

            with open('sessions/characters.pkl', 'wb') as f:
                pickle.dump(self.characters, f)
                logging.debug("Characters saved successfully to file.")
        except Exception as e:
            logging.error(f"Failed to save characters: {e}")

    def on_character_selected(self, item):
        """
        Handle the event when a character is selected from the list.

        Args:
            item (QListWidgetItem): The selected character item.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)
        if selected_character:
            logging.debug(f"Selected character: {character_name}")
            self.selected_character = selected_character
            self.logout_current_character()

    def logout_current_character(self):
        """
        Log out the currently logged-in character.
        """
        logging.debug("Logging out current character.")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))
        self.website_frame.loadFinished.connect(self.login_selected_character)

    def login_selected_character(self):
        """
        Log in the selected character using their saved credentials.
        """
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        logging.debug(f"Logging in character: {self.selected_character['name']}")
        name = self.selected_character['name']
        password = self.selected_character['password']

        login_script = f"""
            var loginForm = document.querySelector('form');
            if (loginForm) {{
                loginForm.iam.value = '{name}';
                loginForm.passwd.value = '{password}';
                loginForm.submit();
            }} else {{
                console.error('Login form not found.');
            }}
        """
        self.website_frame.page().runJavaScript(login_script)

    def add_new_character(self):
        """
        Add a new character to the list.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)
        if dialog.exec_():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()
            self.characters.append({'name': name, 'password': password})
            self.save_characters()
            self.character_list.addItem(QListWidgetItem(name))
            logging.debug(f"Character {name} added.")

    def modify_character(self):
        """
        Modify the selected character's details.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for modification.")
            return

        name = current_item.text()
        character = next((char for char in self.characters if char['name'] == name), None)
        if character:
            logging.debug(f"Modifying character: {name}")
            dialog = CharacterDialog(self, character)
            if dialog.exec_():
                character['name'] = dialog.name_edit.text()
                character['password'] = dialog.password_edit.text()
                self.save_characters()
                current_item.setText(character['name'])
                logging.debug(f"Character {name} modified.")

    def delete_character(self):
        """
        Delete the selected character from the list.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for deletion.")
            return

        name = current_item.text()
        self.characters = [char for char in self.characters if char['name'] != name]
        self.save_characters()
        self.character_list.takeItem(self.character_list.row(current_item))
        logging.debug(f"Character {name} deleted.")

    # -----------------------
    # Minimap Drawing and Update
    # -----------------------

    def draw_minimap(self):
        """
        Draw the minimap with different locations highlighted using colors.
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

                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                column_name = next((name for name, coord in columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in rows.items() if coord == row_index), None)

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

                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"
                    text_rect = font_metrics.boundingRect(label_text)
                    text_x = x0 + (block_size - text_rect.width()) // 2
                    text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()
                    painter.setPen(QColor('white'))
                    painter.drawText(text_x, text_y, label_text)

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
                logging.warning(f"Skipping shop '{name}' due to missing coordinates")

        for name, (column_index, row_index) in guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["guild"], name)
            else:
                logging.warning(f"Skipping guild '{name}' due to missing coordinates")

        for name, (column_index, row_index) in places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["placesofinterest"], name)
            else:
                logging.warning(f"Skipping place of interest '{name}' due to missing coordinates")

        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        if nearest_tavern:
            nearest_tavern = nearest_tavern[0][1]
            painter.setPen(QPen(QColor('orange'), 3))
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_tavern[0] - self.column_start) * block_size + block_size // 2,
                (nearest_tavern[1] - self.row_start) * block_size + block_size // 2
            )

        if nearest_bank:
            nearest_bank = nearest_bank[0][1]
            painter.setPen(QPen(QColor('blue'), 3))
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank[0] - self.column_start) * block_size + block_size // 2,
                (nearest_bank[1] - self.row_start) * block_size + block_size // 2
            )

        if nearest_transit:
            nearest_transit = nearest_transit[0][1]
            painter.setPen(QPen(QColor('red'), 3))
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit[0] - self.column_start) * block_size + block_size // 2,
                (nearest_transit[1] - self.row_start) * block_size // 2
            )

        if self.destination:
            painter.setPen(QPen(QColor('green'), 3))
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (self.destination[0] - self.column_start) * block_size + block_size // 2,
                (self.destination[1] - self.row_start) * block_size // 2
            )

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        """
        Update the minimap by redrawing it and refreshing the info frame.
        """
        self.draw_minimap()
        self.update_info_frame()

    def find_nearest_location(self, x, y, locations):
        """
        Find the nearest location (e.g., tavern, bank, or transit) to the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.
            locations (list): List of location coordinates.

        Returns:
            list: Sorted list of distances and their corresponding coordinates.
        """
        distances = []
        for loc in locations:
            lx, ly = loc
            dist = max(abs(lx - x), abs(ly - y))
            distances.append((dist, (lx, ly)))
        distances.sort()
        return distances

    def find_nearest_tavern(self, x, y):
        """
        Find the nearest tavern to the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.

        Returns:
            list: Sorted list of distances and tavern coordinates.
        """
        return self.find_nearest_location(x, y, list(taverns_coordinates.values()))

    def find_nearest_bank(self, x, y):
        """
        Find the nearest bank to the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.

        Returns:
            list: Sorted list of distances and bank coordinates.
        """
        return self.find_nearest_location(x, y, banks_coordinates)

    def find_nearest_transit(self, x, y):
        """
        Find the nearest transit to the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.

        Returns:
            list: Sorted list of distances and transit coordinates.
        """
        return self.find_nearest_location(x, y, list(transits_coordinates.values()))

    def set_destination(self):
        """
        Set or unset the destination on the minimap.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2
        if self.destination == (current_x, current_y):
            self.destination = None
        else:
            self.destination = (current_x, current_y)
        self.save_destination()
        self.update_minimap()
        self.refresh_webview()

    def save_destination(self):
        """
        Save the current destination and timestamp to a pickle file.
        """
        with open('destination.pkl', 'wb') as f:
            pickle.dump(self.destination, f)
            pickle.dump(datetime.now(), f)

    def load_destination(self):
        """
        Load the saved destination and timestamp from a pickle file.
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
        Zoom in on the minimap.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_minimap()

    def zoom_out(self):
        """
        Zoom out on the minimap.
        """
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location on the minimap based on the selected column and row from the comboboxes.
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
        Handle mouse press events on the minimap.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.x() < self.minimap_label.width() and event.y() < self.minimap_label.height():
            x = event.x()
            y = event.y()

            block_size = self.minimap_size // self.zoom_level
            col_clicked = x // block_size
            row_clicked = y // block_size

            new_column_start = self.column_start + col_clicked - self.zoom_level // 2
            new_row_start = self.row_start + row_clicked - self.zoom_level // 2

            if -1 <= new_column_start <= 200 - self.zoom_level + 1:
                self.column_start = new_column_start
            if -1 <= new_row_start <= 200 - self.zoom_level + 1:
                self.row_start = new_row_start

            self.update_minimap()

    def calculate_ap_cost(self, start, end):
        """
        Calculate the action point (AP) cost between two locations.

        Args:
            start (tuple): Starting coordinates (x, y).
            end (tuple): Ending coordinates (x, y).

        Returns:
            int: The calculated AP cost.
        """
        return max(abs(start[0] - end[0]), abs(start[1] - end[1]))

    def update_info_frame(self):
        """
        Update the info frame with details of the nearest locations and the current destination.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        if nearest_tavern:
            tavern_coords = nearest_tavern[0][1]
            tavern_name = next(name for name, coords in taverns_coordinates.items() if coords == tavern_coords)
            tavern_ap_cost = self.calculate_ap_cost((current_x, current_y), tavern_coords)
            tavern_intersection = self.get_intersection_name(tavern_coords)
            self.tavern_label.setText(f"{tavern_name} - {tavern_intersection} - AP: {tavern_ap_cost}")

        if nearest_bank:
            bank_coords = nearest_bank[0][1]
            bank_ap_cost = self.calculate_ap_cost((current_x, current_y), bank_coords)
            bank_intersection = self.get_intersection_name(bank_coords)
            self.bank_label.setText(f"OmniBank - {bank_intersection} - AP: {bank_ap_cost}")

        if nearest_transit:
            transit_coords = nearest_transit[0][1]
            transit_name = next(name for name, coords in transits_coordinates.items() if coords == transit_coords)
            transit_ap_cost = self.calculate_ap_cost((current_x, current_y), transit_coords)
            transit_intersection = self.get_intersection_name(transit_coords)
            self.transit_label.setText(f"{transit_name} - {transit_intersection} - AP: {transit_ap_cost}")

        if self.destination:
            destination_coords = self.destination
            destination_ap_cost = self.calculate_ap_cost((current_x, current_y), destination_coords)
            destination_intersection = self.get_intersection_name(destination_coords)
            self.destination_label.setText(f"Destination - {destination_intersection} - AP: {destination_ap_cost}")
        else:
            self.destination_label.setText("No Destination Set")

    def get_intersection_name(self, coords):
        """
        Get the intersection name based on coordinates.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: The intersection name.
        """
        x, y = coords

        if x == 0:
            column_name = "WCL"
        elif x == 200:
            column_name = "ECL"
        else:
            x = x if x % 2 != 0 else x - 1
            column_name = next((name for name, coord in columns.items() if coord == x), "")

        if y == 0:
            row_name = "NCL"
        elif y == 200:
            row_name = "SCL"
        else:
            y = y if y % 2 != 0 else y - 1
            row_name = next((name for name, coord in rows.items() if coord == y), "")

        return f"{column_name} & {row_name}"

    # -----------------------
    # Menu Actions
    # -----------------------

    def change_theme(self):
        """
        Change the application's theme by selecting a new background color.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()};")

    def open_discord(self):
        """
        Open the Discord server in the default web browser.
        """
        webbrowser.open("https://discord.gg/ktdG9FZ")

    def show_about_dialog(self):
        """
        Show the About dialog with application details.
        """
        QMessageBox.about(self, "About RBC City Map",
                          "RBC City Map Application\n\n"
                          "Version 0.7.1\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Developement team shown in credits.\n\n")

    def show_credits_dialog(self):
        """
        Show the Credits dialog with details of the development team.
        """
        credits_text = (
            "Credits to the team who made this happen:\n\n"
            "Windows: Jonathan Lollis (Nesmuth), Justin Solivan\n\n"
            "Apple OSx Compatibility: Joseph Lemois\n\n"
            "Linux Compatibility: Josh \"Blaskewitts\" Corse, Fern Lovebond\n\n"
            "Design and Layout: Shuvi, Blair Wilson (Ikunnaprinsess)\n\n"
        )

        credits_dialog = QDialog()
        credits_dialog.setWindowTitle('Credits')
        credits_dialog.setFixedSize(600, 400)

        layout = QVBoxLayout(credits_dialog)

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("background-color: black; border: none;")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area)

        credits_label = QLabel(credits_text)
        credits_label.setStyleSheet("font-size: 18px; color: white; background-color: black;")
        credits_label.setAlignment(Qt.AlignCenter)
        credits_label.setWordWrap(True)

        scroll_area.setWidget(credits_label)

        credits_label.setGeometry(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height())

        animation = QPropertyAnimation(credits_label, b"geometry")
        animation.setDuration(30000)
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(
            QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Linear)

        animation.start()

        credits_dialog.exec_()

    def open_shops_guilds(self):
        """
        Open the Shops/Guilds dialog for the user to select a shop or guild as the destination.
        """
        dialog = ShopsGuildsDialog(self)
        if dialog.exec():
            selected_name = dialog.selected_name
            if selected_name:
                if dialog.is_shop:
                    self.set_custom_destination(shops_coordinates[selected_name])
                else:
                    self.set_custom_destination(guilds_coordinates[selected_name])

    def set_custom_destination(self, coordinates):
        """
        Set a custom destination on the minimap.

        Args:
            coordinates (tuple): Coordinates of the destination.
        """
        if coordinates:
            self.destination = coordinates
            self.save_destination()
            self.update_minimap()
            self.refresh_webview()

# -----------------------
# Theme Customization Dialog
# -----------------------

class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing the application's theme colors.
    """
    def __init__(self, parent=None, color_mappings=None):
        """
        Initialize the theme customization dialog.

        Args:
            parent (QWidget): The parent widget.
            color_mappings (dict): A dictionary of color mappings.
        """
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')

        self.setMinimumSize(400, 300)
        self.color_mappings = color_mappings if color_mappings else {}

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        self.ui_tab = QWidget()
        self.minimap_tab = QWidget()

        self.tabs.addTab(self.ui_tab, "UI, Buttons, and Text")
        self.tabs.addTab(self.minimap_tab, "Minimap Content")

        self.setup_ui_tab()
        self.setup_minimap_tab()

        button_layout = QHBoxLayout()

        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def setup_ui_tab(self):
        """
        Setup the UI tab in the theme customization dialog.
        """
        layout = QGridLayout(self.ui_tab)

        ui_elements = ['default', 'edge', 'text_color']
        for index, element in enumerate(ui_elements):
            color_square = QLabel()
            color_square.setFixedSize(20, 20)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color_mappings.get(element, QColor('white')))
            color_square.setPixmap(pixmap)

            combo_box = QComboBox()
            combo_box.addItems(self.get_color_names())
            combo_box.setCurrentText(self.color_mappings[element].name())
            combo_box.currentTextChanged.connect(lambda _, name=element: self.update_color_mapping(name))

            layout.addWidget(color_square, index, 0)
            layout.addWidget(QLabel(f"{element.capitalize()} Color:"), index, 1)
            layout.addWidget(combo_box, index, 2)

    def setup_minimap_tab(self):
        """
        Setup the Minimap Content tab in the theme customization dialog.
        """
        layout = QGridLayout(self.minimap_tab)

        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']
        for index, element in enumerate(minimap_elements):
            color_square = QLabel()
            color_square.setFixedSize(20, 20)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color_mappings.get(element, QColor('white')))
            color_square.setPixmap(pixmap)

            combo_box = QComboBox()
            combo_box.addItems(self.get_color_names())
            combo_box.setCurrentText(self.color_mappings[element].name())
            combo_box.currentTextChanged.connect(lambda _, name=element: self.update_color_mapping(name))

            layout.addWidget(color_square, index, 0)
            layout.addWidget(QLabel(f"{element.capitalize()} Color:"), index, 1)
            layout.addWidget(combo_box, index, 2)

    def update_color_mapping(self, element_name):
        """
        Update the color mapping for a specific element.

        Args:
            element_name (str): The name of the element.
        """
        selected_color = QColor(self.sender().currentText())
        self.color_mappings[element_name] = selected_color

        sender_index = self.sender().parent().layout().indexOf(self.sender())
        color_square = self.sender().parent().layout().itemAt(sender_index - 2).widget()
        pixmap = QPixmap(20, 20)
        pixmap.fill(selected_color)
        color_square.setPixmap(pixmap)

    def get_color_names(self):
        """
        Get a list of all available color names.

        Returns:
            list: List of color names.
        """
        return QColor.colorNames()

# -----------------------
# Shops/Guilds Dialog
# -----------------------

class ShopsGuildsDialog(QDialog):
    """
    Dialog for selecting a shop or guild as the destination.
    """
    def __init__(self, parent=None):
        """
        Initialize the Shops/Guilds dialog.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle('Select Shops or Guilds')
        self.setFixedSize(300, 400)

        layout = QVBoxLayout(self)

        self.is_shop = True
        self.selected_name = None

        self.shop_guild_combo = QComboBox(self)
        self.shop_guild_combo.addItems(['Shops', 'Guilds'])
        self.shop_guild_combo.currentIndexChanged.connect(self.update_list)
        layout.addWidget(self.shop_guild_combo)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()

        select_button = QPushButton('Select', self)
        select_button.clicked.connect(self.accept)
        buttons_layout.addWidget(select_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        self.update_list()

    def update_list(self):
        """
        Update the list of shops or guilds based on the selected category.
        """
        self.list_widget.clear()
        self.is_shop = self.shop_guild_combo.currentText() == 'Shops'
        items = shops_coordinates if self.is_shop else guilds_coordinates
        for name in items.keys():
            self.list_widget.addItem(QListWidgetItem(name))

    def accept(self):
        """
        Accept the dialog and set the selected shop or guild.
        """
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_name = current_item.text()
        super().accept()

# -----------------------
# Character Dialog
# -----------------------

class CharacterDialog(QDialog):
    """
    Dialog for adding or modifying a character.
    """
    def __init__(self, parent=None, character=None):
        """
        Initialize the Character dialog.

        Args:
            parent (QWidget): The parent widget.
            character (dict): The character to modify, if any.
        """
        super().__init__(parent)
        self.setWindowTitle('Character')
        self.setFixedSize(300, 150)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow('Name:', self.name_edit)
        layout.addRow('Password:', self.password_edit)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        buttons_layout = QHBoxLayout()

        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)

# -----------------------
# Data Scraping and Update
# -----------------------

def scrape_avitd_data():
    """
    Scrape data from 'A View in the Dark' and update guilds and shops data in the database.
    """
    url = "https://aviewinthedark.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

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

    print("Guilds next update text:", guilds_next_update_text)
    print("Shops next update text:", shops_next_update_text)

    guilds_next_update_time = extract_next_update_time(guilds_next_update_text)
    shops_next_update_time = extract_next_update_time(shops_next_update_text)

    update_guilds(cursor, soup, guilds_next_update_time)
    update_shops(cursor, soup, shops_next_update_time)

    connection.commit()
    connection.close()

def extract_next_update_time(text):
    """
    Extract the next update time from the provided text and calculate the next update timestamp.

    Args:
        text (str): Text containing the next update time.

    Returns:
        datetime: The calculated next update timestamp.
    """
    matches = re.findall(r'(\d+)\s*(days?|h|m|s)', text)

    days = hours = minutes = seconds = 0

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

    next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    next_update = next_update.replace(second=0, microsecond=0) + timedelta(minutes=1)
    return next_update

def update_guild(cursor, name, location, next_update_time):
    """
    Update a single guild's data in the database.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor.
        name (str): The name of the guild.
        location (str): The location of the guild.
        next_update_time (datetime): The next update time for the guild.
    """
    col, row = location.split(' and ')
    cursor.execute("""
        UPDATE guilds 
        SET `Column`=%s, `Row`=%s, next_update=%s 
        WHERE Name=%s
    """, (col, row, next_update_time, name))

def update_shop(cursor, name, location, next_update_time):
    """
    Update a single shop's data in the database.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor.
        name (str): The name of the shop.
        location (str): The location of the shop.
        next_update_time (datetime): The next update time for the shop.
    """
    col, row = location.split(' and ')
    cursor.execute("""
        UPDATE shops 
        SET `Column`=%s, `Row`=%s, next_update=%s 
        WHERE Name=%s
    """, (col, row, next_update_time, name))

def update_guilds(cursor, soup, next_update_time):
    """
    Update all guilds' data in the database using the scraped data.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor.
        soup (BeautifulSoup): The parsed HTML content of the page.
        next_update_time (datetime): The next update time for the guilds.
    """
    for name in guilds_coordinates:
        location_tag = soup.find('td', string=name)
        if location_tag:
            location = location_tag.find_next_sibling('td').text.replace('SE of ', '').strip()
            update_guild(cursor, name, location, next_update_time)
        else:
            print(f"Guild '{name}' not found in the table.")

def update_shops(cursor, soup, next_update_time):
    """
    Update all shops' data in the database using the scraped data.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor.
        soup (BeautifulSoup): The parsed HTML content of the page.
        next_update_time (datetime): The next update time for the shops.
    """
    for name in shops_coordinates:
        location_tag = soup.find('td', string=name)
        if location_tag:
            location = location_tag.find_next_sibling('td').text.replace('SE of ', '').strip()
            update_shop(cursor, name, location, next_update_time)
        else:
            print(f"Shop '{name}' not found in the table.")

# -----------------------
# Main Entry Point
# -----------------------

if __name__ == '__main__':
    setup_logging()

    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec())
