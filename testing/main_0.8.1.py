#!/usr/bin/env python3
# Filename: main_0.8.1

"""
=========================
RBC Community Map Application
=========================
The RBC Community Map Application provides a comprehensive graphical interface for navigating
the city map of RavenBlack City. It offers features such as zooming, setting and saving destinations,
viewing points of interest (such as banks, taverns, and guilds), and managing user characters.
Map data is dynamically fetched from a MySQL database, and the app also supports refreshing
data from the 'A View in the Dark' website via web scraping.

Features include:
- Zooming in and out of the map.
- Setting, saving, and loading destinations.
- Viewing closest points of interest, such as banks and taverns.
- Managing multiple user characters, including automatic login for the last active character.
- Handling cookies and persistent sessions for web scraping.
- Coin and bank balance tracking with automatic updates from in-game actions.

Modules:
- sys: Provides access to system-specific parameters and functions.
- os: Used for interacting with the operating system (e.g., directory and file management).
- pickle: Facilitates the serialization and deserialization of Python objects.
- pymysql: Interface for connecting to and interacting with a MySQL database.
- sqlite3: Interface for SQLite database management, used for cookies and coins.
- requests: Allows sending HTTP requests to interact with external websites.
- re: Provides regular expression matching operations, useful for HTML parsing.
- datetime: Supplies classes for manipulating dates and times.
- bs4 (BeautifulSoup): Used for parsing HTML and XML documents.
- PySide6: Provides Python bindings for the Qt application framework, including UI components.
- PySide6.QtWebEngineWidgets: Provides web view functionality to render in-game pages.

Classes:
- RBCCommunityMap: The main application class, responsible for initializing and managing the user interface,
  web scraping, character management, and map functionalities.
- DatabaseViewer: Displays the contents of MySQL database tables in a tabbed view for inspection.
- CharacterDialog: A dialog class for adding, modifying, or deleting user characters.
- ThemeCustomizationDialog: A dialog class that allows users to customize the application's theme.
- SetDestinationDialog: A dialog class for setting destinations on the map.
- AVITDScraper: A web scraper class for fetching and updating data for guilds and shops from 'A View in the Dark'.

Functions:
- connect_to_database: Establishes a connection to the MySQL database and handles any connection errors.
- load_data: Loads map data from the MySQL database, including coordinates for banks, taverns, transits, shops, and guilds.
- initialize_cookie_db: Sets up an SQLite database for managing cookies.
- save_cookie_to_db: Saves individual cookies from web sessions to the SQLite database.
- load_cookies_from_db: Loads cookies from the SQLite database into the web engine for persistent sessions.
- clear_cookie_db: Clears all cookies from the SQLite database.
- fetch_table_data: Retrieves column names and data from a specified MySQL database table.
- extract_coordinates_from_html: Extracts in-game map coordinates from loaded HTML content.
- find_nearest_location: Finds the nearest point of interest based on a set of coordinates.
- calculate_ap_cost: Calculates the Action Point (AP) cost between two locations on the map.
- update_guilds: Scrapes and updates the guilds data in the MySQL database.
- update_shops: Scrapes and updates the shops data in the MySQL database.
- get_next_update_times: Retrieves the next update times for guilds and shops from the database.
- inject_console_logging: Injects JavaScript into web pages to capture and log console messages.
- apply_theme: Applies the selected theme to the application UI components.
- save_theme_settings: Saves customized theme settings to a file for persistence.
- load_theme_settings: Loads saved theme settings from a file or the MySQL database.
- show_about_dialog: Displays an 'About' dialog with details about the application and its version.
- show_credits_dialog: Displays a scrolling 'Credits' dialog with contributors to the project.

To install all required modules, run the following command:
 pip install pymysql requests bs4 PySide6 PySide6-WebEngine
"""

import importlib.util
import os
# -----------------------
# Imports Handling
# -----------------------
import sys

# List of required modules
required_modules = [
    'pickle', 'pymysql', 'requests', 're', 'time', 'sqlite3',
    'webbrowser', 'datetime', 'bs4', 'PySide6.QtWidgets',
    'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtNetwork','cryptography', 'hashlib'
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
        print(f"pip install {' '.join(missing_modules)}")
        return False
    return True

# Check for required modules
if not check_required_modules(required_modules):
    sys.exit("Missing required modules. Please install them and try again.")

# Proceed with the rest of the imports and program setup
import logging
import pymysql
import requests
import re
import webbrowser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QColorDialog, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QInputDialog
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction
from PySide6.QtCore import QUrl, Qt, QRect, QEasingCurve, QPropertyAnimation, QSize, QTimer, QDateTime
from PySide6.QtCore import Slot as pyqtSlot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtNetwork import QNetworkCookie
import sqlite3
from cryptography.fernet import Fernet

# Initialize Fernet encryption using the loaded key
key = b'Kslt2S6mlIeMRsRhfnZ2k2PjFjI98rOUpNE9H8bLywE='  # Replace with your actual key
cipher_suite = Fernet(key)

# -----------------------
# Directory Setup
# -----------------------

def ensure_directories_exist():
    """
    Ensure that the required directories exist. If they don't, create them.

    This function checks for the presence of directories that are essential for
    the application's operation. If any of these directories are missing, they
    are created automatically to prevent issues during runtime. The directories
    managed by this function include:
    - logs: Stores application log files.
    - sessions: Stores session-related data, such as user sessions or cookies.
    - settings: Stores application settings and configuration files.
    - images: Stores image files used by the application, such as icons.

    If any of these directories do not exist, they are created in the current working directory.
    """
    required_dirs = ['logs', 'sessions', 'images']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Call the function to ensure directories are present
ensure_directories_exist()

# -----------------------
# Logging Setup
# -----------------------

def setup_logging():
    """
    Set up logging configuration to save logs in the 'logs' directory.

    This function configures the logging system to record application events,
    errors, and debug information in a log file. The log file is named
    'rbc_{date}.log', where {date} is replaced with the current date in the
    format 'YYYY-MM-DD'. The log files are saved in the 'logs' directory,
    and log messages are formatted to include the timestamp, log level,
    and the message content.

    Logging levels used:
    - DEBUG: Detailed information, typically of interest only when diagnosing problems.
    - INFO: Confirmation that things are working as expected.
    - WARNING: An indication that something unexpected happened, or indicative of some problem.
    - ERROR: A more serious problem, the software has not been able to perform some function.

    If the 'logs' directory does not exist, it should be created by calling
    the 'ensure_directories_exist()' function before this function.
    """
    log_filename = datetime.now().strftime('./logs/rbc_%Y-%m-%d.log')
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level to DEBUG to capture all events
        format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
        filename=log_filename,  # Log file path and name
        filemode='a'  # Append to the log file if it already exists
    )
    print(f"Logging to: {log_filename}")  # Print the log file location to the console

# Call the logging setup function to initialize logging configuration
setup_logging()

# -----------------------
# SQLite Setup
# -----------------------

# Local Database path
DB_PATH = 'sessions/rbc_map_data.db'

def initialize_database():
    """
    Initialize the consolidated database for all data storage.
    Only creates the database and tables if the file does not exist.
    """
    if not os.path.exists(DB_PATH):
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Create the characters table with a primary key on id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT
            )
        ''')

        # Create the last_active_character table with a foreign key on character_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS last_active_character (
                character_id INTEGER,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
            )
        ''')

        # Create the settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_name TEXT PRIMARY KEY,
                setting_value BLOB
            )
        ''')

        # Create the coins table with a foreign key on character_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coins (
                character_id INTEGER,
                pocket INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
            )
        ''')

        # Create the cookies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cookies (
                name TEXT,
                domain TEXT,
                path TEXT,
                value TEXT,
                expiration INTEGER,
                UNIQUE(name, domain, path) ON CONFLICT REPLACE
            )
        ''')

        # Create the color_mappings table for theme settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS color_mappings (
                Type TEXT PRIMARY KEY,
                Color TEXT
            )
        ''')

        # Create the destinations table to store recent destinations with a limit of the last 10
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                col INTEGER,
                row INTEGER,
                timestamp TEXT
            )
        ''')

        connection.commit()
        connection.close()
        print(f"Database {DB_PATH} created with required tables.")
    else:
        print(f"Database {DB_PATH} already exists. Initialization skipped.")

# Call database initialization
initialize_database()

# -----------------------
# MySQL Connection Setup
# -----------------------

# MySQL Server information
REMOTE_HOST = "completeelectronics.net"
LOCAL_HOST = "127.0.0.1"
USER = "rbc_maps"
PASSWORD = "RBC_Community_Map"
DATABASE = "city_map"

def connect_to_database():
    """
    Attempt to connect to the MySQL database, starting with the remote server.
    """
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
            return None

database_connection = connect_to_database()

# -----------------------
# Load Data from Database
# -----------------------

def load_data():
    """
    Load various map-related data from the MySQL database.

    This function establishes a database connection and retrieves data for columns, rows,
    banks, taverns, transits, user buildings, color mappings, shops, guilds, and places of interest.
    The data is stored in dictionaries or lists and returned for use in the application.

    Returns:
        tuple: Contains the following data:
            - columns (dict): Mapping of column names to their coordinates.
            - rows (dict): Mapping of row names to their coordinates.
            - banks_coordinates (list): List of tuples containing column and row coordinates for banks.
            - taverns_coordinates (dict): Mapping of tavern names to their coordinates.
            - transits_coordinates (dict): Mapping of transit names to their coordinates.
            - user_buildings_coordinates (dict): Mapping of user building names to their coordinates.
            - color_mappings (dict): Mapping of element types to their QColor values.
            - shops_coordinates (dict): Mapping of shop names to their coordinates.
            - guilds_coordinates (dict): Mapping of guild names to their coordinates.
            - places_of_interest_coordinates (dict): Mapping of place of interest names to their coordinates.
    """
    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

    # Fetch column names and their coordinates
    cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
    columns_data = cursor.fetchall()
    columns = {name: int(coordinate) for name, coordinate in columns_data}

    # Fetch row names and their coordinates
    cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
    rows_data = cursor.fetchall()
    rows = {name: int(coordinate) for name, coordinate in rows_data}

    # Fetch coordinates from the banks table
    cursor.execute("SELECT `Column`, `Row` FROM banks")
    banks_data = cursor.fetchall()
    banks_coordinates = [
        (col, row, None, None)
        for col, row in banks_data
    ]

    # Fetch taverns and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM taverns")
    taverns_data = cursor.fetchall()
    taverns_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in taverns_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch transits and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM transits")
    transits_data = cursor.fetchall()
    transits_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in transits_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch user buildings and their coordinates
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

    # Fetch shops and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM shops")
    shops_data = cursor.fetchall()
    shops_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in shops_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch guilds and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM guilds")
    guilds_data = cursor.fetchall()
    guilds_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in guilds_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch places of interest and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM placesofinterest")
    places_of_interest_data = cursor.fetchall()
    places_of_interest_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in places_of_interest_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Close the database connection after fetching all data
    connection.close()

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates

# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()

# -----------------------
# Webview Cookie Database
# -----------------------

def save_cookie_to_db(cookie):
    """
    Save a single cookie to the SQLite database.

    Args:
        cookie (QNetworkCookie): The QNetworkCookie object representing the cookie to save.

    This function inserts the cookie's details into the 'cookies' table in the SQLite database.
    """
    connection = sqlite3.connect(DB_PATH)
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
        list: A list of QNetworkCookie objects representing the cookies stored in the database.

    This function retrieves all cookies from the 'cookies' table in the SQLite database
    and converts them into QNetworkCookie objects.
    """
    connection = sqlite3.connect(DB_PATH)
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

    This function deletes all records from the 'cookies' table, effectively clearing all stored cookies.
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM cookies')
    connection.commit()
    connection.close()

# -----------------------
# RBC Community Map Main Class
# -----------------------
class RBCCommunityMap(QMainWindow):
    """
    Main application class for the RBC Community Map.
    """

    def __init__(self):
        """
        Initialize the RBCCommunityMap and its components.
        """
        super().__init__()

        self.is_updating_minimap = False

        # Early initialization of the scraper
        self.AVITD_scraper = AVITDScraper()
        self.AVITD_scraper.scrape_guilds_and_shops()

        self.login_needed = True

        # Set up the main window properties
        self.setWindowIcon(QIcon('images/favicon.ico'))
        self.setWindowTitle('RBC Community Map')
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

        # Load characters from previous sessions
        self.load_characters()

        if not self.characters:
                self.firstrun_character_creation()

        self.load_destination()
        self.setup_ui()
        self.setup_console_logging()
        self.show()
        self.update_minimap()
        self.load_last_active_character()

    # -----------------------
    # Load and apply customized UI Theme
    # -----------------------

    def load_theme_settings(self):
        """
        Load the theme settings from the SQLite database.

        This method checks if theme settings exist in the `color_mappings` table of the unified database.
        If not found, it initializes `color_mappings` with default values.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Fetch the theme settings from the color_mappings table
            cursor.execute("SELECT `Type`, `Color` FROM color_mappings")
            color_mappings_data = cursor.fetchall()

            # Populate color_mappings with QColor objects
            self.color_mappings = {type_: QColor(color) for type_, color in color_mappings_data}
            logging.debug("Theme settings loaded from database.")

            # Set default color if no entries are found
            if not self.color_mappings:
                self.color_mappings = {"background": QColor("white"), "text_color": QColor("black"),
                                       "button_color": QColor("lightgrey")}

        except sqlite3.Error as e:
            logging.error(f"Failed to load theme settings from database: {e}")
            self.color_mappings = {"background": QColor("white"), "text_color": QColor("black"),
                                   "button_color": QColor("lightgrey")}
        finally:
            connection.close()

    def save_theme_settings(self):
        """
        Save the current theme settings to the SQLite database, updating or inserting each setting.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the color_mappings table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS color_mappings (
                    Type TEXT PRIMARY KEY,
                    Color TEXT
                )
            ''')

            # Insert or update each color setting
            for type_, color in self.color_mappings.items():
                cursor.execute('''
                    INSERT INTO color_mappings (Type, Color) VALUES (?, ?)
                    ON CONFLICT(Type) DO UPDATE SET Color = excluded.Color
                ''', (type_, color.name()))  # QColor to hex string

            connection.commit()
            logging.info("Theme settings saved to database.")

        except sqlite3.Error as e:
            logging.error(f"Failed to save theme settings to database: {e}")
        finally:
            connection.close()

    def apply_theme(self):
        """
        Apply the theme settings to the application.

        This method applies the loaded or default theme settings, including background color, text color,
        and button color, to the entire application UI.
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

        This method allows the user to customize the application's theme colors and immediately apply the changes.
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
        Set up cookie handling, including loading and saving cookies from the 'cookies' table in rbc_map_data.db.
        """
        # Ensure the cookies table exists in the unified database
        self.initialize_cookie_db()

        # Connect the QWebEngineProfile's cookie store to the application
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)

        # Load previously saved cookies from the database
        self.load_cookies()

    def initialize_cookie_db(self):
        """
        Create the 'cookies' table in rbc_map_data.db if it does not already exist.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cookies (
                name TEXT,
                domain TEXT,
                path TEXT,
                value TEXT,
                expiration INTEGER,
                UNIQUE(name, domain, path) ON CONFLICT REPLACE
            )
        ''')

        connection.commit()
        connection.close()

    def load_cookies(self):
        """
        Load cookies from the 'cookies' table in rbc_map_data.db and inject them into the QWebEngineProfile.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("SELECT name, domain, path, value, expiration FROM cookies")
        cookies = cursor.fetchall()

        for name, domain, path, value, expiration in cookies:
            cookie = QNetworkCookie()
            cookie.setName(name.encode())
            cookie.setDomain(domain)
            cookie.setPath(path)
            cookie.setValue(value.encode())
            cookie.setExpirationDate(QDateTime.fromSecsSinceEpoch(expiration))
            self.cookie_store.setCookie(cookie, QUrl(f"https://{domain}"))

        connection.close()
        logging.info("Cookies loaded from rbc_map_data.db.")

    def on_cookie_added(self, cookie):
        """
        Save a newly added cookie to the 'cookies' table in rbc_map_data.db.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Convert expiration date to a timestamp if it’s not a session cookie
            expiration = cookie.expirationDate().toSecsSinceEpoch() if not cookie.isSessionCookie() else None

            cursor.execute('''
                INSERT INTO cookies (name, domain, path, value, expiration)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                bytes(cookie.name()).decode('utf-8'),  # Convert QByteArray to string
                cookie.domain(),
                cookie.path(),
                bytes(cookie.value()).decode('utf-8'),  # Convert QByteArray to string
                expiration
            ))

            connection.commit()
            logging.debug(f"Cookie added to rbc_map_data.db: {cookie.name().data().decode('utf-8')}")
        except Exception as e:
            logging.error(f"Failed to add cookie to database: {e}")
        finally:
            connection.close()

    # -----------------------
    # UI Setup
    # -----------------------

    def setup_ui(self):
        """
        Set up the main user interface for the RBC Community Map application.

        This method initializes and arranges the key components of the user interface,
        including the minimap, browser controls, and character management.
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
        self.website_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Directly process coins from HTML within `process_html`
        if self.selected_character:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id FROM characters WHERE name = ?", (self.selected_character['name'],))
                character_row = cursor.fetchone()
                if character_row:
                    character_id = character_row[0]
                    self.selected_character['id'] = character_id  # Ensure character ID is available for coin extraction
                    logging.info(f"Character ID {character_id} set for {self.selected_character['name']}.")
                else:
                    logging.error(f"Character '{self.selected_character['name']}' not found in the database.")
            except sqlite3.Error as e:
                logging.error(f"Failed to retrieve character ID: {e}")
            finally:
                connection.close()

                self.show()
                self.update_minimap()

    # -----------------------
    # Browser Controls Setup
    # -----------------------

    def go_back(self):
        """
        Navigate the web browser back to the previous page.
        """
        self.website_frame.back()

    def go_forward(self):
        """
        Navigate the web browser forward to the next page.
        """
        self.website_frame.forward()

    def refresh_page(self):
        """
        Refresh the current page displayed in the web browser.
        """
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
        Set up console logging within the web engine view by connecting the web channel
        to handle JavaScript console messages.
        """
        self.web_channel = QWebChannel(self.website_frame.page())
        self.website_frame.page().setWebChannel(self.web_channel)
        self.web_channel.registerObject("qtHandler", self)

    def inject_console_logging(self):
        """
        Inject JavaScript into the web page to capture console logs and send them to PyQt,
        enabling logging of JavaScript console messages within the Python application.
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
            message (str): The console message to be logged.
        """
        print(f"Console message: {message}")
        logging.debug(f"Console message: {message}")

    # -----------------------
    # Menu Control Items
    # -----------------------

    def save_webpage_screenshot(self):
        """
        Save the current webpage as a screenshot.

        Opens a file dialog to specify the location and filename for saving
        the screenshot in PNG format.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Webpage Screenshot", "",
                                                   "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.website_frame.grab().save(file_name)

    def save_app_screenshot(self):
        """
        Save the current application window as a screenshot.

        Opens a file dialog to specify the location and filename for saving
        the screenshot in PNG format.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save App Screenshot", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.grab().save(file_name)

    def open_shopping_list_tool(self):
        """
        Opens the ShoppingListTool, using the currently selected character from character_list.
        If no character is selected, it displays an error message.
        """
        # Get the currently selected character from the QListWidget (character_list)
        current_item = self.character_list.currentItem()

        if current_item:
            character_name = current_item.text()  # Extract the selected character's name
        else:
            # Show an error message if no character is selected
            QMessageBox.warning(self, "No Character Selected", "Please select a character from the list.")
            return

        # Open the ShoppingListTool with the selected character and unified database path
        self.shopping_list_tool = ShoppingListTool(character_name, DB_PATH)
        self.shopping_list_tool.show()

    # -----------------------
    # Character Management
    # -----------------------

    def load_characters(self):
        """
        Load characters from the SQLite database, including IDs for reference.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the characters table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT
                )
            ''')

            # Fetch characters from the database including id
            cursor.execute("SELECT id, name, password FROM characters")
            character_data = cursor.fetchall()
            self.characters = [
                {'id': char_id, 'name': name, 'password': password}
                for char_id, name, password in character_data
            ]

            # Populate characters list and UI element
            self.character_list.clear()
            for character in self.characters:
                self.character_list.addItem(QListWidgetItem(character['name']))
            logging.debug("Characters loaded successfully from the database.")

            # Automatically select the first character if any exist
            if self.characters:
                self.character_list.setCurrentRow(0)
                self.selected_character = self.characters[0]

        except sqlite3.Error as e:
            logging.error(f"Failed to load characters from database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load characters: {e}")
            self.characters = []
        finally:
            connection.close()

    def save_characters(self):
        """
        Save characters to the SQLite database in plaintext.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the characters table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    name TEXT PRIMARY KEY,
                    password TEXT
                )
            ''')

            # Insert or update each character without encrypting the password
            for character in self.characters:
                cursor.execute('''
                    INSERT OR REPLACE INTO characters (name, password) VALUES (?, ?)
                ''', (character['name'], character['password']))

            connection.commit()
            logging.debug("Characters saved successfully to the database in plaintext.")

        except sqlite3.Error as e:
            logging.error(f"Failed to save characters to database: {e}")
        finally:
            connection.close()

    def on_character_selected(self, item):
        """
        Handle character selection from the list.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)

        if selected_character:
            logging.debug(f"Selected character: {character_name}")
            self.selected_character = selected_character

            # Retrieve character_id from the database
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            try:
                cursor.execute("SELECT id FROM characters WHERE name = ?", (character_name,))
                character_row = cursor.fetchone()
                if character_row:
                    character_id = character_row[0]
                    self.save_last_active_character(character_id)  # Pass character_id to save_last_active_character
                else:
                    logging.error(f"Character '{character_name}' not found in characters table.")

            except sqlite3.Error as e:
                logging.error(f"Failed to retrieve character_id for '{character_name}': {e}")
            finally:
                connection.close()

            self.logout_current_character()
            QTimer.singleShot(1000, self.login_selected_character)

    def logout_current_character(self):
        """
        Logout the current character by navigating to the logout URL.
        """
        logging.debug("Logging out current character.")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))
        QTimer.singleShot(1000, self.login_selected_character)

    def login_selected_character(self):
        """
        Log in the selected character using the plaintext password.
        """
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        logging.debug(f"Logging in character: {self.selected_character['name']}")
        name = self.selected_character['name']
        password = self.selected_character['password']  # Plaintext password

        # JavaScript code to fill in the login form
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

    def firstrun_character_creation(self):
        """
        Handles the first-run character creation, saving the character in plaintext,
        initializing default coin values in the coins table, and setting this character as the last active.
        """
        logging.debug("First-run character creation.")
        dialog = CharacterDialog(self)

        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            try:
                # Insert the new character into the characters table
                cursor.execute('''
                    INSERT INTO characters (name, password) VALUES (?, ?)
                ''', (name, password))
                connection.commit()

                # Retrieve the id of the newly inserted character
                character_id = cursor.lastrowid

                # Insert default coin values for the new character in the coins table
                cursor.execute('''
                    INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)
                ''', (character_id,))
                connection.commit()

                # Set the new character as the last active character
                self.save_last_active_character(character_id)

                # Update the character list in the UI
                self.characters.append({'name': name, 'password': password})
                self.character_list.addItem(QListWidgetItem(name))

                logging.debug(f"Character '{name}' created with initial coin values and set as last active.")

            except sqlite3.Error as e:
                logging.error(f"Failed to create character '{name}': {e}")
            finally:
                connection.close()

        else:
            sys.exit("No characters added. Exiting the application.")

    def add_new_character(self):
        """
        Add a new character to the list, saving the password in plaintext,
        initializing default coin values in the coins table, and setting this character as the last active.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)

        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            try:
                # Insert the new character into the characters table
                cursor.execute('''
                    INSERT INTO characters (name, password) VALUES (?, ?)
                ''', (name, password))
                connection.commit()

                # Retrieve the id of the newly inserted character
                character_id = cursor.lastrowid

                # Insert default coin values for the new character in the coins table
                cursor.execute('''
                    INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)
                ''', (character_id,))
                connection.commit()

                # Set the new character as the last active character
                self.save_last_active_character(character_id)

                # Update the character list in the UI
                self.characters.append({'name': name, 'password': password})
                self.character_list.addItem(QListWidgetItem(name))

                logging.debug(f"Character '{name}' added with initial coin values and set as last active.")

            except sqlite3.Error as e:
                logging.error(f"Failed to add character '{name}': {e}")
            finally:
                connection.close()

    def modify_character(self):
        """
        Modify the selected character's details, saving the new password in plaintext.
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

    def save_last_active_character(self, character_id):
        """
        Save the last active character's ID to the last_active_character table.
        Ensures that only one entry exists, replacing any previous entry.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Use REPLACE INTO to ensure there's only one entry for the last active character
            cursor.execute('''
                REPLACE INTO last_active_character (character_id) VALUES (?)
            ''', (character_id,))

            connection.commit()
            logging.debug(f"Last active character set to character_id: {character_id}")

        except sqlite3.Error as e:
            logging.error(f"Failed to save last active character: {e}")
        finally:
            connection.close()

    def load_last_active_character(self):
        """
        Load the last active character from the database by character_id and set the selected character for auto-login.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Retrieve the last active character's ID from the last_active_character table
            cursor.execute("SELECT character_id FROM last_active_character")
            result = cursor.fetchone()

            if result:
                character_id = result[0]

                # Find the character in self.characters by matching 'id'
                self.selected_character = next((char for char in self.characters if char.get('id') == character_id),
                                               None)

                if self.selected_character:
                    logging.debug(f"Last active character loaded: {self.selected_character['name']}")
                    self.login_needed = True  # Set the flag to indicate login is needed
                    self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))  # Load the login page
                else:
                    logging.warning(f"Last active character ID '{character_id}' not found in character list.")

            else:
                logging.warning("No last active character found in the database.")

        except sqlite3.Error as e:
            logging.error(f"Failed to load last active character from database: {e}")
        finally:
            connection.close()

    # -----------------------
    # Web View Handling
    # -----------------------

    def on_webview_load_finished(self, success):
        """
        Handle the event when the webview finishes loading.

        Logs an error and shows a message box if the load fails. If successful, the HTML
        content is processed to extract coordinates and update the minimap.
        """
        if not success:
            logging.error("Failed to load the webpage.")
            QMessageBox.critical(self, "Error",
                                 "Failed to load the webpage. Please check your network connection or try again later.")
        else:
            logging.info("Webpage loaded successfully.")
            # Process the HTML if needed
            self.website_frame.page().toHtml(self.process_html)

            # If login is needed, trigger the login process
            if self.login_needed:
                logging.debug("Logging in last active character.")
                self.login_selected_character()
                self.login_needed = False

    def process_html(self, html):
        """
        Process the HTML content of the webview to extract coordinates and coin information.

        Args:
            html (str): The HTML content of the page as a string.

        This method calls both the extract_coordinates_from_html and extract_coins_from_html methods.
        """
        try:
            # Extract coordinates for the minimap
            x_coord, y_coord = self.extract_coordinates_from_html(html)
            if x_coord is not None and y_coord is not None:
                # Apply specific offsets based on zoom level
                if self.zoom_level == 3:
                    offset = 0  # No offset needed for 3x3
                elif self.zoom_level == 5:
                    offset = -1  # Offset by -1 for 5x5
                elif self.zoom_level == 7:
                    offset = -2  # Offset by -2 for 7x7
                else:
                    offset = -(self.zoom_level // 2)  # Default case if needed

                # Apply the calculated offset to center the minimap
                self.column_start = x_coord + offset
                self.row_start = y_coord + offset
                self.update_minimap()

            # Call the method to extract bank coins and pocket changes from the HTML
            self.extract_coins_from_html(html)
            logging.debug("HTML processed successfully for coordinates and coin count.")

        except Exception as e:
            logging.error(f"Unexpected error in process_html: {e}")

    def extract_coordinates_from_html(self, html):
        """
        Extract coordinates from the HTML content.

        Args:
            html (str): HTML content as a string.

        Returns:
            tuple: x and y coordinates.

        Parses the HTML using BeautifulSoup to find the input elements that hold the
        x and y coordinates. Returns these coordinates if found, otherwise returns None.
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

    def extract_coins_from_html(self, html):
        """
        Extract bank coins, pocket coins, and handle coin-related actions such as deposits,
        withdrawals, transit handling, and coins gained from hunting or stealing.

        Args:
            html (str): The HTML content as a string.

        This method searches for bank balance, deposits, withdrawals, hunting, robbing, receiving,
        and transit coin actions in the HTML content, updating both bank and pocket coins in the
        SQLite database based on character_id.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Get the character ID for the selected character
        character_id = self.selected_character['id']

        # Search for the bank balance line
        bank_match = re.search(r"Welcome to Omnibank. Your account has (\d+) coins in it.", html)

        # Search for a deposit action
        deposit_match = re.search(r"You deposit (\d+) coins.", html)

        # Search for a withdrawal action
        withdraw_match = re.search(r"You withdraw (\d+) coins.", html)

        # Search for transit pocket coin update
        transit_match = re.search(r"It costs 5 coins to ride. You have (\d+).", html)

        # Additional coin-related actions
        actions = {
            'hunter': r'You drink the hunter\'s blood.*You also found (\d+) coins',
            'paladin': r'You drink the paladin\'s blood.*You also found (\d+) coins',
            'human': r'You drink the human\'s blood.*You also found (\d+) coins',
            'bag_of_coins': r'The bag contained (\d+) coins',
            'robbing': r'You stole (\d+) coins from (\w+)',
            'silver_suitcase': r'The suitcase contained (\d+) coins',
            'given_coins': r'(\w+) gave you (\d+) coins',
            'getting_robbed': r'(\w+) stole (\d+) coins from you'
        }

        # Handle bank balance update
        if bank_match:
            bank_coins = int(bank_match.group(1))
            logging.info(f"Bank coins found: {bank_coins}")

            # Update the bank coins in the SQLite database
            cursor.execute('''
                UPDATE coins
                SET bank = ?
                WHERE character_id = ?
            ''', (bank_coins, character_id))

        # Handle deposit action
        if deposit_match:
            deposit_coins = int(deposit_match.group(1))
            logging.info(f"Deposit found: {deposit_coins} coins")

            # Reduce the pocket coins by the deposited amount
            cursor.execute('''
                UPDATE coins
                SET pocket = pocket - ?
                WHERE character_id = ?
            ''', (deposit_coins, character_id))

        # Handle withdrawal action
        if withdraw_match:
            withdraw_coins = int(withdraw_match.group(1))
            logging.info(f"Withdrawal found: {withdraw_coins} coins")

            # Increase the pocket coins by the withdrawn amount
            cursor.execute('''
                UPDATE coins
                SET pocket = pocket + ?
                WHERE character_id = ?
            ''', (withdraw_coins, character_id))

        # Handle transit coin update
        if transit_match:
            coins_in_pocket = int(transit_match.group(1))
            logging.info(f"Transit found: Pocket coins updated to {coins_in_pocket}")

            # Explicitly set the pocket coin count after transit
            cursor.execute('''
                UPDATE coins
                SET pocket = ?
                WHERE character_id = ?
            ''', (coins_in_pocket, character_id))

        # Handle other coin-related actions (hunting, robbing, etc.)
        for action, pattern in actions.items():
            match = re.search(pattern, html)
            if match:
                coin_count = int(match.group(1))
                if action == 'getting_robbed':
                    # Losing coins when robbed
                    vamp_name = match.group(2)
                    cursor.execute('''
                        UPDATE coins
                        SET pocket = pocket - ?
                        WHERE character_id = ?
                    ''', (coin_count, character_id))
                    logging.info(f"Lost {coin_count} coins to {vamp_name}.")
                else:
                    # Gaining coins from hunting, robbing, etc.
                    cursor.execute('''
                        UPDATE coins
                        SET pocket = pocket + ?
                        WHERE character_id = ?
                    ''', (coin_count, character_id))
                    logging.info(f"Gained {coin_count} coins from {action}.")
                break  # Exit loop after first match

        connection.commit()
        connection.close()
        logging.info(f"Updated coins for character ID {character_id}.")

    def refresh_webview(self):
        """
        Refresh the webview content.

        Reloads the current page displayed in the QWebEngineView.
        """
        self.website_frame.reload()

    # -----------------------
    # Minimap Drawing and Update
    # -----------------------
    def draw_minimap(self):
        """
        Draws the minimap with various features such as special locations and lines to nearest locations,
        with cell lines and dynamically scaled text size.
        """
        pixmap = QPixmap(self.minimap_size, self.minimap_size)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, self.minimap_size, self.minimap_size, QColor('lightgrey'))

        block_size = self.minimap_size // self.zoom_level
        font_size = max(8, block_size // 4)  # Dynamically adjust font size, with a minimum of 5
        border_size = 1  # Size of the border around each cell

        # Dynamically adjust font size based on block size
        font = painter.font()
        font.setPointSize(font_size)
        painter.setFont(font)

        # Calculate font metrics for centering text
        font_metrics = QFontMetrics(font)

        def draw_location(column_index, row_index, color, label_text=None):
            """
            Draws a location on the minimap with dynamic scaling and border.

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
                # Calculate bounding box for text centering
                text_rect = font_metrics.boundingRect(label_text)
                # Calculate centered position with boundaries
                text_x = x0 + (block_size - text_rect.width()) // 2
                text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()

                # Define QRect for wrapping within cell size, ensuring center alignment with bounds
                wrap_rect = QRect(x0, y0, block_size, block_size)
                painter.setPen(QColor('white'))
                painter.drawText(wrap_rect, Qt.AlignCenter | Qt.TextWordWrap, label_text)

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
                if column_index < min(self.columns.values()) or column_index > max(self.columns.values()) or \
                        row_index < min(self.rows.values()) or row_index > max(self.rows.values()):
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

                    # Set the font size dynamically, ensuring it does not exceed the maximum
                    max_font_size = 8  # Set to desired maximum font size
                    calculated_font_size = max(4, min(block_size // 3, max_font_size))
                    font = painter.font()
                    font.setPointSize(calculated_font_size)
                    painter.setFont(font)

                    # Define text rectangle and enable word wrapping with center alignment
                    text_rect = QRect(x0, y0, block_size, block_size)
                    painter.setPen(QColor('white'))
                    painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, label_text)

        # Draw special locations (banks with correct offsets)
        for (col_name, row_name, _, _) in self.banks_coordinates:
            column_index = self.columns.get(col_name)
            row_index = self.rows.get(row_name)
            if column_index is not None and row_index is not None:
                # Adjust bank coordinates by +1 to match the tavern and transit coordinate system
                adjusted_column_index = column_index + 1
                adjusted_row_index = row_index + 1
                logging.debug(
                    f"Drawing bank at {col_name} & {row_name} with coordinates ({adjusted_column_index}, {adjusted_row_index})")
                draw_location(adjusted_column_index, adjusted_row_index, self.color_mappings["bank"], "Bank")
            else:
                logging.warning(f"Skipping bank at {col_name} & {row_name} due to missing coordinates")

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
            painter.setPen(QPen(QColor('orange'), 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_tavern_coords[0] - self.column_start) * block_size + block_size // 2,
                (nearest_tavern_coords[1] - self.row_start) * block_size + block_size // 2
            )

        # Draw nearest bank line
        if nearest_bank:
            nearest_bank_coords = nearest_bank[0][1]
            logging.debug(
                f"Drawing line to nearest bank at coordinates ({nearest_bank_coords[0] + 1}, {nearest_bank_coords[1] + 1})")
            painter.setPen(QPen(QColor('blue'), 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank_coords[0] + 1 - self.column_start) * block_size + block_size // 2,
                (nearest_bank_coords[1] + 1 - self.row_start) * block_size + block_size // 2
            )

        # Draw nearest transit line
        if nearest_transit:
            nearest_transit_coords = nearest_transit[0][1]
            logging.debug(
                f"Drawing line to nearest transit at coordinates ({nearest_transit_coords[0]}, {nearest_transit_coords[1]})")
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit_coords[0] - self.column_start) * block_size + block_size // 2,
                (nearest_transit_coords[1] - self.row_start) * block_size + block_size // 2
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

        Calls draw_minimap and then updates the info frame with any relevant information.
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
        return self.find_nearest_location(x, y, list(self.taverns_coordinates.values()))

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
        return self.find_nearest_location(x, y, list(self.transits_coordinates.values()))

    def set_destination(self):
        """
        Open the set destination dialog to select a new destination.
        """
        dialog = set_destination_dialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.update_minimap()

    def get_current_destination(self):
        """
        Retrieve the latest destination from the SQLite database.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT col, row FROM destinations ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        connection.close()
        return (result[0], result[1]) if result else None

    def load_destination(self):
        """
        Load the destination from the SQLite database.

        Loads the last set destination coordinates and updates the minimap if available.
        """
        destination_coords = self.get_current_destination()
        if destination_coords:
            self.destination = destination_coords
            logging.info(f"Loaded destination from database: {self.destination}")
        else:
            self.destination = None
            logging.info("No destination found in database. Starting with no destination.")

    # -----------------------
    # Minimap Controls
    # -----------------------
    def zoom_in(self):
        """
        Zoom in the minimap, ensuring the character stays centered.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 2  # Reduce by 2 to keep zoom levels odd-numbered
            self.website_frame.page().toHtml(self.process_html)

    def zoom_out(self):
        """
        Zoom out the minimap, ensuring the character stays centered.
        """
        if self.zoom_level < 7:  # Adjusted max level to improve readability
            self.zoom_level += 2  # Increase by 2 to keep zoom levels odd-numbered
            self.website_frame.page().toHtml(self.process_html)

    def recenter_minimap(self):
        """
        Recenter the minimap so that the character's location is at the center cell.
        """
        # Ensure character_x and character_y are up to date
        if not hasattr(self, 'character_x') or not hasattr(self, 'character_y'):
            logging.error("Character position not set. Cannot recenter minimap.")
            return

        # Calculate the center offset based on the current zoom level
        center_offset = (self.zoom_level - 1) // 2

        # Set `column_start` and `row_start` to keep the character centered
        self.column_start = max(self.character_x - center_offset, 0)
        self.row_start = max(self.character_y - center_offset, 0)

        # Update the minimap display after recentering
        self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location.

        Adjusts the minimap's starting column and row based on the selected location from the combo boxes,
        then updates the minimap.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()

        if column_name in self.columns:
            self.column_start = self.columns[column_name] - self.zoom_level // 2

        if row_name in self.rows:
            self.row_start = self.rows[row_name] - self.zoom_level // 2

        # Recenter and update the minimap after setting the new location
        self.recenter_minimap()

    def open_set_destination_dialog(self):
        """
        Open the set destination dialog.

        Opens a dialog that allows the user to set a destination. If the user confirms the destination,
        it loads the destination and updates the minimap.
        """
        dialog = set_destination_dialog(self)

        # Execute dialog and check for acceptance
        if dialog.exec() == QDialog.Accepted:
            # Load the newly set destination from the database
            self.load_destination()

            # Update the minimap with the new destination
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

        This method calculates and displays the nearest tavern, bank, and transit station to the current location,
        along with the AP (Action Points) cost to reach each. It also displays the details for the set destination,
        if any.
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
        Open the RBC Discord invite link in the system's default web browser.
        """
        webbrowser.open('https://discord.gg/nwEa8FaTDS')

    def open_website(self):
        """
        Open the RBC Website in the system's default web browser.
        """
        webbrowser.open('http://lollis-home.tailbf7f28.ts.net/viewpage.php?page_id=1')

    def show_about_dialog(self):
        """
        Display an "About" dialog with details about the RBC City Map application.

        The dialog includes information about the application version, its purpose,
        and a brief description of its features.
        """
        QMessageBox.about(self, "About RBC City Map",
                          "RBC City Map Application\n\n"
                          "Version 0.8.0\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Development team shown in credits.\n\n")

    def show_credits_dialog(self):
        """
        Display a "Credits" dialog with a list of contributors to the RBC City Map project.

        The credits are presented in a scrolling animation, acknowledging contributions
        from different individuals for various parts of the project.
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

        # Create and start the scrolling animation
        animation = QPropertyAnimation(credits_label, b"geometry")
        animation.setDuration(30000)  # 30 seconds
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(
            QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        animation.start()

        credits_dialog.exec()


# -----------------------
# Database Viewer Class
# -----------------------
    def open_database_viewer(self):
        """
        Open the database viewer to browse and inspect data from the RBC City Map database.

        This method connects to the database, fetches the data from specified tables,
        and displays it in a new DatabaseViewer window. Ensures a fresh connection each time.
        """
        try:
            # Create a new database connection every time the viewer is opened
            database_connection = connect_to_database()

            if not database_connection:
                QMessageBox.critical(self, "Error", "Failed to connect to the database.")
                return

            # Show the database viewer, passing the new connection
            self.database_viewer = DatabaseViewer(database_connection)
            self.database_viewer.show()

        except Exception as e:
            logging.error(f"Error opening Database Viewer: {e}")
            QMessageBox.critical(self, "Error", f"Error opening Database Viewer: {e}")

    def fetch_table_data(self, cursor, table_name):
        """
        Fetch data from the specified table and return it as a list of tuples, including column names.

        Args:
            cursor: MySQL cursor object.
            table_name: Name of the table to fetch data from.

        Returns:
            Tuple: (List of column names, List of table data)
        """
        cursor.execute(f"DESCRIBE `{table_name}`")
        column_names = [col[0] for col in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()

        return column_names, data

# -----------------------
# Tools
# -----------------------
class DatabaseViewer(QMainWindow):
    """
    Main application class for viewing database tables.

    This class provides a graphical interface to display the contents of multiple database tables
    in a tabbed layout, allowing users to easily browse and inspect the data.
    """

    def __init__(self, db_connection):
        """
        Initialize the DatabaseViewer with the provided table data.

        Args:
            db_connection: The established database connection.
        """
        super().__init__()
        self.setWindowTitle('MySQL Database Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Create a QTabWidget to hold the table views
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.db_connection = db_connection
        self.cursor = self.db_connection.cursor()

        # Query to get all table names
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()

        for (table_name,) in tables:
            column_names, data = self.get_table_data(table_name)
            self.add_table_tab(table_name, column_names, data)

    def get_table_data(self, table_name):
        """
        Fetch the column names and data for a given table.

        Args:
            table_name: The name of the table to fetch data from.

        Returns:
            A tuple containing a list of column names and the data.
        """
        # Use backticks to handle reserved keywords or special characters in table names
        self.cursor.execute(f"SELECT * FROM `{table_name}`")
        data = self.cursor.fetchall()

        column_names = [i[0] for i in self.cursor.description]
        return column_names, data

    def add_table_tab(self, table_name, column_names, data):
        """
        Add a new tab for a table.

        Args:
            table_name: The name of the table.
            column_names: List of column names for the table.
            data: The data to display in the table.
        """
        # Create a QTableWidget to display the table data
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(column_names))
        table_widget.setHorizontalHeaderLabels(column_names)

        # Populate the table with data
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        # Add the table widget as a new tab
        self.tab_widget.addTab(table_widget, table_name)

    def closeEvent(self, event):
        """
        Ensure the database connection is closed when the application is closed.
        """
        self.cursor.close()
        self.db_connection.close()
        event.accept()

# -----------------------
# Character Dialog Class
# -----------------------
class CharacterDialog(QDialog):
    """
    A dialog for adding or modifying a character.

    This dialog provides a simple interface for entering or editing the name and password
    of a character. It can be used to add a new character or modify an existing one.
    """

    def __init__(self, parent=None, character=None):
        """
        Initialize the character dialog.

        Args:
            parent (QWidget): The parent widget for this dialog.
            character (dict, optional): A dictionary containing the character's information.
                                        If provided, the dialog will be pre-filled with this data.
                                        Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Character")

        # Create input fields for the character's name and password
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Hide the password text

        # If a character is provided, pre-fill the fields with its data
        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        # Set up the form layout with labels and input fields
        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        # Create OK and Cancel buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)

        # Add the buttons to the layout
        layout.addRow(button_box)
        self.setLayout(layout)

        # Connect the buttons to the dialog's accept and reject methods
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

# -----------------------
# Theme Customization Dialog
# -----------------------
class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing the application's theme colors.

    This dialog provides the interface for users to change colors associated with UI elements
    and the minimap content. Users can save or cancel their changes.
    """

    def __init__(self, parent=None, color_mappings=None):
        """
        Initialize the theme customization dialog.

        Args:
            parent (QWidget): The parent widget.
            color_mappings (dict): A dictionary containing the current color mappings for the application.
        """
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')
        self.setMinimumSize(400, 300)

        # Initialize color mappings
        self.color_mappings = color_mappings if color_mappings else {}

        # Main layout of the dialog
        layout = QVBoxLayout(self)

        # Tab widget to separate UI elements and minimap content
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Create tabs
        self.ui_tab = QWidget()
        self.minimap_tab = QWidget()
        self.tabs.addTab(self.ui_tab, "UI, Buttons, and Text")
        self.tabs.addTab(self.minimap_tab, "Minimap Content")

        # Set up the tabs with content
        self.setup_ui_tab()
        self.setup_minimap_tab()

        # Add Save and Cancel buttons
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

        This tab allows users to customize colors for the background, text, and buttons.
        """
        layout = QGridLayout(self.ui_tab)

        # UI elements that can be customized
        ui_elements = ['background', 'text_color', 'button_color']

        # Create the layout with color squares and change buttons
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

        This tab allows users to customize colors for different elements on the minimap,
        such as banks, taverns, and user buildings.
        """
        layout = QGridLayout(self.minimap_tab)

        # Minimap elements that can be customized
        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']

        # Create the layout with color squares and change buttons
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
            element_name (str): The name of the element whose color is being changed.
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

        This method updates the application's stylesheet based on the selected colors.
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
        Initialize the scraper with the required headers and database connection.
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

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            section_image_alt (str): The alt text of the section image to locate the section.

        Returns:
            list: A list of tuples containing the name, column, and row of each entry.
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

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            section_name (str): The name of the section (e.g., 'Guilds', 'Shops').

        Returns:
            str: The next update time in 'YYYY-MM-DD HH:MM:SS' format or 'NA' if not found.
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

        Args:
            guilds (list): List of scraped guild data.
            shops (list): List of scraped shop data.
            guilds_next_update (str): The next update time for guilds.
            shops_next_update (str): The next update time for shops.
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

        Args:
            data (list): List of tuples containing the name, column, and row of each entry.
            table (str): The table name ('guilds' or 'shops') to update.
            next_update (str): The next update time to be stored in the database.
        """
        if not self.connection:
            logging.error("Failed to connect to the database.")
            return

        cursor = self.connection.cursor()

        # Step 1: Set all entries' Row and Column to 'NA' initially
        try:
            logging.debug(f"Setting all {table} entries' Row and Column to 'NA'.")
            cursor.execute(f"UPDATE {table} SET `Column`='NA', `Row`='NA', `next_update`=%s", (next_update,))
        except pymysql.MySQLError as e:
            logging.error(f"Failed to reset {table} entries to 'NA': {e}")

        # Step 2: Update with the correct data from the scraped results
        for name, column, row in data:
            try:
                logging.debug(
                    f"Updating {table} entry: Name={name}, Column={column}, Row={row}, Next Update={next_update}")
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
# Set Destination
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
        self.resize(200, 250)

        # Store the parent reference to access its methods
        self.parent = parent

        # Set up the main layout for the dialog
        main_layout = QVBoxLayout(self)

        # Dropdown for recent destinations
        self.recent_destinations_dropdown = QComboBox()
        self.populate_recent_destinations()

        # Comboboxes to select destinations
        dropdown_layout = QFormLayout()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()

        # Populate dropdowns with values from the MySQL database
        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

        dropdown_layout.addRow("Recent Destinations:", self.recent_destinations_dropdown)
        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

        # Custom location entry
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
        button_layout = QGridLayout()

        set_button = QPushButton("Set Destination")
        set_button.clicked.connect(self.set_destination)
        clear_button = QPushButton("Clear Destination")
        clear_button.clicked.connect(self.clear_destination)
        update_button = QPushButton("Update Data")
        update_button.clicked.connect(self.update_comboboxes)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(set_button, 0, 0)
        button_layout.addWidget(clear_button, 0, 1)
        button_layout.addWidget(update_button, 1, 0)
        button_layout.addWidget(cancel_button, 1, 1)

        main_layout.addLayout(button_layout)

    def populate_recent_destinations(self):
        """
        Populate the recent destinations dropdown with a human-readable street format.
        """
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem("Select a recent destination")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Retrieve recent destinations from the database
        cursor.execute("SELECT col, row FROM destinations ORDER BY timestamp DESC LIMIT 10")
        recent_destinations = cursor.fetchall()

        # Map each destination's grid coordinates to street names
        for col, row in recent_destinations:
            col_name = self.parent.columns.get(col, f"Column {col}")
            row_name = self.parent.rows.get(row, f"Row {row}")

            # Format as "ABC Street & 123 Street"
            destination_name = f"{col_name} & {row_name}"
            self.recent_destinations_dropdown.addItem(destination_name, (col, row))  # Store (col, row) as data

        connection.close()

    def populate_dropdown(self, dropdown, items):
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems(items)

    def update_comboboxes(self):
        """
        Update the comboboxes with the latest data after scraping.
        """
        self.show_notification("Updating Shop and Guild Data. Please wait...")

        if hasattr(self.parent, 'AVITD_scraper') and self.parent.AVITD_scraper:
            self.parent.AVITD_scraper.scrape_guilds_and_shops()
            logging.info("AVITD Scraper used to update guilds and shops.")
        else:
            logging.error("AVITD Scraper is not initialized or accessible in the parent class.")

        self.parent.columns, self.parent.rows, self.parent.banks_coordinates, \
            self.parent.taverns_coordinates, self.parent.transits_coordinates, \
            self.parent.user_buildings_coordinates, self.parent.color_mappings, \
            self.parent.shops_coordinates, self.parent.guilds_coordinates, \
            self.parent.places_of_interest_coordinates = load_data()

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

    def show_notification(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("Notification")
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        message_label = QLabel(message)
        layout.addWidget(message_label)
        dialog.setLayout(layout)

        QTimer.singleShot(5000, dialog.accept)
        dialog.setFixedSize(300, 100)
        dialog.exec()

    def clear_destination(self):
        """
        Clear the currently set destination and update the minimap.
        """
        self.parent.destination = None

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        try:
            cursor.execute('DELETE FROM destinations')
            connection.commit()
            logging.info("All destinations cleared from database.")

        except sqlite3.Error as e:
            logging.error(f"Failed to clear destinations in database: {e}")

        finally:
            connection.close()

        self.parent.update_minimap()
        self.accept()

    def set_destination(self):
        """
        Set the destination based on user selection from the dropdowns.
        """
        selected_tavern = self.tavern_dropdown.currentText()
        selected_bank = self.bank_dropdown.currentText()
        selected_transit = self.transit_dropdown.currentText()
        selected_shop = self.shop_dropdown.currentText()
        selected_guild = self.guild_dropdown.currentText()
        selected_poi = self.poi_dropdown.currentText()
        selected_user_building = self.user_building_dropdown.currentText()

        col, row = None, None
        direction = None

        if selected_tavern != "Select a destination":
            col, row = self.parent.taverns_coordinates[selected_tavern]
        elif selected_bank != "Select a destination":
            col_name, row_name = selected_bank.split(" & ")
            col, row = self.parent.columns[col_name], self.parent.rows[row_name]
            col += 1
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
                    if direction == "East":
                        col += 1
                    elif direction == "South":
                        row += 1
                    elif direction == "South East":
                        col += 1
                        row += 1

        if col is not None and row is not None:
            self.parent.destination = (col, row)

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            try:
                cursor.execute('''
                    INSERT INTO destinations (col, row, timestamp)
                    VALUES (?, ?, ?)
                ''', (col, row, datetime.now().isoformat()))

                cursor.execute('''
                    DELETE FROM destinations
                    WHERE id NOT IN (SELECT id FROM destinations ORDER BY timestamp DESC LIMIT 10)
                ''')

                connection.commit()
                logging.info(f"Destination set to col={col}, row={row} with direction={direction} and saved to database.")

            except sqlite3.Error as e:
                logging.error(f"Failed to set destination in database: {e}")

            finally:
                connection.close()

            self.parent.update_minimap()
            self.accept()
        else:
            logging.warning("No valid destination selected or incorrect coordinates provided.")

# -----------------------
# Shopping list Tools
# -----------------------
class ShoppingListTool(QMainWindow):
    def __init__(self, character_name, db_path):
        super().__init__()
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)
        self.character_name = character_name
        self.db_path = db_path  # Central SQLite DB path

        # Initialize MySQL connection for shop data
        self.mysql_connection = connect_to_database()  # MySQL connection for shop items
        if not self.mysql_connection:
            print("Failed to connect to the MySQL database.")
            sys.exit(1)

        self.cursor = self.mysql_connection.cursor()

        # Initialize SQLite connection for coin data
        self.sqlite_connection = sqlite3.connect(self.db_path)  # Central SQLite DB connection
        self.sqlite_cursor = self.sqlite_connection.cursor()

        # Initialize shopping list total
        self.list_total = 0

        # Setting up UI
        self.setup_ui()

        # Load data from MySQL (shop info)
        self.populate_shop_dropdown()

        # Load coin information from SQLite
        self.load_coin_info()

    def setup_ui(self):
        # Initialize UI elements
        self.shop_combobox = QComboBox(self)
        self.charisma_combobox = QComboBox(self)
        self.available_items_list = QListWidget(self)
        self.shopping_list = QListWidget(self)

        # Add options to charisma combobox
        self.charisma_combobox.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])

        # Buttons
        self.add_item_button = QPushButton("Add Item", self)
        self.remove_item_button = QPushButton("Remove Item", self)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Shop:"))
        layout.addWidget(self.shop_combobox)
        layout.addWidget(QLabel("Select Charisma Level:"))
        layout.addWidget(self.charisma_combobox)
        layout.addWidget(QLabel("Available Items:"))
        layout.addWidget(self.available_items_list)
        layout.addWidget(self.add_item_button)
        layout.addWidget(QLabel("Shopping List:"))
        layout.addWidget(self.shopping_list)
        layout.addWidget(self.remove_item_button)

        # Create a label to display the total of the shopping list, coins in pocket, and bank balance
        self.total_label = QLabel(
            f"List total: 0 Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}")
        layout.addWidget(self.total_label)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)

        # Load items when shop or charisma level changes
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self.load_items)

        # Load items initially
        self.load_items()

    def add_item(self):
        """
        Add the selected item from the available items list to the shopping list.
        """
        selected_item = self.available_items_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            item_name, item_price = item_text.split(" - ")
            quantity = 1  # Default quantity is 1

            # Check if the item is already in the shopping list
            for i in range(self.shopping_list.count()):
                existing_item_text = self.shopping_list.item(i).text()
                existing_item_name = existing_item_text.split(" - ")[0]
                if existing_item_name == item_name:
                    # Update the quantity if the item is already present
                    existing_quantity = int(existing_item_text.split(" - ")[2].split("x")[0])
                    self.shopping_list.item(i).setText(f"{item_name} - {item_price} Coins - {existing_quantity + 1}x")
                    self.update_total()
                    return

            # If the item is not in the list, add it with quantity 1
            self.shopping_list.addItem(f"{item_name} - {item_price} Coins - {quantity}x")
            self.update_total()

    def remove_item(self):
        """
        Remove the selected item from the shopping list or decrease its quantity.
        """
        selected_item = self.shopping_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            item_name, item_price, item_quantity = item_text.split(" - ")
            item_quantity = int(item_quantity.split("x")[0])

            if item_quantity > 1:
                # Decrease the quantity if more than 1
                self.shopping_list.currentItem().setText(f"{item_name} - {item_price} Coins - {item_quantity - 1}x")
            else:
                # Remove the item from the list if quantity is 1
                self.shopping_list.takeItem(self.shopping_list.row(selected_item))

            self.update_total()

    def add_from_damage_calculator(self, hw_count, gs_count):
        """
        Add Holy Water and Garlic Spray to the shopping list based on the damage calculator results.
        """
        shop_name = "Discount Potions"

        try:
            # Fetch the price for Vial of Holy Water from MySQL
            query_hw = """
            SELECT charisma_level_1 FROM shop_items
            WHERE shop_name = %s AND item_name = 'Vial of Holy Water'
            """
            self.cursor.execute(query_hw, (shop_name,))
            hw_price = self.cursor.fetchone()

            if hw_price:
                hw_price = hw_price[0]
            else:
                print("Vial of Holy Water not found.")
                return

            # Fetch the price for Garlic Spray from MySQL
            query_gs = """
            SELECT charisma_level_1 FROM shop_items
            WHERE shop_name = %s AND item_name = 'Garlic Spray'
            """
            self.cursor.execute(query_gs, (shop_name,))
            gs_price = self.cursor.fetchone()

            if gs_price:
                gs_price = gs_price[0]
            else:
                print("Garlic Spray not found.")
                return

            # Add Vial of Holy Water to the shopping list if hw_count > 0
            if hw_count > 0:
                self.shopping_list.addItem(f"Vial of Holy Water - {hw_price} Coins - {hw_count}x")

            # Add Garlic Spray to the shopping list if gs_count > 0
            if gs_count > 0:
                self.shopping_list.addItem(f"Garlic Spray - {gs_price} Coins - {gs_count}x")

            # Update the total price after adding the items
            self.update_total()

            # Ensure the shopping list window stays visible
            self.show()

        except pymysql.MySQLError as err:
            print(f"Error fetching prices from Discount Potions: {err}")

    def populate_shop_dropdown(self):
        """
        Populate the shop dropdown with available shops from the MySQL database.
        """
        try:
            self.cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
            shops = self.cursor.fetchall()
            for shop in shops:
                self.shop_combobox.addItem(shop[0])
        except pymysql.MySQLError as err:
            print(f"Error fetching shop names: {err}")

    def load_items(self):
        """
        Load items from the selected shop and charisma level into the available items list.
        Update the shopping list prices based on the selected charisma level.
        """
        self.available_items_list.clear()
        shop_name = self.shop_combobox.currentText()
        charisma_level = self.charisma_combobox.currentText()

        # Determine the price column based on charisma level
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(charisma_level, "base_price")

        # Load items for the selected shop and charisma level from MySQL
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
            self.available_items_list.addItem(f"{item_name} - {price} Coins")

        # Now update the prices of items in the shopping list based on the charisma level
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            item_name = item_text.split(" - ")[0]
            quantity = int(item_text.split(" - ")[2].split("x")[0])

            # Query for the updated price from MySQL
            query = f"""
            SELECT {price_column}
            FROM shop_items
            WHERE item_name = %s AND shop_name = %s
            """
            self.cursor.execute(query, (item_name, shop_name))
            result = self.cursor.fetchone()

            if result:
                updated_price = result[0]
                self.shopping_list.item(index).setText(f"{item_name} - {updated_price} Coins - {quantity}x")

        self.update_total()

    def update_total(self):
        """
        Update the total price of the shopping list and display it.
        """
        self.list_total = 0
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            item_price = int(item_text.split(" - ")[1].split(" Coins")[0])
            quantity = int(item_text.split(" - ")[2].split("x")[0])
            self.list_total += item_price * quantity

        self.total_label.setText(f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}")

    def load_coin_info(self):
        """
        Load the character's coin information from the SQLite database.
        """
        try:
            # Query to get coins in pocket and in bank for the character
            self.sqlite_cursor.execute("""
            SELECT coins_in_pocket, coins_in_bank
            FROM characters
            WHERE character_name = ?
            """, (self.character_name,))
            result = self.sqlite_cursor.fetchone()

            if result:
                self.coins_in_pocket = result[0]
                self.coins_in_bank = result[1]
            else:
                print(f"Character {self.character_name} not found in the database.")
                self.coins_in_pocket = 0
                self.coins_in_bank = 0

        except sqlite3.DatabaseError as err:
            print(f"Error fetching coin info: {err}")
            self.coins_in_pocket = 0
            self.coins_in_bank = 0

    def coins_in_pocket(self):
        return self.coins_in_pocket

    def coins_in_bank(self):
        return self.coins_in_bank


def main():
    """
    Main function to run the RBC City Map Application.
    """
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./images/favicon.ico'))  # Set the global favicon
    window = RBCCommunityMap()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()