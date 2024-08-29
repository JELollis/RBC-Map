#!/usr/bin/env python3
# Filename: main_0.8.0

"""
=========================
RBC City Map Application
=========================
This application provides a comprehensive graphical interface for viewing and navigating
the city map of RavenBlack City. It includes features such as zooming in and out, setting
and saving destinations, viewing the closest points of interest, and managing user characters.
The map data is dynamically fetched from a MySQL database, with support for refreshing data
from the 'A View in the Dark' website.

Modules:
- sys: Provides access to system-specific parameters and functions.
- os: Used for interacting with the operating system (e.g., directory management).
- pickle: Facilitates the serialization and deserialization of Python objects.
- pymysql: Interface for connecting to and interacting with a MySQL database.
- requests: Allows sending HTTP requests to interact with external websites.
- re: Provides regular expression matching operations.
- datetime: Supplies classes for manipulating dates and times.
- bs4 (BeautifulSoup): Used for parsing HTML and XML documents.
- PySide6: Provides a set of Python bindings for the Qt application framework.
- sqlite3: Interface for SQLite database management.

Classes:
- CityMapApp: The main application class that initializes and manages the user interface,
  character management, web scraping, and map functionalities.
- DatabaseViewer: A utility class that displays the contents of database tables in a tabbed view.
- CharacterDialog: A dialog class for adding or modifying user characters.
- ThemeCustomizationDialog: A dialog class for customizing the application theme.
- SetDestinationDialog: A dialog class for setting a destination on the map.
- AVITDScraper: A scraper class that fetches data from 'A View in the Dark' to update guilds
  and shops data in the database.

Functions:
- connect_to_database: Establishes a connection to the MySQL database and handles connection errors.
- load_data: Loads various map data from the database, including coordinates for banks, taverns, transits,
  user buildings, shops, guilds, and places of interest.
- initialize_cookie_db: Sets up an SQLite database for storing cookies.
- save_cookie_to_db: Saves individual cookies to the SQLite database.
- load_cookies_from_db: Loads cookies from the SQLite database into the web engine.
- clear_cookie_db: Clears all cookies from the SQLite database.
- fetch_table_data: Retrieves and returns the column names and data from a specified database table.
- extract_coordinates_from_html: Extracts map coordinates from the loaded HTML content.
- find_nearest_location: Finds the nearest point of interest based on a given set of coordinates.
- calculate_ap_cost: Calculates the Action Point (AP) cost between two map coordinates.
- update_guilds: Updates the guilds data in the MySQL database using scraped data.
- update_shops: Updates the shops data in the MySQL database using scraped data.
- get_next_update_times: Retrieves the next update times for guilds and shops from the MySQL database.
- inject_console_logging: Injects JavaScript into the web page to capture and log console messages.
- apply_theme: Applies the currently selected theme to the application UI.
- save_theme_settings: Saves the customized theme settings to a file.
- load_theme_settings: Loads the saved theme settings from a file or database.
- show_about_dialog: Displays the 'About' dialog with information about the application.
- show_credits_dialog: Displays the 'Credits' dialog with information about contributors.

To install all required modules, run the following command:
 pip install pymysql requests bs4 PySide6 PySide6-WebEngine
"""

# -----------------------
# Imports Handling
# -----------------------
import sys
import importlib.util
import os

# List of required modules
required_modules = [
    'pickle', 'pymysql', 'requests', 're', 'time', 'sqlite3',
    'webbrowser', 'datetime', 'bs4', 'PySide6.QtWidgets',
    'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtNetwork'
]

def check_required_modules(modules):
    """
    Check if all required modules are installed.

    Args:
        modules (list): List of module names as strings.

    Returns:
        bool: True if all modules are installed, False otherwise.
    """
    missing_modules = []
    for module in modules:
        if importlib.util.find_spec(module) is None:
            missing_modules.append(module)

    if missing_modules:
        print("The following modules are missing:")
        for mod in missing_modules:
            print(f"- {mod}")
        print("\nYou can install them with:")
        print("pip install pymysql requests bs4 PySide6 PySide6-WebEngine")
        return False
    return True

# Check for required modules
if not check_required_modules(required_modules):
    sys.exit("Missing required modules. Please install them and try again.")

# Proceed with the rest of the imports and program setup
import logging
import pickle
import pymysql
import requests
import re
import webbrowser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QColorDialog, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction
from PySide6.QtCore import QUrl, Qt, QRect, QEasingCurve, QPropertyAnimation, QSize, QTimer, QDateTime
from PySide6.QtCore import Slot as pyqtSlot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtNetwork import QNetworkCookie
import sqlite3

# -----------------------
# Directory setup
# -----------------------

def ensure_directories_exist():
    """
    Ensure that the required directories exist. If they don't, create them.
    """
    required_dirs = ['logs', 'sessions', 'settings', 'images']
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
    log_filename = datetime.now().strftime('./logs/rbc_%Y-%m-%d.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filename,
        filemode='a'  # Append to the log file if it exists
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
        tuple: Contains columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates
    """
    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

    # Fetch columns
    cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
    columns_data = cursor.fetchall()
    columns = {name: int(coordinate) for name, coordinate in columns_data}

    # Fetch rows
    cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
    rows_data = cursor.fetchall()
    rows = {name: int(coordinate) for name, coordinate in rows_data}

    # Fetch coordinates from banks table with column and row names
    cursor.execute("SELECT `Column`, `Row` FROM banks")
    banks_data = cursor.fetchall()
    banks_coordinates = [
        (col, row, None, None)
        for col, row in banks_data
    ]

    # Fetch taverns
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM taverns")
    taverns_data = cursor.fetchall()
    taverns_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in taverns_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch transits
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM transits")
    transits_data = cursor.fetchall()
    transits_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in transits_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch user buildings
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM userbuildings")
    user_buildings_data = cursor.fetchall()
    user_buildings_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in user_buildings_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch color mappings
    cursor.execute("SELECT `Type`, `Color` FROM color_mappings")
    color_mappings_data = cursor.fetchall()
    color_mappings = {type_: QColor(color) for type_, color in color_mappings_data}

    # Fetch shops
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM shops")
    shops_data = cursor.fetchall()
    shops_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in shops_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch guilds
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM guilds")
    guilds_data = cursor.fetchall()
    guilds_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in guilds_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch places of interest
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM placesofinterest")
    places_of_interest_data = cursor.fetchall()
    places_of_interest_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in places_of_interest_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    connection.close()

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates

# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()

# -----------------------
# SQLite Cookie Storage Setup
# -----------------------

COOKIE_DB_PATH = './sessions/cookies.db'

def initialize_cookie_db():
    """
    Initialize the SQLite database for storing cookies.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cookies (
            name TEXT,
            value TEXT,
            domain TEXT,
            path TEXT,
            expiry TEXT,
            secure INTEGER,
            httponly INTEGER
        )
    ''')
    connection.commit()
    connection.close()

def save_cookie_to_db(cookie):
    """
    Save a single cookie to the SQLite database.

    Args:
        cookie (QNetworkCookie): The cookie to save.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO cookies (name, value, domain, path, expiry, secure, httponly)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        cookie.name().data().decode('utf-8'),
        cookie.value().data().decode('utf-8'),
        cookie.domain(),
        cookie.path(),
        cookie.expirationDate().toString() if not cookie.isSessionCookie() else None,
        int(cookie.isSecure()),
        int(cookie.isHttpOnly())
    ))
    connection.commit()
    connection.close()

def load_cookies_from_db():
    """
    Load all cookies from the SQLite database.

    Returns:
        list: A list of QNetworkCookie objects.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT name, value, domain, path, expiry, secure, httponly FROM cookies')
    rows = cursor.fetchall()
    cookies = []
    for row in rows:
        cookie = QNetworkCookie(
            name=row[0].encode('utf-8'),
            value=row[1].encode('utf-8')
        )
        cookie.setDomain(row[2])
        cookie.setPath(row[3])

        if row[4]:
            cookie.setExpirationDate(QDateTime.fromString(row[4]))
        cookie.setSecure(bool(row[5]))
        cookie.setHttpOnly(bool(row[6]))
        cookies.append(cookie)
    connection.close()
    return cookies

def clear_cookie_db():
    """
    Clear all cookies from the SQLite database.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM cookies')
    connection.commit()
    connection.close()

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

        self.scraper = AVITDScraper()
        self.scraper.scrape_guilds_and_shops()

        self.setWindowIcon(QIcon('./images/favicon.ico'))
        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        # Apply saved theme settings
        self.load_theme_settings()
        self.apply_theme()

        # Create a QWebEngineProfile for handling cookies
        self.web_profile = QWebEngineProfile.defaultProfile()

        # Enable persistent cookies and set the storage path
        cookie_storage_path = os.path.join(os.getcwd(), 'sessions')
        os.makedirs(cookie_storage_path, exist_ok=True)
        self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.web_profile.setPersistentStoragePath(cookie_storage_path)

        # Set up cookie handling and logging
        self.setup_cookie_handling()

        # Load the data
        self.columns, self.rows, self.banks_coordinates, self.taverns_coordinates, self.transits_coordinates, self.user_buildings_coordinates, self.color_mappings, self.shops_coordinates, self.guilds_coordinates, self.places_of_interest_coordinates = load_data()

        # Set up the UI components
        self.zoom_level = 3
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.color_mappings = color_mappings

        # Initialize characters list and character_list widget early to avoid attribute errors
        self.characters = []
        self.character_list = QListWidget()
        self.selected_character = None
        self.webview_loaded = False  # To prevent multiple loadFinished events

        self.load_characters()

        if not self.characters:
            self.add_new_character()
            if not self.characters:
                # Exit if no characters are added
                sys.exit("No characters added. Exiting the application.")

        self.load_last_active_character()  # Load the last active character

        self.load_destination()
        self.setup_ui()
        self.setup_console_logging()
        self.show()
        self.update_minimap()

    # -----------------------
    # Load and apply customized UI Theme
    # -----------------------

    def load_theme_settings(self):
        """
        Load the theme settings from a file or default to the color_mappings database entry.
        """
        settings_file = './settings/theme_settings.pkl'

        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'rb') as f:
                    self.color_mappings = pickle.load(f)
            except (EOFError, pickle.UnpicklingError) as e:
                logging.error(f"Failed to load theme settings from file: {e}")
                self.color_mappings = {}
        else:
            # Fallback to the database color_mappings
            connection = connect_to_database()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("SELECT `Type`, `Color` FROM color_mappings")
                    color_mappings_data = cursor.fetchall()
                    self.color_mappings = {type_: QColor(color) for type_, color in color_mappings_data}
                except pymysql.MySQLError as e:
                    logging.error(f"Failed to load color mappings from database: {e}")
                    self.color_mappings = {}
                finally:
                    connection.close()
            else:
                self.color_mappings = {}  # Default to an empty dict if no database entry is found

    def save_theme_settings(self):
        """
        Save the theme settings to a file.
        """
        settings_file = './settings/theme_settings.pkl'
        with open(settings_file, 'wb') as f:
            pickle.dump(self.color_mappings, f)

    def apply_theme(self):
        """
        Apply the theme settings to the application.
        """
        # Apply background color
        background_color = self.color_mappings.get('background', QColor('white')).name()

        # Apply text color
        text_color = self.color_mappings.get('text_color', QColor('black')).name()

        # Apply button color
        button_color = self.color_mappings.get('button_color', QColor('lightgrey')).name()

        # Apply styles to the entire application
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QMenuBar {{
                background-color: {background_color};
                color: {text_color};
            }}
            QMenuBar::item {{
                background-color: {background_color};
                color: {text_color};
            }}
            QMenu {{
                background-color: {background_color};
                color: {text_color};
            }}
            QMenu::item {{
                background-color: {background_color};
                color: {text_color};
            }}
            """
        )

    def change_theme(self):
        """
        Open the theme customization dialog and apply the selected theme.
        """
        dialog = ThemeCustomizationDialog(self, color_mappings=self.color_mappings)
        if dialog.exec():
            self.color_mappings = dialog.color_mappings
            self.apply_theme()
            self.save_theme_settings()

    # -----------------------
    # Cookie Handling
    # -----------------------

    def setup_cookie_handling(self):
        """
        Set up cookie handling including loading and saving cookies.
        """
        initialize_cookie_db()
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        self.load_cookies()

    def load_cookies(self):
        """
        Load cookies from the SQLite database.
        """
        cookies = load_cookies_from_db()
        for cookie in cookies:
            self.cookie_store.setCookie(cookie, QUrl("https://quiz.ravenblack.net"))
        logging.info("Cookies loaded from SQLite database.")

    def on_cookie_added(self, cookie):
        """
        Handle the event when a new cookie is added, ensuring no duplicates are stored.
        """
        # Prevent adding duplicate cookies
        connection = sqlite3.connect(COOKIE_DB_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM cookies 
            WHERE name = ? AND domain = ? AND path = ?
        ''', (
            cookie.name().data().decode('utf-8'),
            cookie.domain(),
            cookie.path()
        ))
        result = cursor.fetchone()

        if result[0] == 0:
            save_cookie_to_db(cookie)
            logging.debug(
                f"Cookie added: {cookie.name().data().decode('utf-8')} = {cookie.value().data().decode('utf-8')}")
        else:
            logging.debug(
                f"Duplicate cookie ignored: {cookie.name().data().decode('utf-8')} = {cookie.value().data().decode('utf-8')}")

        connection.close()

    # -----------------------
    # CityMapApp UI Set Up
    # -----------------------

    def setup_ui(self):
        """
        Set up the main user interface for the application.
        """

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.create_menu_bar()

        # Initialize the QWebEngineView before setting up the browser controls
        self.website_frame = QWebEngineView(self.web_profile)
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)

        # Create the browser controls layout at the top of the webview
        self.browser_controls_layout = QHBoxLayout()

        # Load images for back, forward, and refresh buttons
        back_button = QPushButton()
        back_button.setIcon(QIcon('./images/back.png'))
        back_button.setIconSize(QSize(30, 30))
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet("background-color: transparent; border: none;")
        back_button.clicked.connect(self.website_frame.back)
        self.browser_controls_layout.addWidget(back_button)

        forward_button = QPushButton()
        forward_button.setIcon(QIcon('./images/forward.png'))
        forward_button.setIconSize(QSize(30, 30))
        forward_button.setFixedSize(30, 30)
        forward_button.setStyleSheet("background-color: transparent; border: none;")
        forward_button.clicked.connect(self.website_frame.forward)
        self.browser_controls_layout.addWidget(forward_button)

        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon('./images/refresh.png'))
        refresh_button.setIconSize(QSize(30, 30))
        refresh_button.setFixedSize(30, 30)
        refresh_button.setStyleSheet("background-color: transparent; border: none;")
        refresh_button.clicked.connect(self.website_frame.reload)
        self.browser_controls_layout.addWidget(refresh_button)

        # Set spacing between buttons to make them closer together
        self.browser_controls_layout.setSpacing(5)
        self.browser_controls_layout.addStretch(1)

        # Create a container widget for the webview and controls
        webview_container = QWidget()
        webview_layout = QVBoxLayout(webview_container)
        webview_layout.setContentsMargins(0, 0, 0, 0)
        webview_layout.addLayout(self.browser_controls_layout)
        webview_layout.addWidget(self.website_frame)

        # Main layout for map and controls
        map_layout = QHBoxLayout()
        main_layout.addLayout(map_layout)

        # Left layout containing the minimap and control buttons
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

        # Label to display the minimap
        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Information frame to display closest locations and AP costs
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setFixedHeight(80)
        info_layout = QVBoxLayout()
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Labels to display closest locations and destination
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
        set_destination_button.clicked.connect(self.open_set_destination_dialog)
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
        website_button.clicked.connect(self.open_website)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        # Character list frame
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Shape.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        self.character_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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

        # Add the webview_container and left_frame to the map layout
        map_layout.addWidget(left_frame)
        map_layout.addWidget(webview_container, stretch=1)

        # Make sure the webview expands to fill the remaining space
        self.website_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.show()
        self.update_minimap()

    def go_back(self):
        self.website_frame.back()

    def go_forward(self):
        self.website_frame.forward()

    def refresh_page(self):
        self.website_frame.reload()

    def create_menu_bar(self):
        """
        Create the menu bar with File, Settings, Tools, and Help menus.
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

        # Tools menu
        tools_menu = menu_bar.addMenu('Tools')

        # Database Viewer Tool
        database_viewer_action = QAction('Database Viewer', self)
        database_viewer_action.triggered.connect(self.open_database_viewer)
        tools_menu.addAction(database_viewer_action)

        # Shopping List Tool
        shopping_list_action = QAction('Shopping List Generator', self)
        shopping_list_action.triggered.connect(self.open_shopping_list_tool)
        tools_menu.addAction(shopping_list_action)

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

        # -----------------------
        # Error Logging
        # -----------------------

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
    # Menu Control Items
    # -----------------------

    def save_webpage_screenshot(self):
        """
        Save the current webpage as a screenshot.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Webpage Screenshot", "",
                                                   "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.website_frame.grab().save(file_name)

    def save_app_screenshot(self):
        """
        Save the current application window as a screenshot.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save App Screenshot", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.grab().save(file_name)

    def open_shopping_list_tool(self):
        """
        Opens the Shopping List Tool window.
        """
        self.shopping_list_tool = ShoppingListTool()
        self.shopping_list_tool.show()
        
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
            logging.error(f"An unexpected error occurred while loading characters: {e}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")
            self.characters = []

    def save_characters(self):
        """
        Save characters to a pickle file in the 'sessions' directory.
        """
        try:
            os.makedirs('sessions', exist_ok=True)
            with open('./sessions/characters.pkl', 'wb') as f:
                pickle.dump(self.characters, f)
                logging.debug("Characters saved successfully to file.")
        except Exception as e:
            logging.error(f"Failed to save characters: {e}")

    def on_character_selected(self, item):
        """
        Handle character selection from the list.

        Args:
            item (QListWidgetItem): The selected item in the list.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)
        if selected_character:
            logging.debug(f"Selected character: {character_name}")
            self.selected_character = selected_character
            self.save_last_active_character()
            self.logout_current_character()
            QTimer.singleShot(1000, self.login_selected_character)

    def logout_current_character(self):
        """
        Logout the current character.
        """
        logging.debug("Logging out current character.")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))

        # Delay login to allow logout to complete
        QTimer.singleShot(1000, self.login_selected_character)

    def login_selected_character(self):
        """
        Log in the selected character after logging out the current one.
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
        Add a new character.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)
        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()
            self.characters.append({'name': name, 'password': password})
            self.save_characters()
            self.character_list.addItem(QListWidgetItem(name))
            logging.debug(f"Character {name} added.")

    def modify_character(self):
        """
        Modify the selected character.
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
            if dialog.exec():
                character['name'] = dialog.name_edit.text()
                character['password'] = dialog.password_edit.text()
                self.save_characters()
                current_item.setText(character['name'])
                logging.debug(f"Character {name} modified.")

    def delete_character(self):
        """
        Delete the selected character.
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

    def save_last_active_character(self):
        """
        Save the last active character to a file.
        """
        try:
            with open('./sessions/last_active_character.pkl', 'wb') as f:
                pickle.dump(self.selected_character, f)
                logging.debug("Last active character saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save last active character: {e}")

    def load_last_active_character(self):
        """
        Load the last active character from a file and log in automatically.
        """
        try:
            with open('./sessions/last_active_character.pkl', 'rb') as f:
                self.selected_character = pickle.load(f)
                logging.debug(f"Last active character loaded: {self.selected_character['name']}")
                self.login_selected_character()
        except FileNotFoundError:
            logging.warning("Last active character file not found. No character loaded.")
        except Exception as e:
            logging.error(f"Failed to load last active character: {e}")

    # -----------------------
    # Web View Handling
    # -----------------------

    def on_webview_load_finished(self, success):
        """
        Handle the event when the webview finishes loading.
        """
        if not success:
            logging.error("Failed to load the webpage.")
            QMessageBox.critical(self, "Error",
                                 "Failed to load the webpage. Please check your network connection or try again later.")
        else:
            logging.info("Webpage loaded successfully.")
            # Process the HTML if needed
            self.website_frame.page().toHtml(self.process_html)

    def process_html(self, html):
        """
        Process the HTML content of the webview to extract coordinates and update the minimap.

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
        self.website_frame.reload()

    # -----------------------
    # Minimap Drawing and Update
    # -----------------------

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
            # Adjust coordinates for WCL (column 0) and NCL (row 0)
            if column_index != 0 and row_index != 0:
                column_index += 1
                row_index += 1

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

        # Update the part where banks and other locations are drawn
        for (col_name, row_name, _, _) in self.banks_coordinates:
            column_index = self.columns.get(col_name)
            row_index = self.rows.get(row_name)
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing bank at {col_name} & {row_name} with coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["bank"], "Bank")
            else:
                logging.warning(f"Skipping bank at {col_name} & {row_name} due to missing coordinates")

        # Draw the grid
        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                column_index = self.column_start + j
                row_index = self.row_start + i

                x0, y0 = j * block_size, i * block_size

                # Draw the cell background
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                column_name = next((name for name, coord in self.columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in self.rows.items() if coord == row_index), None)

                # Draw cell background color
                if column_index < min(self.columns.values()) or column_index > max(
                        self.columns.values()) or row_index < min(
                        self.rows.values()) or row_index > max(self.rows.values()):
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

        # Draw special locations (banks with correct offsets)
        for (col_name, row_name, _, _) in self.banks_coordinates:
            column_index = self.columns.get(col_name)
            row_index = self.rows.get(row_name)
            if column_index is not None and row_index is not None:
                # Only adjust for positive columns
                if column_index > 0:
                    adjusted_column_index = column_index + 1
                else:
                    adjusted_column_index = column_index  # No adjustment for column = 0 (WCL)

                adjusted_row_index = row_index + 1
                logging.debug(
                    f"Drawing bank at {col_name} & {row_name} with coordinates ({adjusted_column_index}, {adjusted_row_index})"
                )
                draw_location(adjusted_column_index, adjusted_row_index, self.color_mappings["bank"], "Bank")

        # Draw other locations as before
        for name, (column_index, row_index) in self.taverns_coordinates.items():
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing tavern '{name}' at coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["tavern"], name)
            else:
                logging.warning(f"Skipping tavern '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.transits_coordinates.items():
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing transit '{name}' at coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["transit"], name)
            else:
                logging.warning(f"Skipping transit '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.user_buildings_coordinates.items():
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing user building '{name}' at coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["user_building"], name)
            else:
                logging.warning(f"Skipping user building '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.shops_coordinates.items():
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing shop '{name}' at coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["shop"], name)
            else:
                logging.warning(f"Skipping shop '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing guild '{name}' at coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["guild"], name)
            else:
                logging.warning(f"Skipping guild '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                logging.debug(f"Drawing place of interest '{name}' at coordinates ({column_index}, {row_index})")
                draw_location(column_index, row_index, self.color_mappings["placesofinterest"], name)
            else:
                logging.warning(f"Skipping place of interest '{name}' due to missing coordinates")

        # Get current location
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find and draw lines to nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        # Draw nearest tavern line
        if nearest_tavern:
            nearest_tavern_coords = nearest_tavern[0][1]
            logging.debug(
                f"Drawing line to nearest tavern at coordinates ({nearest_tavern_coords[0]}, {nearest_tavern_coords[1]})")
            tavern_x = nearest_tavern_coords[0] if nearest_tavern_coords[0] == 0 else nearest_tavern_coords[0] + 1
            tavern_y = nearest_tavern_coords[1] if nearest_tavern_coords[1] == 0 else nearest_tavern_coords[1] + 1
            painter.setPen(QPen(QColor('orange'), 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (tavern_x - self.column_start) * block_size + block_size // 2,
                (tavern_y - self.row_start) * block_size + block_size // 2
            )

        # Draw nearest bank line
        if nearest_bank:
            nearest_bank_coords = nearest_bank[0][1]
            logging.debug(
                f"Drawing line to nearest bank at coordinates ({nearest_bank_coords[0]}, {nearest_bank_coords[1]})")
            bank_x = nearest_bank_coords[0] if nearest_bank_coords[0] == 0 else nearest_bank_coords[0] + 1
            bank_y = nearest_bank_coords[1] if nearest_bank_coords[1] == 0 else nearest_bank_coords[1] + 1
            painter.setPen(QPen(QColor('blue'), 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (bank_x - self.column_start) * block_size + block_size // 2,
                (bank_y - self.row_start) * block_size + block_size // 2
            )

        # Draw nearest transit line
        if nearest_transit:
            nearest_transit_coords = nearest_transit[0][1]
            logging.debug(
                f"Drawing line to nearest transit at coordinates ({nearest_transit_coords[0]}, {nearest_transit_coords[1]})")
            transit_x = nearest_transit_coords[0] if nearest_transit_coords[0] == 0 else nearest_transit_coords[0] + 1
            transit_y = nearest_transit_coords[1] if nearest_transit_coords[1] == 0 else nearest_transit_coords[1] + 1
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (transit_x - self.column_start) * block_size + block_size // 2,
                (transit_y - self.row_start) * block_size + block_size // 2
            )

        # Draw destination line
        if self.destination:
            logging.debug(f"Drawing line to destination at coordinates ({self.destination[0]}, {self.destination[1]})")
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
        valid_banks = []
        for col, row, _, _ in self.banks_coordinates:
            try:
                col_index = self.columns[col]
                row_index = self.rows[row]
            except KeyError:
                logging.warning(
                    f"Bank location with column '{col}' and row '{row}' could not be found in the available columns or rows.")
                continue
            valid_banks.append((col_index, row_index))

        if not valid_banks:
            logging.warning("No valid bank locations found.")
            return None

        return self.find_nearest_location(x, y, valid_banks)

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
        self.refresh_webview()

    def save_destination(self):
        """
        Save the destination to a file.
        """
        with open('./sessions/destination.pkl', 'wb') as f:
            pickle.dump(self.destination, f)
            pickle.dump(datetime.now(), f)

    def load_destination(self):
        """
        Load the destination from a file.
        """
        try:
            with open('./sessions/destination.pkl', 'rb') as f:
                self.destination = pickle.load(f)
                self.scrape_timestamp = pickle.load(f)
        except (FileNotFoundError, EOFError):
            logging.warning("Destination file not found or is empty. Setting defaults.")
            self.destination = None
            self.scrape_timestamp = datetime.min

    # -----------------------
    # Minimap Controls
    # -----------------------

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

    def open_set_destination_dialog(self):
        dialog = set_destination_dialog(self)
        if dialog.exec():
            self.load_destination()
            self.update_minimap()

    def mousePressEvent(self, event):
        """
        Handle mouse press event to update the minimap location.

        Args:
            event (QMouseEvent): Mouse event.
        """
        if event.position().x() < self.minimap_label.width() and event.position().y() < self.minimap_label.height():
            x = event.position().x()
            y = event.position().y()

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

    # -----------------------
    # Infobar Management
    # -----------------------

    def calculate_ap_cost(self, start, end):
        """
        Calculate the AP cost of moving from start to end using the Chebyshev distance.

        Args:
            start (tuple): Starting coordinates (x, y).
            end (tuple): Ending coordinates (x, y).

        Returns:
            int: AP cost of moving from start to end.
        """
        return max(abs(start[0] - end[0]), abs(start[1] - end[1]))

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
            tavern_name = next(name for name, coords in self.taverns_coordinates.items() if coords == tavern_coords)
            tavern_ap_cost = self.calculate_ap_cost((current_x, current_y), tavern_coords)
            tavern_intersection = self.get_intersection_name(tavern_coords)
            self.tavern_label.setText(f"{tavern_name} - {tavern_intersection} - AP: {tavern_ap_cost}")

        # Get details for nearest bank
        if nearest_bank:
            bank_coords = nearest_bank[0][1]
            adjusted_bank_coords = (bank_coords[0] + 1, bank_coords[1] + 1)
            bank_ap_cost = self.calculate_ap_cost((current_x, current_y), adjusted_bank_coords)
            bank_intersection = self.get_intersection_name(adjusted_bank_coords)
            self.bank_label.setText(f"OmniBank - {bank_intersection} - AP: {bank_ap_cost}")

        # Get details for nearest transit
        if nearest_transit:
            transit_coords = nearest_transit[0][1]
            transit_name = next(name for name, coords in self.transits_coordinates.items() if coords == transit_coords)
            transit_ap_cost = self.calculate_ap_cost((current_x, current_y), transit_coords)
            transit_intersection = self.get_intersection_name(transit_coords)
            self.transit_label.setText(f"{transit_name} - {transit_intersection} - AP: {transit_ap_cost}")

        # Get details for set destination
        if self.destination:
            destination_coords = self.destination
            destination_ap_cost = self.calculate_ap_cost((current_x, current_y), destination_coords)
            destination_intersection = self.get_intersection_name(destination_coords)
            self.destination_label.setText(f"Destination - {destination_intersection} - AP: {destination_ap_cost}")
        else:
            self.destination_label.setText("No Destination Set")

    def get_intersection_name(self, coords):
        """
        Get the intersection name for the given coordinates, including special cases for map edges.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: Intersection name.
        """
        x, y = coords

        # Special cases for edges of the map
        if x <= min(self.columns.values()) - 1:
            column_name = "Edge of Map"
        else:
            column_name = next((name for name, coord in self.columns.items() if coord == x - 1), "Edge of Map")

        if y <= min(self.rows.values()) - 1:
            row_name = "Edge of Map"
        else:
            row_name = next((name for name, coord in self.rows.items() if coord == y - 1), "Edge of Map")

        if column_name == "Edge of Map" or row_name == "Edge of Map":
            return "Edge of Map"
        else:
            return f"{column_name} & {row_name}"

    # -----------------------
    # Menu Actions
    # -----------------------

    def open_discord(self):
        """
        Open the RBC Discord invite link.
        """
        webbrowser.open('https://discord.gg/nwEa8FaTDS')

    def open_website(self):
        """
        Open the RBC Website in the system default browser.
        """
        webbrowser.open('https://lollis-home.ddns.net/viewpage.php?page_id=1')

    def show_about_dialog(self):
        """
        Show the About dialog with application details.
        """
        QMessageBox.about(self, "About RBC City Map",
                          "RBC City Map Application\n\n"
                          "Version 0.7.1\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Development team shown in credits.\n\n")

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
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area)

        credits_label = QLabel(credits_text)
        credits_label.setStyleSheet("font-size: 18px; color: white; background-color: black;")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setWordWrap(True)

        scroll_area.setWidget(credits_label)

        credits_label.setGeometry(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height())

        animation = QPropertyAnimation(credits_label, b"geometry")
        animation.setDuration(30000)
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(
            QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        animation.start()

        credits_dialog.exec()



    def open_database_viewer(self):
        """
        Open the database viewer.
        """
        # Initialize tables data
        connection = connect_to_database()
        if not connection:
            QMessageBox.critical(self, "Error", "Failed to connect to the database.")
            return

        cursor = connection.cursor()

        # Specify the tables to fetch
        tables_to_fetch = ['columns', 'rows', 'banks', 'taverns', 'transits', 'userbuildings', 'shops', 'guilds',
                           'placesofinterest']
        tables_data = {}

        for table_name in tables_to_fetch:
            column_names, data = self.fetch_table_data(cursor, table_name)
            tables_data[table_name] = (column_names, data)

        cursor.close()
        connection.close()

        # Show the database viewer
        self.database_viewer = DatabaseViewer(tables_data)
        self.database_viewer.show()

    def fetch_table_data(self, cursor, table_name):
        """
        Fetch data from the specified table and return it as a list of tuples, including column names.

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


# -----------------------
# Database Viewer Class
# -----------------------

class DatabaseViewer(QMainWindow):
    """
    Main application class for viewing database tables.
    """

    def __init__(self, tables_data):
        """
        Initialize the DatabaseViewer with table data.
        """
        super().__init__()
        self.setWindowTitle('MySQL Database Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        for table_name, (column_names, data) in tables_data.items():
            self.add_table_tab(table_name, column_names, data)

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

# -----------------------
# Character Dialog Class
# -----------------------

class CharacterDialog(QDialog):
    """
    A dialog for adding or modifying a character.
    """

    def __init__(self, parent=None, character=None):
        """
        Initialize the character dialog.

        Args:
            parent (QWidget): Parent widget.
            character (dict, optional): Character dictionary to modify. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Character")

        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)

        layout.addRow(button_box)
        self.setLayout(layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

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
        Set up the UI tab in the theme customization dialog.
        """
        layout = QGridLayout(self.ui_tab)

        ui_elements = ['background', 'text_color', 'button_color']
        for index, element in enumerate(ui_elements):
            color_square = QLabel()
            color_square.setFixedSize(20, 20)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color_mappings.get(element, QColor('white')))
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color')
            color_button.clicked.connect(lambda _, el=element, sq=color_square: self.change_color(el, sq))

            layout.addWidget(QLabel(f"{element.replace('_', ' ').capitalize()}:"), index, 0)
            layout.addWidget(color_square, index, 1)
            layout.addWidget(color_button, index, 2)

    def setup_minimap_tab(self):
        """
        Set up the Minimap Content tab in the theme customization dialog.
        """
        layout = QGridLayout(self.minimap_tab)

        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']
        for index, element in enumerate(minimap_elements):
            color_square = QLabel()
            color_square.setFixedSize(20, 20)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color_mappings.get(element, QColor('white')))
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color')
            color_button.clicked.connect(lambda _, el=element, sq=color_square: self.change_color(el, sq))

            layout.addWidget(QLabel(f"{element.capitalize()}:"), index, 0)
            layout.addWidget(color_square, index, 1)
            layout.addWidget(color_button, index, 2)

    def change_color(self, element_name, color_square):
        """
        Open a color dialog to change the color of the specified element.

        Args:
            element_name (str): The name of the element.
            color_square (QLabel): The QLabel that shows the current color.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_mappings[element_name] = color
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

    def apply_theme(self):
        """
        Apply the theme settings to the application.
        """
        # Apply background color
        background_color = self.color_mappings.get('background', QColor('white'))
        self.setStyleSheet(f"background-color: {background_color.name()};")

        # Apply text and button colors
        text_color = self.color_mappings.get('text_color', QColor('black')).name()
        button_color = self.color_mappings.get('button_color', QColor('lightgrey')).name()
        self.setStyleSheet(
            f"QWidget {{ background-color: {background_color.name()}; }}"
            f"QPushButton {{ background-color: {button_color}; color: {text_color}; }}"
            f"QLabel {{ color: {text_color}; }}"
        )

# -----------------------
# AVITD Scraper Class
# -----------------------

class AVITDScraper:
    """
    A scraper class for 'A View in the Dark' to update guilds and shops data in the database.
    """

    def __init__(self):
        """
        Initialize the scraper with required headers and database connection.
        """
        self.url = "https://aviewinthedark.net/"
        self.connection = connect_to_database()  # Using the global connect_to_database method
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("AVITDScraper initialized.")

    def scrape_guilds_and_shops(self):
        """
        Scrape the guilds and shops data from the website and update the database.
        """
        logging.info("Starting to scrape guilds and shops.")
        response = requests.get(self.url, headers=self.headers)
        logging.debug(f"Received response: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        guilds = self.scrape_section(soup, "the guilds")
        shops = self.scrape_section(soup, "the shops")
        guilds_next_update = self.extract_next_update_time(soup, 'Guilds')
        shops_next_update = self.extract_next_update_time(soup, 'Shops')

        # Display results in the console (for debugging purposes)
        self.display_results(guilds, shops, guilds_next_update, shops_next_update)

        # Update the database with scraped data
        self.update_database(guilds, "guilds", guilds_next_update)
        self.update_database(shops, "shops", shops_next_update)
        logging.info("Finished scraping and updating the database.")

    def scrape_section(self, soup, section_image_alt):
        """
        Scrape a specific section (guilds or shops) from the website.
        """
        logging.debug(f"Scraping section: {section_image_alt}")
        data = []
        section_image = soup.find('img', alt=section_image_alt)
        if not section_image:
            logging.warning(f"No data found for {section_image_alt}.")
            return data

        table = section_image.find_next('table')
        rows = table.find_all('tr', class_=['odd', 'even'])

        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 2:
                logging.debug(f"Skipping row due to insufficient columns: {row}")
                continue

            name = columns[0].text.strip()
            location = columns[1].text.strip().replace("SE of ", "").strip()

            try:
                column, row = location.split(" and ")
                data.append((name, column, row))
                logging.debug(f"Extracted data - Name: {name}, Column: {column}, Row: {row}")
            except ValueError:
                logging.warning(f"Location format unexpected for {name}: {location}")

        logging.info(f"Scraped {len(data)} entries from {section_image_alt}.")
        return data

    def extract_next_update_time(self, soup, section_name):
        """
        Extract the next update time for a specific section (guilds or shops).
        """
        logging.debug(f"Extracting next update time for section: {section_name}")
        section_divs = soup.find_all('div', class_='next_change')
        for div in section_divs:
            if section_name in div.text:
                match = re.search(r'(\d+)\s+days?,\s+(\d+)h\s+(\d+)m\s+(\d+)s', div.text)
                if match:
                    days = int(match.group(1))
                    hours = int(match.group(2))
                    minutes = int(match.group(3))
                    seconds = int(match.group(4))
                    next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                    logging.debug(f"Next update time for {section_name}: {next_update}")
                    return next_update.strftime('%Y-%m-%d %H:%M:%S')
        logging.warning(f"No next update time found for {section_name}.")
        return 'NA'

    def display_results(self, guilds, shops, guilds_next_update, shops_next_update):
        """
        Display the results of the scraping in the console for debugging purposes.
        """
        logging.info(f"Guilds Next Update: {guilds_next_update}")
        logging.info(f"Shops Next Update: {shops_next_update}")

        logging.info("Guilds Data:")
        for guild in guilds:
            logging.info(f"Name: {guild[0]}, Column: {guild[1]}, Row: {guild[2]}")

        logging.info("Shops Data:")
        for shop in shops:
            logging.info(f"Name: {shop[0]}, Column: {shop[1]}, Row: {shop[2]}")

    def update_database(self, data, table, next_update):
        """
        Update the database with the scraped data.
        """
        if not self.connection:
            logging.error("Failed to connect to the database.")
            return

        cursor = self.connection.cursor()
        for name, column, row in data:
            try:
                logging.debug(f"Updating {table} entry: Name={name}, Column={column}, Row={row}, Next Update={next_update}")
                cursor.execute(
                    f"UPDATE {table} SET `Column`=%s, `Row`=%s, `next_update`=%s WHERE `Name`=%s",
                    (column, row, next_update, name)
                )
            except pymysql.MySQLError as e:
                logging.error(f"Failed to update {table} entry '{name}': {e}")

        self.connection.commit()
        cursor.close()
        logging.info(f"Database updated for {table}.")

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")

# -----------------------
# Tools
# -----------------------

class set_destination_dialog(QDialog):
    """
    A dialog for setting a destination on the map.
    """

    def __init__(self, parent=None):
        """
        Initialize the set destination dialog.

        Args:
            parent (QWidget): Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Set Destination")
        self.resize(200, 200)

        # Store the parent reference to access its methods
        self.parent = parent

        # Set up the main layout for the dialog
        main_layout = QVBoxLayout(self)

        # Comboboxes to select destinations
        dropdown_layout = QFormLayout()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()

        # Populate dropdowns with values from the database
        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

        custom_location_layout = QHBoxLayout()
        self.columns_dropdown = QComboBox()
        self.rows_dropdown = QComboBox()
        self.directional_dropdown = QComboBox()

        self.populate_dropdown(self.columns_dropdown, self.parent.columns.keys())
        self.populate_dropdown(self.rows_dropdown, self.parent.rows.keys())
        self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "South East"])

        custom_location_layout.addWidget(QLabel("ABC Street:"))
        custom_location_layout.addWidget(self.columns_dropdown)
        custom_location_layout.addWidget(QLabel("123 Street:"))
        custom_location_layout.addWidget(self.rows_dropdown)
        custom_location_layout.addWidget(QLabel("Direction:"))
        custom_location_layout.addWidget(self.directional_dropdown)

        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(custom_location_layout)

        # Add control buttons
        button_layout = QGridLayout()  # Change to QGridLayout to accommodate (widget, row, column) syntax

        set_button = QPushButton("Set Destination")
        set_button.clicked.connect(self.set_destination)
        clear_button = QPushButton("Clear Destination")
        clear_button.clicked.connect(self.clear_destination)
        update_button = QPushButton("Update Data")
        update_button.clicked.connect(self.update_comboboxes)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Add buttons to the layout using the correct syntax for QGridLayout
        button_layout.addWidget(set_button, 0, 0)
        button_layout.addWidget(clear_button, 0, 1)
        button_layout.addWidget(update_button, 1, 0)
        button_layout.addWidget(cancel_button, 1, 1)

        main_layout.addLayout(button_layout)

    def populate_dropdown(self, dropdown, items):
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems(items)

    def update_comboboxes(self):
        # Run the scraper before updating comboboxes
        self.parent.scraper.scrape_guilds_and_shops()

        # Now update the comboboxes with the new data
        self.parent.columns, self.parent.rows, self.parent.banks_coordinates, self.parent.taverns_coordinates, self.parent.transits_coordinates, self.parent.user_buildings_coordinates, self.parent.color_mappings, self.parent.shops_coordinates, self.parent.guilds_coordinates, self.parent.places_of_interest_coordinates = load_data()

        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown,
                               [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())
        self.populate_dropdown(self.columns_dropdown, self.parent.columns.keys())
        self.populate_dropdown(self.rows_dropdown, self.parent.rows.keys())

    def clear_destination(self):
        """
        Clear the currently set destination and update the minimap.
        """
        # Clear the destination in the parent application
        self.parent.destination = None

        # Save the cleared destination to the file to ensure persistence
        with open('./sessions/destination.pkl', 'wb') as f:
            pickle.dump(self.parent.destination, f)
            pickle.dump(datetime.now(), f)
        self.parent.update_minimap()
        self.accept()

    def set_destination(self):
        selected_tavern = self.tavern_dropdown.currentText()
        selected_bank = self.bank_dropdown.currentText()
        selected_transit = self.transit_dropdown.currentText()
        selected_shop = self.shop_dropdown.currentText()
        selected_guild = self.guild_dropdown.currentText()
        selected_poi = self.poi_dropdown.currentText()
        selected_user_building = self.user_building_dropdown.currentText()

        col, row = None, None  # Initialize col and row to None
        direction = None  # Initialize direction to None

        if selected_tavern != "Select a destination":
            col, row = self.parent.taverns_coordinates[selected_tavern]
        elif selected_bank != "Select a destination":
            col_name, row_name = selected_bank.split(" & ")
            col, row = self.parent.columns[col_name], self.parent.rows[row_name]
            col += 1  # Adjust bank coordinates by +1
            row += 1
        elif selected_transit != "Select a destination":
            col, row = self.parent.transits_coordinates[selected_transit]
        elif selected_shop != "Select a destination":
            col, row = self.parent.shops_coordinates[selected_shop]
        elif selected_guild != "Select a destination":
            col, row = self.parent.guilds_coordinates[selected_guild]
        elif selected_poi != "Select a destination":
            col, row = self.parent.places_of_interest_coordinates[selected_poi]
        elif selected_user_building != "Select a destination":
            col, row = self.parent.user_buildings_coordinates[selected_user_building]
        else:
            col_name = self.columns_dropdown.currentText()
            row_name = self.rows_dropdown.currentText()
            direction = self.directional_dropdown.currentText()

            if col_name and row_name:
                col = self.parent.columns.get(col_name)
                row = self.parent.rows.get(row_name)

                if col is not None and row is not None:
                    # Apply direction
                    if direction == "East":
                        col += 1  # Only move to the East
                    elif direction == "South":
                        row += 1  # Only move to the South
                    elif direction == "South East":
                        col += 1  # Move to the East
                        row += 1  # Move to the South

        # If col and row are set, update the destination
        if col is not None and row is not None:
            self.parent.destination = (col, row)
            self.parent.save_destination()
            self.parent.update_minimap()
            self.accept()
            logging.debug(f"Setting destination to col={col}, row={row} for direction={direction}")
        else:
            logging.warning("No valid destination selected or incorrect coordinates provided.")


class ShoppingListTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)

        self.connection = connect_to_database()
        if not self.connection:
            print("Failed to connect to the database.")
            sys.exit(1)

        self.cursor = self.connection.cursor()

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create dropdowns for selecting shop and charisma level
        form_layout = QFormLayout()

        self.shop_dropdown = QComboBox()
        self.populate_shop_dropdown()
        form_layout.addRow("Select Shop:", self.shop_dropdown)

        self.charisma_dropdown = QComboBox()
        self.charisma_dropdown.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        form_layout.addRow("Select Charisma Level:", self.charisma_dropdown)

        main_layout.addLayout(form_layout)

        # Create list widgets for shopping list
        self.item_list = QListWidget()
        self.shopping_list = QListWidget()

        main_layout.addWidget(QLabel("Available Items"))
        main_layout.addWidget(self.item_list)

        # Add buttons for adding/removing items
        button_layout = QVBoxLayout()

        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item_to_list)
        button_layout.addWidget(add_button)

        remove_button = QPushButton("Remove Item")
        remove_button.clicked.connect(self.remove_item_from_list)
        button_layout.addWidget(remove_button)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Shopping List"))
        main_layout.addWidget(self.shopping_list)

        # Create a label to display the total of the shopping list
        self.total_label = QLabel("List Total: 0 Coins")
        main_layout.addWidget(self.total_label)

        # Load the items when the shop or charisma level changes
        self.shop_dropdown.currentIndexChanged.connect(self.load_items)
        self.charisma_dropdown.currentIndexChanged.connect(self.update_shopping_list_prices)

        # Load items initially
        self.load_items()

    def populate_shop_dropdown(self):
        """
        Populate the shop dropdown with available shops from the database.
        """
        self.cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
        shops = self.cursor.fetchall()
        for shop in shops:
            self.shop_dropdown.addItem(shop[0])

    def load_items(self):
        """
        Load items from the selected shop and charisma level into the item list.
        """
        self.item_list.clear()
        shop_name = self.shop_dropdown.currentText()
        charisma_level = self.charisma_dropdown.currentText()

        if charisma_level == "No Charisma":
            price_column = "base_price"
        elif charisma_level == "Charisma 1":
            price_column = "charisma_level_1"
        elif charisma_level == "Charisma 2":
            price_column = "charisma_level_2"
        elif charisma_level == "Charisma 3":
            price_column = "charisma_level_3"
        else:
            price_column = "base_price"  # Default to base_price

        query = f"""
        SELECT item_name, {price_column}
        FROM shop_items
        WHERE shop_name = %s
        """
        self.cursor.execute(query, (shop_name,))
        items = self.cursor.fetchall()

        for item in items:
            item_name = item[0]
            price = item[1]
            self.item_list.addItem(f"{item_name} - {price} Coins")

    def add_item_to_list(self):
        """
        Add the selected item to the shopping list.
        """
        selected_item = self.item_list.currentItem()
        if selected_item:
            item_name = selected_item.text().split(" - ")[0]
            price = int(selected_item.text().split(" - ")[1].split()[0])
            self.shopping_list.addItem(f"{item_name} - {price} Coins")
            self.update_total()

    def remove_item_from_list(self):
        """
        Remove the selected item from the shopping list.
        """
        selected_item = self.shopping_list.currentItem()
        if selected_item:
            self.shopping_list.takeItem(self.shopping_list.row(selected_item))
            self.update_total()

    def update_shopping_list_prices(self):
        """
        Update the prices of items in the shopping list when the charisma level is changed.
        """
        charisma_level = self.charisma_dropdown.currentText()

        if charisma_level == "No Charisma":
            price_column = "base_price"
        elif charisma_level == "Charisma 1":
            price_column = "charisma_level_1"
        elif charisma_level == "Charisma 2":
            price_column = "charisma_level_2"
        elif charisma_level == "Charisma 3":
            price_column = "charisma_level_3"
        else:
            price_column = "base_price"  # Default to base_price

        for index in range(self.shopping_list.count()):
            item_name = self.shopping_list.item(index).text().split(" - ")[0]

            query = f"""
            SELECT {price_column}
            FROM shop_items
            WHERE shop_name = %s AND item_name = %s
            """
            self.cursor.execute(query, (self.shop_dropdown.currentText(), item_name))
            price = self.cursor.fetchone()[0]

            self.shopping_list.item(index).setText(f"{item_name} - {price} Coins")

        self.update_total()

    def update_total(self):
        """
        Calculate and update the total cost of items in the shopping list.
        """
        total = 0
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            price = int(item_text.split("-")[1].strip().split()[0])  # Extract the price
            total += price

        self.total_label.setText(f"List Total: {total} Coins")

    def closeEvent(self, event):
        """
        Ensure the database connection is closed when the application is closed.
        """
        self.cursor.close()
        self.connection.close()
        event.accept()


def main():
    """
    Main function to run the RBC City Map Application.
    """
    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
