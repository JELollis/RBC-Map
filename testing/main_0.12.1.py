#!/usr/bin/env python3
# Filename: main_0.12.1

"""
======================
License Agreement
======================

Copyright 2024-2025 RBC Community Map Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
=================================
RBC City Map Application (v0.12.1)
=================================
This application provides an interactive mapping tool for the text-based vampire game **Vampires! The Dark Alleyway**
(set in RavenBlack City). The map allows players to track locations, navigate using the minimap, manage characters,
set destinations, and interact with dynamically updated data scraped from "A View in the Dark."

Key Features:
- **WASD Keyboard Navigation**: Move seamlessly through the minimap.
- **Character Management**: Store and switch between multiple game accounts with encrypted credentials.
- **Minimap System**: View **nearest banks, taverns, and transit stations** dynamically.
- **SQLite Database Support**: Fast and lightweight storage with improved query performance.
- **Theme Customization**: Fully customizable interface with **CSS styling** options.
- **Web Scraper Integration**: Auto-fetch **guild/shop locations** from 'A View in the Dark'.
- **Shopping List Tool**: Plan in-game purchases with cost breakdowns.
- **Damage Calculator**: Calculate combat interactions and weapon damage efficiently.

Modules Used:
- **sys**: Provides system-specific parameters and functions.
- **os**: Used for interacting with the operating system (e.g., file and directory management).
- **requests**: Handles HTTP requests for web scraping operations.
- **re**: Regular expression operations for parsing HTML and text.
- **datetime**: Used in timestamps, logs, and database operations.
- **bs4 (BeautifulSoup)**: Parses HTML and extracts meaningful data (used in AVITDScraper).
- **PySide6**: Provides a **Qt-based GUI framework**, handling UI elements, WebEngine, and event management.
- **sqlite3**: Database engine for persistent storage of map data, character info, and settings.
- **webbrowser**: Enables external browser interactions (e.g., opening the RBC website or Discord).
- **math**: Used in **damage calculations** and navigation logic.
- **logging**: Captures logs, errors, and system events.

================================
Classes and Methods (v0.12.1)
================================

#### RBCCommunityMap (Core Application)
Handles the main UI, character management, minimap rendering, and keyboard navigation.

- **__init__**: Initializes the main window, UI, and database connections.
- **load_keybind_config**: Loads user-defined keybindings from the database.
- **setup_keybindings**: Assigns keyboard controls for movement (WASD).
- **move_character**: Moves the character in the desired direction.
- **setup_ui_components**: Builds the main UI layout.
- **refresh_page**: Reloads the webview content.
- **apply_theme**: Applies custom themes to the UI.
- **load_cookies**: Loads saved cookies into the embedded web browser.
- **extract_coordinates_from_html**: Parses player coordinates from the web page.
- **draw_minimap**: Renders the minimap based on extracted coordinates.
- **zoom_in/zoom_out**: Controls the minimap zoom level.
- **set_destination**: Marks a location on the minimap.
- **calculate_ap_cost**: Computes movement costs between locations.
- **mousePressEvent**: Captures mouse clicks to interact with the minimap.

#### DatabaseViewer (Database Management)
A utility to view and inspect data stored in the SQLite database.

- **__init__**: Initializes the database viewer UI.
- **get_table_data**: Fetches data from a selected table.
- **add_table_tab**: Displays a new tab for a table's content.
- **closeEvent**: Handles viewer closure and cleanup.

#### CharacterDialog (Character Management UI)
A dialog for adding and editing game characters.

- **__init__**: Initializes the character creation/modification dialog.

#### ThemeCustomizationDialog (Theme Settings)
A UI tool to adjust the app’s theme colors.

- **__init__**: Loads theme customization options.
- **setup_ui_tab**: Configures the main UI color settings.
- **setup_minimap_tab**: Configures minimap color customization.
- **change_color**: Opens a color picker to adjust UI elements.
- **apply_theme**: Saves and applies theme changes.

#### CSSCustomizationDialog (Webview Customization)
Allows users to modify webview styles using custom CSS.

- **__init__**: Initializes CSS customization.
- **add_tab**: Adds a category tab for CSS elements.
- **save_and_apply_changes**: Saves and injects custom CSS into the webview.

#### AVITDScraper (Web Scraping Engine)
Fetches guild and shop location data from "A View in the Dark."

- **__init__**: Sets up scraper parameters.
- **scrape_guilds_and_shops**: Collects shop and guild locations.
- **update_database**: Updates SQLite with fresh location data.

#### SetDestinationDialog (Destination Selection UI)
Allows users to select a travel destination within the city.

- **__init__**: Loads the UI components.
- **populate_recent_destinations**: Displays recently visited locations.
- **set_destination**: Saves a new destination in the database.

#### ShoppingListTool (In-Game Purchase Planning)
A tool for calculating costs of items from different shops.

- **__init__**: Initializes the shopping list interface.
- **add_item**: Adds an item to the list.
- **update_total**: Calculates total cost including charisma-based discounts.

#### DamageCalculator (Combat Assistance Tool)
Helps players estimate weapon damage needed to defeat opponents.

- **__init__**: Loads calculator settings.
- **calculate_damage**: Computes weapon-based damage outputs.

#### PowersDialog (Powers Reference UI)
Displays information about in-game powers and related locations.

- **__init__**: Initializes the powers UI.
- **load_powers**: Loads power descriptions.
- **set_destination**: Sets a guild as the destination for training.

================================
Installation Instructions
================================

To install dependencies, run:
```sh
pip install requests bs4 PySide6 PySide6-WebEngine
"""
import logging
import logging.handlers
# -----------------------
# Global Constants
# -----------------------
# Database Path
DB_PATH = 'sessions/rbc_map_data.db'

# Logging Configuration
LOG_DIR = 'logs'
DEFAULT_LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
def get_logging_level_from_db(default=logging.INFO) -> int:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'log_level'")
            row = cursor.fetchone()
            if row:
                return int(row[0])
    except Exception as e:
        print(f"Failed to load log level from DB: {e}", file=sys.stderr)
    return default

VERSION_NUMBER = "0.12.1"

# Keybinding Defaults
DEFAULT_KEYBINDS = {
    "move_up": "W",
    "move_down": "S",
    "move_left": "A",
    "move_right": "D",
    "zoom_in": "PageUp",
    "zoom_out": "PageDown",
}

# Required Directories
REQUIRED_DIRECTORIES = ['logs', 'sessions', 'images']



# -----------------------
# Imports Handling
# -----------------------

import math
import os
import subprocess
import sys

# List of required modules with pip package names (some differ from import names)
required_modules = {
    'requests': 'requests',
    're': 're',  # Built-in, no pip install needed
    'time': 'time',  # Built-in
    'sqlite3': 'sqlite3',  # Built-in
    'webbrowser': 'webbrowser',  # Built-in
    'datetime': 'datetime',  # Built-in
    'bs4': 'beautifulsoup4',
    'PySide6.QtWidgets': 'PySide6',
    'PySide6.QtGui': 'PySide6',
    'PySide6.QtCore': 'PySide6',
    'PySide6.QtWebEngineWidgets': 'PySide6',
    'PySide6.QtWebChannel': 'PySide6',
    'PySide6.QtNetwork': 'PySide6'
}

def check_and_install_modules(modules: dict[str, str]) -> bool:
    """
    Check if required modules are installed, prompt user to install missing ones, and attempt installation.

    Args:
        modules (dict): Dictionary mapping module names to their pip package names.

    Returns:
        bool: True if all modules are available after checking/installing, False otherwise.
    """
    missing_modules = []
    pip_installable = []

    # Check each module
    for module, pip_name in modules.items():
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
            if pip_name not in ('re', 'time', 'sqlite3', 'webbrowser', 'datetime'):  # Skip built-ins
                pip_installable.append(pip_name)

    if not missing_modules:
        return True

    # Inform user of missing modules
    print("The following modules are missing:")
    for mod in missing_modules:
        print(f"- {mod}")

    if not pip_installable:
        print("All missing modules are built-ins that should come with Python. Please check your Python installation.")
        return False

    # Prompt user for installation
    try:
        from PySide6.QtWidgets import QMessageBox  # Early import for GUI prompt
    except ImportError:
        # Fallback to console prompt if PySide6 isn't available yet
        response = input(f"\nWould you like to install missing modules ({', '.join(set(pip_installable))}) with pip? (y/n): ").strip().lower()
        if response != 'y':
            print("Please install the missing modules manually with:")
            print(f"pip install {' '.join(set(pip_installable))}")
            return False
    else:
        # Use GUI prompt if PySide6 is partially available
        _ = QApplication(sys.argv)  # Needed for QMessageBox to function
        # noinspection PyTypeChecker, PyUnresolvedReferences
        response = QMessageBox.question(None, "Missing Modules",f"Missing modules: {', '.join(missing_modules)}\n\nInstall with pip ({', '.join(set(pip_installable))})?",
                                        QMessageBox.Yes | QMessageBox.No)
        # noinspection PyUnresolvedReferences
        if response == QMessageBox.No:
            print("Please install the missing modules manually with:")
            print(f"pip install {' '.join(set(pip_installable))}")
            return False

    # Attempt to install missing modules
    print(f"Installing missing modules: {', '.join(set(pip_installable))}...")
    try:
        # Use sys.executable to ensure the correct Python environment
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + list(set(pip_installable)))
        print("Installation successful! Please restart the application.")

        # Re-check modules after installation
        for module in missing_modules:
            try:
                __import__(module)
            except ImportError:
                print(f"Failed to import {module} even after installation. Please check your environment.")
                return False
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install modules: {e}")
        print("Please install them manually with:")
        print(f"pip install {' '.join(set(pip_installable))}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during installation: {e}")
        return False

# Check and attempt to install required modules
if not check_and_install_modules(required_modules):
    sys.exit("Missing required modules. Please resolve the issues and try again.")

# Proceed with the rest of the imports and program setup
import requests
import re
import webbrowser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QComboBox, \
    QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem, QFileDialog, \
    QColorDialog, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QInputDialog, QTextEdit, QSplashScreen, \
    QCompleter, QCheckBox, QGroupBox, QStyle
from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction, QIntValidator, QMouseEvent, \
    QShortcut, QKeySequence, QDesktopServices, QBrush
from PySide6.QtCore import QUrl, Qt, QRect, QEasingCurve, QPropertyAnimation, QSize, QTimer, QDateTime, QMimeData, \
    QByteArray, QEvent
from PySide6.QtCore import Slot as pyqtSlot
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtNetwork import QNetworkCookie
from typing import List, Tuple, TYPE_CHECKING, cast, TypeVar, Type
from collections.abc import KeysView
import sqlite3

# -----------------------
# Define Type Checking
# -----------------------

if TYPE_CHECKING:
    class AVITDScraper:
        def scrape_guilds_and_shops(self) -> None: ...
        def close_connection(self) -> None: ...


    class MainWindowType(QWidget):
        current_css_profile: str
        selected_character: dict | None
        destination: tuple[int, int] | None
        website_frame: QWebEngineView
        AVITD_scraper: AVITDScraper
        def apply_custom_css(self, css: str) -> None: ...
        def update_minimap(self) -> None: ...

        columns: dict[str, int]
        rows: dict[str, int]
        taverns_coordinates: dict[str, tuple[int, int]]
        banks_coordinates: dict[str, tuple[str, str, str, str]]
        transits_coordinates: dict[str, tuple[int, int]]
        shops_coordinates: dict[str, tuple[int, int]]
        guilds_coordinates: dict[str, tuple[int, int]]
        places_of_interest_coordinates: dict[str, tuple[int, int]]
        user_buildings_coordinates: dict[str, tuple[int, int]]

# -----------------------
# Define App Icon
# -----------------------

APP_ICON = QIcon()

# -----------------------
# Startup Splash
# -----------------------

class SplashScreen(QSplashScreen):
    def __init__(self, image_path, max_height=400):
        if not os.path.exists(image_path):
            logging.error(f"Image not found: {image_path}")
            pixmap = QPixmap(300, 200)
            # noinspection PyUnresolvedReferences
            pixmap.fill(Qt.black)
        else:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logging.error(f"Failed to load image: {image_path}")
                pixmap = QPixmap(300, 200)
                # noinspection PyUnresolvedReferences
                pixmap.fill(Qt.black)
            else:
                # Scale pixmap to max_height, preserving aspect ratio
                if pixmap.height() > max_height:
                    # noinspection PyUnresolvedReferences

                    pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
        # noinspection PyUnresolvedReferences
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        # noinspection PyUnresolvedReferences
        self.setAttribute(Qt.WA_DeleteOnClose)

    def show_message(self, message):
        # noinspection PyUnresolvedReferences
        self.showMessage(f"Startup script: {message} loading...", Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        QApplication.processEvents()

# -----------------------
# Directory Setup
# -----------------------
def ensure_directories_exist(directories: list[str] = None) -> bool:
    """
    Ensure that the required directories exist, creating them if necessary.
    """
    if directories is None:
        directories = REQUIRED_DIRECTORIES

    success = True
    for directory in directories:
        try:
            # Check existence first to avoid unnecessary syscalls
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                logging.debug(f"Created directory: {directory}")
            else:
                logging.debug(f"Directory already exists: {directory}")
        except OSError as e:
            logging.error(f"Failed to create directory '{directory}': {e}")
            success = False
    return success

# Example usage at startup (optional, depending on your flow)
if not ensure_directories_exist():
    logging.warning("Some directories could not be created. Application may encounter issues.")

# -----------------------
# Logging Setup
# -----------------------
def setup_logging(log_dir: str = LOG_DIR, log_level: int = DEFAULT_LOG_LEVEL, log_format: str = LOG_FORMAT) -> bool:
    """
    Set up logging configuration to save logs in the specified directory with daily rotation.
    """
    log_filename = None  # Predefine so it's always available in except blocks
    try:
        log_filename = datetime.now().strftime(f'{log_dir}/rbc_%Y-%m-%d.log')

        # Clear any existing handlers to avoid duplication if called multiple times
        logger = logging.getLogger()
        if logger.handlers:
            logger.handlers.clear()

        handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter(log_format))
        handler.setLevel(log_level)

        logger.setLevel(log_level)
        logger.addHandler(handler)

        logger.info(f"Logging initialized. Logs will be written to {log_filename}")
        return True

    except OSError as e:
        print(f"Failed to set up logging to {log_filename or '[unknown]'}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error during logging setup: {e}", file=sys.stderr)
        return False

# Initialize logging at startup
if not setup_logging(log_level=get_logging_level_from_db()):
    print("Logging setup failed. Continuing without file logging.", file=sys.stderr)
    logging.basicConfig(level=DEFAULT_LOG_LEVEL, format=LOG_FORMAT, stream=sys.stderr)  # Fallback to console

# Log app version
logging.info(f"Launching app version {VERSION_NUMBER}")

def save_logging_level_to_db(level: int) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (setting_name, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_name) DO UPDATE SET setting_value=excluded.setting_value
            """, ('log_level', str(level)))
            conn.commit()
            logging.info(f"Log level updated to {logging.getLevelName(level)} in settings")
            return True
    except Exception as e:
        logging.error(f"Failed to save log level: {e}")
        return False

# -----------------------
# SQLite Setup
# -----------------------
def create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables if they don’t exist."""
    cursor = conn.cursor()
    tables = [
        """CREATE TABLE IF NOT EXISTS banks (
            ID INTEGER PRIMARY KEY,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT,
            active_cookie INTEGER DEFAULT NULL
        )
        """,
        """CREATE TABLE IF NOT EXISTS coins (
            character_id INTEGER,
            pocket INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS color_mappings (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            color TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS `columns` (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Coordinate INTEGER NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value TEXT,
            domain TEXT,
            path TEXT,
            expiration TEXT,
            secure INTEGER,
            httponly INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS css_profiles (
                    profile_name TEXT PRIMARY KEY
                )""",
        """CREATE TABLE IF NOT EXISTS custom_css (
            profile_name TEXT NOT NULL,
            element TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (profile_name, element),
            FOREIGN KEY (profile_name) REFERENCES css_profiles(profile_name) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            col INTEGER,
            row INTEGER,
            timestamp TEXT,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS guilds (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            next_update TIMESTAMP DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS last_active_character (
            character_id INTEGER,
            FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS placesofinterest (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS powers (
            power_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            guild TEXT NOT NULL,
            cost INTEGER DEFAULT NULL,
            quest_info TEXT,
            skill_info TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS recent_destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            col INTEGER,
            row INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS `rows` (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Coordinate INTEGER NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS settings (
            setting_name TEXT PRIMARY KEY,
            setting_value BLOB
        )""",
        """CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY,
            shop_name TEXT DEFAULT NULL,
            item_name TEXT DEFAULT NULL,
            base_price INTEGER DEFAULT NULL,
            charisma_level_1 INTEGER DEFAULT NULL,
            charisma_level_2 INTEGER DEFAULT NULL,
            charisma_level_3 INTEGER DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS shops (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            next_update TIMESTAMP DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS taverns (
            ID INTEGER PRIMARY KEY,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS transits (
            ID INTEGER PRIMARY KEY,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS userbuildings (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS discord_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            invite_link TEXT NOT NULL
        );"""
    ]
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            logging.debug(f"Created table: {table_sql.split('(')[0].strip()}")
        except sqlite3.Error as e:
            logging.error(f"Failed to create table: {e}")
            raise
    conn.commit()

def insert_initial_data(conn: sqlite3.Connection) -> None:
    """Insert initial data into the database."""
    cursor = conn.cursor()
    initial_data = [
        ("INSERT OR IGNORE INTO settings (setting_name, setting_value) VALUES (?, ?)", [
            ('keybind_config', 1),
            ('css_profile', 'Default'),
            ('log_level', str(DEFAULT_LOG_LEVEL))
        ]),

        ("INSERT OR IGNORE INTO banks (ID, Column, Row, Name) VALUES (?, ?, ?, ?)", [
            (1,'Aardvark','82nd','OmniBank'),
            (2,'Alder','40th','OmniBank'),
             (3,'Alder','80th','OmniBank'),
             (4,'Amethyst','16th','OmniBank'),
             (5,'Amethyst','37th','OmniBank'),
             (6,'Amethyst','99th','OmniBank'),
             (7,'Anguish','30th','OmniBank'),
             (8,'Anguish','73rd','OmniBank'),
             (9,'Anguish','91st','OmniBank'),
             (10,'Beech','26th','OmniBank'),
             (11,'Beech','39th','OmniBank'),
             (12,'Beryl','28th','OmniBank'),
             (13,'Beryl','40th','OmniBank'),
             (14,'Beryl','65th','OmniBank'),
             (15,'Beryl','72nd','OmniBank'),
             (16,'Bleak','14th','OmniBank'),
             (17,'Buzzard','13th','OmniBank'),
             (18,'Cedar','1st','OmniBank'),
             (19,'Cedar','52nd','OmniBank'),
             (20,'Cedar','80th','OmniBank'),
             (21,'Chagrin','23rd','OmniBank'),
             (22,'Chagrin','39th','OmniBank'),
             (23,'Cobalt','46th','OmniBank'),
             (24,'Cobalt','81st','OmniBank'),
             (25,'Cobalt','88th','OmniBank'),
             (26,'Cormorant','93rd','OmniBank'),
             (27,'Despair','1st','OmniBank'),
             (28,'Despair','75th','OmniBank'),
             (29,'Dogwood','4th','OmniBank'),
             (30,'Duck','37th','OmniBank'),
             (31,'Duck','77th','OmniBank'),
             (32,'Eagle','64th','OmniBank'),
             (33,'Eagle','89th','OmniBank'),
             (34,'Elm','98th','OmniBank'),
             (35,'Emerald','19th','OmniBank'),
             (36,'Emerald','90th','OmniBank'),
             (37,'Emerald','99th','OmniBank'),
             (38,'Ennui','20th','OmniBank'),
             (39,'Ennui','78th','OmniBank'),
             (40,'Fear','15th','OmniBank'),
             (41,'Ferret','32nd','OmniBank'),
             (42,'Ferret','90th','OmniBank'),
             (43,'Fir','2nd','OmniBank'),
             (44,'Flint','37th','OmniBank'),
             (45,'Flint','45th','OmniBank'),
             (46,'Flint','47th','OmniBank'),
             (47,'Flint','5th','OmniBank'),
             (48,'Gloom','34th','OmniBank'),
             (49,'Gloom','71st','OmniBank'),
             (50,'Gloom','89th','OmniBank'),
             (51,'Gloom','90th','OmniBank'),
             (52,'Haddock','46th','OmniBank'),
             (53,'Haddock','52nd','OmniBank'),
             (54,'Haddock','67th','OmniBank'),
             (55,'Haddock','74th','OmniBank'),
             (56,'Haddock','88th','OmniBank'),
             (57,'Hessite','39th','OmniBank'),
             (58,'Hessite','76th','OmniBank'),
             (59,'Holly','96th','OmniBank'),
             (60,'Horror','49th','OmniBank'),
             (61,'Horror','59th','OmniBank'),
             (62,'Ire','31st','OmniBank'),
             (63,'Ire','42nd','OmniBank'),
             (64,'Ire','53rd','OmniBank'),
             (65,'Ire','97th','OmniBank'),
             (66,'Ivory','5th','OmniBank'),
             (67,'Ivory','71st','OmniBank'),
             (68,'Ivy','70th','OmniBank'),
             (69,'Ivy','79th','OmniBank'),
             (70,'Ivy','NCL','OmniBank'),
             (71,'Jackal','43rd','OmniBank'),
             (72,'Jaded','25th','OmniBank'),
             (73,'Jaded','48th','OmniBank'),
             (74,'Jaded','71st','OmniBank'),
             (75,'Juniper','16th','OmniBank'),
             (76,'Juniper','20th','OmniBank'),
             (77,'Juniper','98th','OmniBank'),
             (78,'Knotweed','15th','OmniBank'),
             (79,'Knotweed','29th','OmniBank'),
             (80,'Kraken','13th','OmniBank'),
             (81,'Kraken','18th','OmniBank'),
             (82,'Kraken','34th','OmniBank'),
             (83,'Kraken','3rd','OmniBank'),
             (84,'Kraken','45th','OmniBank'),
             (85,'Kraken','48th','OmniBank'),
             (86,'Kraken','7th','OmniBank'),
             (87,'Kyanite','40th','OmniBank'),
             (88,'Kyanite','6th','OmniBank'),
             (89,'Larch','33rd','OmniBank'),
             (90,'Larch','7th','OmniBank'),
             (91,'Larch','91st','OmniBank'),
             (92,'Lead','11th','OmniBank'),
             (93,'Lead','21st','OmniBank'),
             (94,'Lead','88th','OmniBank'),
             (95,'Lion','80th','OmniBank'),
             (96,'Lonely','93rd','OmniBank'),
             (97,'Malachite','11th','OmniBank'),
             (98,'Malachite','32nd','OmniBank'),
             (99,'Malachite','87th','OmniBank'),
             (100,'Malaise','36th','OmniBank'),
             (101,'Malaise','4th','OmniBank'),
             (102,'Malaise','50th','OmniBank'),
             (103,'Maple','34th','OmniBank'),
             (104,'Maple','84th','OmniBank'),
             (105,'Maple','85th','OmniBank'),
             (106,'Mongoose','78th','OmniBank'),
             (107,'Mongoose','79th','OmniBank'),
             (108,'Mongoose','91st','OmniBank'),
             (109,'Nervous','10th','OmniBank'),
             (110,'Nettle','37th','OmniBank'),
             (111,'Nettle','67th','OmniBank'),
             (112,'Nickel','93rd','OmniBank'),
             (113,'Obsidian','36th','OmniBank'),
             (114,'Obsidian','79th','OmniBank'),
             (115,'Octopus','27th','OmniBank'),
             (116,'Octopus','71st','OmniBank'),
             (117,'Octopus','77th','OmniBank'),
             (118,'Olive','99th','OmniBank'),
             (119,'Olive','9th','OmniBank'),
             (120,'Oppression','2nd','OmniBank'),
             (121,'Oppression','89th','OmniBank'),
             (122,'Pessimism','19th','OmniBank'),
             (123,'Pessimism','44th','OmniBank'),
             (124,'Pessimism','87th','OmniBank'),
             (125,'Pilchard','44th','OmniBank'),
             (126,'Pilchard','60th','OmniBank'),
             (127,'Pine','42nd','OmniBank'),
             (128,'Pine','44th','OmniBank'),
             (129,'Pyrites','11th','OmniBank'),
             (130,'Pyrites','24th','OmniBank'),
             (131,'Pyrites','90th','OmniBank'),
             (132,'Quail','10th','OmniBank'),
             (133,'Quail','12th','OmniBank'),
             (134,'Quail','18th','OmniBank'),
             (135,'Quail','26th','OmniBank'),
             (136,'Quail','36th','OmniBank'),
             (137,'Quail','41st','OmniBank'),
             (138,'Quail','58th','OmniBank'),
             (139,'Quail','74th','OmniBank'),
             (140,'Qualms','28th','OmniBank'),
             (141,'Qualms','57th','OmniBank'),
             (142,'Qualms','75th','OmniBank'),
             (143,'Quartz','75th','OmniBank'),
             (144,'Quince','48th','OmniBank'),
             (145,'Quince','61st','OmniBank'),
             (146,'Ragweed','31st','OmniBank'),
             (147,'Ragweed','56th','OmniBank'),
             (148,'Raven','11th','OmniBank'),
             (149,'Raven','15th','OmniBank'),
             (150,'Raven','79th','OmniBank'),
             (151,'Raven','98th','OmniBank'),
             (152,'Regret','70th','OmniBank'),
             (153,'Ruby','18th','OmniBank'),
             (154,'Ruby','45th','OmniBank'),
             (155,'Sorrow','48th','OmniBank'),
             (156,'Sorrow','9th','OmniBank'),
             (157,'Squid','10th','OmniBank'),
             (158,'Squid','24th','OmniBank'),
             (159,'Steel','31st','OmniBank'),
             (160,'Steel','64th','OmniBank'),
             (161,'Steel','7th','OmniBank'),
             (162,'Sycamore','16th','OmniBank'),
             (163,'Tapir','11th','OmniBank'),
             (164,'Tapir','41st','OmniBank'),
             (165,'Tapir','NCL','OmniBank'),
             (166,'Teasel','60th','OmniBank'),
             (167,'Teasel','66th','OmniBank'),
             (168,'Teasel','92nd','OmniBank'),
             (169,'Torment','23rd','OmniBank'),
             (170,'Torment','28th','OmniBank'),
             (171,'Torment','31st','OmniBank'),
             (172,'Umbrella','20th','OmniBank'),
             (173,'Umbrella','80th','OmniBank'),
             (174,'Unctuous','23rd','OmniBank'),
             (175,'Unctuous','43rd','OmniBank'),
             (176,'Unicorn','11th','OmniBank'),
             (177,'Unicorn','78th','OmniBank'),
             (178,'Uranium','1st','OmniBank'),
             (179,'Uranium','48th','OmniBank'),
             (180,'Uranium','93rd','OmniBank'),
             (181,'Uranium','97th','OmniBank'),
             (182,'Vauxite','68th','OmniBank'),
             (183,'Vauxite','91st','OmniBank'),
             (184,'Vexation','24th','OmniBank'),
             (185,'Vulture','43rd','OmniBank'),
             (186,'Vulture','82nd','OmniBank'),
             (187,'WCL','77th','OmniBank'),
             (188,'Willow','84th','OmniBank'),
             (189,'Woe','44th','OmniBank'),
             (190,'Woe','85th','OmniBank'),
             (191,'Yak','45th','OmniBank'),
             (192,'Yak','82nd','OmniBank'),
             (193,'Yak','94th','OmniBank'),
             (194,'Yearning','75th','OmniBank'),
             (195,'Yearning','93rd','OmniBank'),
             (196,'Yew','4th','OmniBank'),
             (197,'Zebra','61st','OmniBank'),
             (198,'Zelkova','23rd','OmniBank'),
             (199,'Zelkova','73rd','OmniBank'),
             (200,'Zinc','74th','OmniBank')
        ]),
        ("INSERT OR IGNORE INTO color_mappings (id, type, color) VALUES (?, ?, ?)", [
            (1, 'bank', '#0000ff'),
            (2, 'tavern', '#887700'),
            (3, 'transit', '#880000'),
            (4, 'user_building', '#660022'),
            (5, 'alley', '#000000'),
            (6, 'default', '#888888'),
            (7, 'border', 'white'),
            (8, 'edge', '#0000ff'),
            (9, 'shop', '#004488'),
            (10, 'guild', '#ff0000'),
            (11, 'placesofinterest', '#660022'),
            (12, 'background', '#3b3b3b'),
            (13, 'text_color', '#dddddd'),
            (14, 'button_color', '#55557f'),
            (15, 'cityblock', '#0000dd'),
            (16, 'intersect', '#008800'),
            (17, 'street', '#444444'),
            (18, 'button_hover_color', '#666699'),
            (19, 'button_pressed_color', '#444466'),
            (20, 'button_border_color', '#222244'),
            (21, 'graveyard', '#888888')
        ]),
        ("INSERT OR IGNORE INTO `columns` (ID, Name, Coordinate) VALUES (?, ?, ?)", [
            ('1', 'WCL', '0'),
            ('2', 'Western City Limits', '0'),
            ('3', 'Aardvark', '2'),
            ('4', 'Alder', '4'),
            ('5', 'Buzzard', '6'),
            ('6', 'Beech', '8'),
            ('7', 'Cormorant', '10'),
            ('8', 'Cedar', '12'),
            ('9', 'Duck', '14'),
            ('10', 'Dogwood', '16'),
            ('11', 'Eagle', '18'),
            ('12', 'Elm', '20'),
            ('13', 'Ferret', '22'),
            ('14', 'Fir', '24'),
            ('15', 'Gibbon', '26'),
            ('16', 'Gum', '28'),
            ('17', 'Haddock', '30'),
            ('18', 'Holly', '32'),
            ('19', 'Iguana', '34'),
            ('20', 'Ivy', '36'),
            ('21', 'Jackal', '38'),
            ('22', 'Juniper', '40'),
            ('23', 'Kraken', '42'),
            ('24', 'Knotweed', '44'),
            ('25', 'Lion', '46'),
            ('26', 'Larch', '48'),
            ('27', 'Mongoose', '50'),
            ('28', 'Maple', '52'),
            ('29', 'Nightingale', '54'),
            ('30', 'Nettle', '56'),
            ('31', 'Octopus', '58'),
            ('32', 'Olive', '60'),
            ('33', 'Pilchard', '62'),
            ('34', 'Pine', '64'),
            ('35', 'Quail', '66'),
            ('36', 'Quince', '68'),
            ('37', 'Raven', '70'),
            ('38', 'Ragweed', '72'),
            ('39', 'Squid', '74'),
            ('40', 'Sycamore', '76'),
            ('41', 'Tapir', '78'),
            ('42', 'Teasel', '80'),
            ('43', 'Unicorn', '82'),
            ('44', 'Umbrella', '84'),
            ('45', 'Vulture', '86'),
            ('46', 'Vervain', '88'),
            ('47', 'Walrus', '90'),
            ('48', 'Willow', '92'),
            ('49', 'Yak', '94'),
            ('50', 'Yew', '96'),
            ('51', 'Zebra', '98'),
            ('52', 'Zelkova', '100'),
            ('53', 'Amethyst', '102'),
            ('54', 'Anguish', '104'),
            ('55', 'Beryl', '106'),
            ('56', 'Bleak', '108'),
            ('57', 'Cobalt', '110'),
            ('58', 'Chagrin', '112'),
            ('59', 'Diamond', '114'),
            ('60', 'Despair', '116'),
            ('61', 'Emerald', '118'),
            ('62', 'Ennui', '120'),
            ('63', 'Flint', '122'),
            ('64', 'Fear', '124'),
            ('65', 'Gypsum', '126'),
            ('66', 'Gloom', '128'),
            ('67', 'Hessite', '130'),
            ('68', 'Horror', '132'),
            ('69', 'Ivory', '134'),
            ('70', 'Ire', '136'),
            ('71', 'Jet', '138'),
            ('72', 'Jaded', '140'),
            ('73', 'Kyanite', '142'),
            ('74', 'Killjoy', '144'),
            ('75', 'Lead', '146'),
            ('76', 'Lonely', '148'),
            ('77', 'Malachite', '150'),
            ('78', 'Malaise', '152'),
            ('79', 'Nickel', '154'),
            ('80', 'Nervous', '156'),
            ('81', 'Obsidian', '158'),
            ('82', 'Oppression', '160'),
            ('83', 'Pyrites', '162'),
            ('84', 'Pessimism', '164'),
            ('85', 'Quartz', '166'),
            ('86', 'Qualms', '168'),
            ('87', 'Ruby', '170'),
            ('88', 'Regret', '172'),
            ('89', 'Steel', '174'),
            ('90', 'Sorrow', '176'),
            ('91', 'Turquoise', '178'),
            ('92', 'Torment', '180'),
            ('93', 'Uranium', '182'),
            ('94', 'Unctuous', '184'),
            ('95', 'Vauxite', '186'),
            ('96', 'Vexation', '188'),
            ('97', 'Wulfenite', '190'),
            ('98', 'Woe', '192'),
            ('99', 'Yuksporite', '194'),
            ('100', 'Yearning', '196'),
            ('101', 'Zinc', '198'),
            ('102', 'Zestless', '200')
        ]),
        ("INSERT OR IGNORE INTO css_profiles (profile_name) VALUES (?)", [("Default",)]),
        ("INSERT OR IGNORE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)", [
            ("Default", "BODY", "background-color:#000000;"),
            ("Default", "H1,DIV,BODY,P,A", "font-family:Verdana,Arial,sans-serif;"),
            ("Default", "BODY,H1", "text-align:center;"),
            ("Default", "P,A,TD,DIV,BODY", "color:#dddddd;"),
            ("Default", "P,TD,DIV", "text-align:left;"),
            ("Default", "TD", "vertical-align:top;"),
            ("Default", "TD,DIV,BODY,P", "font-size:small;"),
            ("Default", "FORM", "padding:0px; margin:0px; text-align:center;"),
            ("Default", "H1", "font-size:x-large; color:#ff0000; padding:0 0 0 0;"),
            ("Default", "A", "text-decoration:underline;"),
            ("Default", "UL", "text-align:left; font-size:smaller; padding-left:38px; margin-top:3px;"),
            ("Default", "P", "padding:5px 10px 0px 10px; margin:0px; font-weight:bold;"),
            ("Default", "P.ans", "font-style:italic; font-weight:normal; padding:5px 10px 0px 15px; margin:0px;"),
            ("Default", "DIV.spacey", "text-align:center; width:450px; padding-top:10px;"),
            ("Default", ".head", "text-align:center; font-weight:bold;"),
            ("Default", "TD.cityblock", "text-align:center; background-color:#0000dd;"),
            ("Default", "TD.intersect","text-align:center; background-color:#444444; width:150px; height:100px; position:relative;"),
            ("Default", "TD.street","text-align:center; background-color:#444444; width:150px; height:100px; position:relative;"),
            ("Default", "TD.city","text-align:center; border:solid white 1px; width:150px; height:100px; position:relative;"),
            ("Default", "SPAN.intersect", "background-color:#008800; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.transit", "background-color:#880000; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.arena","background-color:#ff0000; border:solid white 1px; padding:2px; font-weight:bold; color:white;"),
            ("Default", "SPAN.pub", "background-color:#887700; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.bank", "background-color:#0000ff; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.shop", "background-color:#004488; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.grave", "background-color:#888888; border:solid white 1px; color:#222222; padding:2px;"),
            ("Default", "SPAN.pk", "background-color:#000066; border:solid white 1px; color:#ffff00; padding:2px;"),
            ("Default", "SPAN.lair,SPAN.alchemy","background-color:#660022; border:solid white 1px; color:#cccccc; padding:2px;"),
            ("Default", "SPAN.sever,SPAN.bind", "border:solid red 1px; color:red; padding:2px;"),
            ("Default", "SPAN.vhuman", "color:green; background-color:black;"),
            ("Default", "SPAN.phuman", "color:cyan; background-color:black; font-weight:bold;"),
            ("Default", "SPAN.whuman", "color:brown; background-color:black; font-weight:bold;"),
            ("Default", "SPAN.object", "color:yellow;"),
            ("Default", "UL.possessions", "margin-top:0px; margin-bottom:3px; font-size:small;"),
            ("Default", "#mo","display:none; position:absolute; left:0; top:0; width:300; padding:2px; font:x-small Verdana,Sans-serif; color:black; background-color:yellow; border: solid black 1px;"),
            ("Default", "TABLE.textad", "background-color:#002211; border:solid #668877 1px;"),
            ("Default", "TABLE.hiscore", "border:solid #668877 1px;"),
            ("Default", "TABLE.hiscore tr:first-child", "background-color: #004400;"),
            ("Default", "TABLE.hiscore tr:not(:first-child) td", "border-right: solid #668877 1px;"),
            ("Default", "TD.headline", "font-size:8pt; text-align:center; padding:0px 8px 0px 8px;"),
            ("Default", "TD.text", "font-size:7pt; text-align:center; padding:0px 8px 0px 8px;"),
            ("Default", "TD.link", "font-size:6pt; text-align:right; color:#999999; padding:0px 2px 0px 1px;"),
            ("Default", "TABLE.at", "padding:5px; width:100%;"),
            ("Default", "TABLE.at TD","background-color:#333333; border:solid white 1px; padding:3px; padding-left:5px;"),
            ("Default", "TABLE.at TD.ahead", "font-weight:bold; padding-left:2px;"),
            ("Default", "DIV.asubhead", "font-weight:normal; font-size:80%;"),
            ("Default", "DIV.sb", "overflow:auto; height:80px; border:solid #bbbbbb 1px; background-color:#555533;"),
            ("Default", "TABLE.battle", "padding:0px; margin:0px;"),
            ("Default", "TABLE.battle TD", "border:none; padding:0px; margin:0px; text-align:center;"),
            ("Default", "TABLE.battle TD.n,TD.f,TD.e", "width:10px;"),
            ("Default", "TABLE.battle TD.f", "background:white;"),
            ("Default", "FORM.bq", "display:inline;"),
            ("Default", ".pansy", "color:#ff8888;"),
            ("Default", ".cloak", "color:#00ffff;"),
            ("Default", ".rich", "color:#ffff44;"),
            ("Default", ".mh","border:none; background-color:transparent; text-decoration:underline; color:white; padding:0px; cursor:hand;")
        ]),
        ("INSERT OR IGNORE INTO guilds (ID, Name, Column, Row, next_update) VALUES (?, ?, ?, ?, ?)", [
            (1,'Allurists Guild 1','NA','NA',''),
            (2,'Allurists Guild 2','NA','NA',''),
            (3,'Allurists Guild 3','NA','NA',''),
            (4,'Empaths Guild 1','NA','NA',''),
            (5,'Empaths Guild 2','NA','NA',''),
            (6,'Empaths Guild 3','NA','NA',''),
            (7,'Immolators Guild 1','NA','NA',''),
            (8,'Immolators Guild 2','NA','NA',''),
            (9,'Immolators Guild 3','NA','NA',''),
            (10,'Thieves Guild 1','NA','NA',''),
            (11,'Thieves Guild 2','NA','NA',''),
            (12,'Thieves Guild 3','NA','NA',''),
            (13,'Travellers Guild 1','NA','NA',''),
            (14,'Travellers Guild 2','NA','NA',''),
            (15,'Travellers Guild 3','NA','NA',''),
            (16,'Peacekeepers Mission 1','Emerald','67th',''),
            (17,'Peacekeepers Mission 2','Unicorn','33rd',''),
            (18,'Peacekeepers Mission 3','Emerald','33rd','')
        ]),
        ("INSERT OR IGNORE INTO placesofinterest (ID, Name, Column, Row) VALUES (?, ?, ?, ?)", [
            (1,'Battle Arena','Zelkova','52nd'),
            (2,'Hall of Binding','Vervain','40th'),
            (3,'Hall of Severance','Walrus','40th'),
            (4,'Graveyard','Larch','50th'),
            (5,'Cloister of Secrets','Gloom','1st'),
            (6,'Eternal Aubade of Mystical Treasures','Zelkova','47th'),
            (7,'Kindred Hospital','Woe','13th')
        ]),
        ("INSERT OR IGNORE INTO powers (power_id, name, guild, cost, quest_info, skill_info) VALUES (?, ?, ?, ?, ?, ?)", [
            (1,'Battle Cloak','Any Peacekeeper''s Mission',2000,'None','Buying a cloak from one of the peace missions will prevent you from attacking or being attacked by non-cloaked vampires. The cloak enforces a resting rule which limits you to bite only humans after being zeroed until you reach 250 BP. Vampires cannot bite or attack you during this time. You may still bite and rob non-cloaked vampires, as they can do the same to you. Cloaked vampires appear blue, and if zeroed, they turn pink.'),
            (2,'Celerity 1','Travellers Guild 1',4000,'Bring items to 3 pubs, no transits but you can teleport.','AP regeneration time reduced by 5 minutes per AP (25 minutes/AP).'),
            (3,'Celerity 2','Travellers Guild 2',8000,'Bring items to 6 pubs, no transits but you can teleport.','AP regeneration time reduced by 5 minutes per AP (20 minutes/AP).'),
            (4,'Celerity 3','Travellers Guild 3',17500,'Bring items to 12 pubs, no transits but you can teleport.','AP regeneration time reduced by 5 minutes per AP (15 minutes/AP).'),
            (5,'Charisma 1','Allurists Guild 1',1000,'Convince 3 vampires to visit a specific pub and say "VampName sent me".','Shop prices reduced by 3%.'),
            (6,'Charisma 2','Allurists Guild 2',3000,'Convince 6 vampires to visit a specific pub and say "VampName sent me".','Shop prices reduced by 7%.'),
            (7,'Charisma 3','Allurists Guild 3',5000,'Convince 9 vampires to visit a specific pub and say "VampName sent me".','Shop prices reduced by 10%, with an additional coin discount on each item.'),
            (8,'Locate 1','Empaths Guild 1',1500,'Visit specific locations, say "Check-Point", and drain 10 BP per location.','You can now determine the distance to a specific vampire.'),
            (9,'Locate 2','Empaths Guild 2',4000,'Visit specific locations, say "Check-Point", and drain 15 BP per location.','Locate 2 adds directional tracking and some advantages for locating close vampires in the shadows.'),
            (10,'Locate 3','Empaths Guild 3',15000,'Visit specific locations, say "Check-Point", and drain 25 BP per location.','Locate 3 reveals the exact street intersection of the vampire.'),
            (11,'Neutrality 1','Peacekeeper''s Mission 1',10000,'None','Neutrality designates a vampire as "non-violent", restricting weapon use but granting Peacekeeper protection. Can be removed at the same place and cost.'),
            (12,'Neutrality 2','Peacekeeper''s Mission 2',10000,'Additional 500 BP cost at this level.','Continues non-violent status with Peacekeeper protection.'),
            (13,'Neutrality 3','Peacekeeper''s Mission 3',10000,'Additional 1000 BP cost at this level.','Non-violent status continues, and Vial of Holy Water causes only 1 BP of damage.'),
            (14,'Perception 1','Allurists Guild',7500,'Hunt and kill 1 Vampire Hunter within 10 days.','Allows detection of hunters and potentially coin sounds in vampire pockets.'),
            (15,'Perception 2','Allurists Guild',15000,'Hunt and kill 3 Vampire Hunters within 10 days.','Detects Paladins and nearby hunters with concentration.'),
            (16,'Second Sight','Donation Required','$5','Visit donation page for $5 or find a sponsor.','Grants a bonus power of choice from a list, including Celerity-1, Stamina-1, Thievery-1, Shadows-1, Telepathy-1, Charisma-1, or Locate-1.'),
            (17,'Shadows 1','Thieves Guild 1',1000,'None','Allows you to fall into shadows after 3 days of inactivity.'),
            (18,'Shadows 2','Thieves Guild 2',2000,'None','Allows you to fall into shadows after 2 days of inactivity.'),
            (19,'Shadows 3','Thieves Guild 3',4000,'None','Allows you to fall into shadows after 1 day of inactivity.'),
            (20,'Stamina 1','Immolators Guild 1',1000,'Walk to a specified location, say code word, lose 500 BP.','Increases max AP by 10 and adds resistance to scrolls of turning (25% chance).'),
            (21,'Stamina 2','Immolators Guild 2',2500,'Walk to a specified location, say code word, lose 1000 BP.','Increases max AP by 10 and adds resistance to scrolls of turning (50% chance).'),
            (22,'Stamina 3','Immolators Guild 3',5000,'Walk to a specified location, say code word, lose 1500 BP.','Increases max AP by 10 and adds resistance to scrolls of turning (75% chance).'),
            (23,'Suction 1','Immolators Guild (ALL)',7500,'Bite 20 vampires with higher BP, spit blood into wineskin.','Gain ability to drink 2 pints from vampires and up to 4 from humans.'),
            (24,'Suction 2','Immolators Guild (ALL)',15000,'Bite 20 vampires with higher BP, spit blood into wineskin.','Gain ability to drink 4 pints from vampires and up to 10 from humans.'),
            (25,'Surprise','Empaths Guild (ALL)',20000,'None','Allows access to overcrowded squares (blue squares), but entry may still be limited if it''s too full.'),
            (26,'Telepathy 1','Travellers Guild 1',2500,'None','Allows sending messages to vampires from a distance with an AP cost of 10 for unrelated vampires and 5 for sire or childer.'),
            (27,'Telepathy 2','Travellers Guild 2',5000,'None','Allows sending messages to vampires from a distance with an AP cost of 6 for unrelated vampires and 3 for sire or childer.'),
            (28,'Telepathy 3','Travellers Guild 3',10000,'None','Allows sending messages to vampires from a distance with an AP cost of 2 for unrelated vampires and 1 for sire or childer.'),
            (29,'Thievery 1','Thievery Guild 1',2000,'None','Adds a (rob) option to vampires, allowing you to rob up to 25% of their coins.'),
            (30,'Thievery 2','Thievery Guild 2',5000,'None','Improves the (rob) option, allowing you to rob up to 50% of a vampire''s coins.'),
            (31,'Thievery 3','Thievery Guild 3',10000,'None','Improves the (rob) option further, allowing you to rob up to 75% of a vampire''s coins.'),
            (32,'Thrift 1','Allurists Guild 1',1000,'Buy 1 Perfect Red Rose from a specified shop.','5% chance to keep a used item/scroll instead of it burning up.'),
            (33,'Thrift 2','Allurists Guild 2',3000,'Buy 1 Perfect Red Rose from 3 specified shops.','10% chance to keep a used item/scroll instead of it burning up.'),
            (34,'Thrift 3','Allurists Guild 3',10000,'Buy 1 Perfect Red Rose from 6 specified shops.','15% chance to keep a used item/scroll instead of it burning up.')
        ]),
        ("INSERT OR IGNORE INTO `rows` (ID, Name, Coordinate) VALUES (?, ?, ?)", [
            ('1', 'NCL', '0'),
            ('2', 'Northern City Limits', '0'),
            ('3', '1st', '2'),
            ('4', '2nd', '4'),
            ('5', '3rd', '6'),
            ('6', '4th', '8'),
            ('7', '5th', '10'),
            ('8', '6th', '12'),
            ('9', '7th', '14'),
            ('10', '8th', '16'),
            ('11', '9th', '18'),
            ('12', '10th', '20'),
            ('13', '11th', '22'),
            ('14', '12th', '24'),
            ('15', '13th', '26'),
            ('16', '14th', '28'),
            ('17', '15th', '30'),
            ('18', '16th', '32'),
            ('19', '17th', '34'),
            ('20', '18th', '36'),
            ('21', '19th', '38'),
            ('22', '20th', '40'),
            ('23', '21st', '42'),
            ('24', '22nd', '44'),
            ('25', '23rd', '46'),
            ('26', '24th', '48'),
            ('27', '25th', '50'),
            ('28', '26th', '52'),
            ('29', '27th', '54'),
            ('30', '28th', '56'),
            ('31', '29th', '58'),
            ('32', '30th', '60'),
            ('33', '31st', '62'),
            ('34', '32nd', '64'),
            ('35', '33rd', '66'),
            ('36', '34th', '68'),
            ('37', '35th', '70'),
            ('38', '36th', '72'),
            ('39', '37th', '74'),
            ('40', '38th', '76'),
            ('41', '39th', '78'),
            ('42', '40th', '80'),
            ('43', '41st', '82'),
            ('44', '42nd', '84'),
            ('45', '43rd', '86'),
            ('46', '44th', '88'),
            ('47', '45th', '90'),
            ('48', '46th', '92'),
            ('49', '47th', '94'),
            ('50', '48th', '96'),
            ('51', '49th', '98'),
            ('52', '50th', '100'),
            ('53', '51st', '102'),
            ('54', '52nd', '104'),
            ('55', '53rd', '106'),
            ('56', '54th', '108'),
            ('57', '55th', '110'),
            ('58', '56th', '112'),
            ('59', '57th', '114'),
            ('60', '58th', '116'),
            ('61', '59th', '118'),
            ('62', '60th', '120'),
            ('63', '61st', '122'),
            ('64', '62nd', '124'),
            ('65', '63rd', '126'),
            ('66', '64th', '128'),
            ('67', '65th', '130'),
            ('68', '66th', '132'),
            ('69', '67th', '134'),
            ('70', '68th', '136'),
            ('71', '69th', '138'),
            ('72', '70th', '140'),
            ('73', '71st', '142'),
            ('74', '72nd', '144'),
            ('75', '73rd', '146'),
            ('76', '74th', '148'),
            ('77', '75th', '150'),
            ('78', '76th', '152'),
            ('79', '77th', '154'),
            ('80', '78th', '156'),
            ('81', '79th', '158'),
            ('82', '80th', '160'),
            ('83', '81st', '162'),
            ('84', '82nd', '164'),
            ('85', '83rd', '166'),
            ('86', '84th', '168'),
            ('87', '85th', '170'),
            ('88', '86th', '172'),
            ('89', '87th', '174'),
            ('90', '88th', '176'),
            ('91', '89th', '178'),
            ('92', '90th', '180'),
            ('93', '91st', '182'),
            ('94', '92nd', '184'),
            ('95', '93rd', '186'),
            ('96', '94th', '188'),
            ('97', '95th', '190'),
            ('98', '96th', '192'),
            ('99', '97th', '194'),
            ('100', '98th', '196'),
            ('101', '99th', '198'),
            ('102', '100th', '200')
        ]),
        ("INSERT OR IGNORE INTO shop_items (id, shop_name, item_name, base_price, charisma_level_1, charisma_level_2, charisma_level_3) VALUES (?, ?, ?, ?, ?, ?, ?)", [
            (1,'Discount Magic','Perfect Dandelion',35,33,32,31),
            (2,'Discount Magic','Sprint Potion',105,101,97,94),
            (3,'Discount Magic','Perfect Red Rose',350,339,325,315),
            (4,'Discount Magic','Scroll of Turning',350,339,325,315),
            (5,'Discount Magic','Scroll of Succour',525,509,488,472),
            (6,'Discount Magic','Scroll of Bondage',637,617,592,573),
            (7,'Discount Magic','Garlic Spray',700,678,651,630),
            (8,'Discount Magic','Scroll of Displacement',700,678,651,630),
            (9,'Discount Magic','Perfect Black Orchid',795,772,740,716),
            (10,'Discount Magic','Scroll of Summoning',1050,1018,976,945),
            (11,'Discount Magic','Vial of Holy Water',1400,1357,1302,1260),
            (12,'Discount Magic','Wooden Stake',2800,2715,2604,2520),
            (13,'Discount Magic','Scroll of Accounting',3500,3394,3255,3150),
            (14,'Discount Magic','Scroll of Teleportation',3500,3394,3255,3150),
            (15,'Discount Magic','UV Grenade',3500,3394,3255,3150),
            (16,'Discount Magic','Ring of Resistance',14000,13579,13020,12600),
            (17,'Discount Magic','Diamond Ring',70000,67900,65100,63000),
            (18,'Discount Potions','Sprint Potion',105,101,97,94),
            (19,'Discount Potions','Garlic Spray',700,678,651,630),
            (20,'Discount Potions','Vial of Holy Water',1400,1357,1302,1260),
            (21,'Discount Potions','Blood Potion',30000,30000,30000,30000),
            (22,'Discount Potions','Necromancer',25,25,25,25),
            (23,'Discount Scrolls','Scroll of Turning',350,339,325,315),
            (24,'Discount Scrolls','Scroll of Succour',525,509,488,472),
            (25,'Discount Scrolls','Scroll of Displacement',700,678,651,630),
            (26,'Discount Scrolls','Scroll of Summoning',1050,1018,976,945),
            (27,'Discount Scrolls','Scroll of Accounting',3500,3394,3255,3150),
            (28,'Discount Scrolls','Scroll of Teleportation',3500,3394,3255,3150),
            (29,'Dark Desires','Perfect Dandelion',50,48,46,45),
            (30,'Dark Desires','Sprint Potion',150,145,139,135),
            (31,'Dark Desires','Perfect Red Rose',500,485,465,450),
            (32,'Dark Desires','Scroll of Turning',500,485,465,450),
            (33,'Dark Desires','Scroll of Succour',750,727,697,675),
            (34,'Dark Desires','Scroll of Bondage',910,882,846,819),
            (35,'Dark Desires','Garlic Spray',1000,970,930,900),
            (36,'Dark Desires','Scroll of Displacement',1000,970,930,900),
            (37,'Dark Desires','Perfect Black Orchid',1137,1102,1057,1023),
            (38,'Dark Desires','Scroll of Summoning',1500,1455,1395,1350),
            (39,'Dark Desires','Vial of Holy Water',2000,1940,1860,1800),
            (40,'Dark Desires','Wooden Stake',4000,3880,3720,3600),
            (41,'Dark Desires','Scroll of Accounting',5000,4850,4650,4500),
            (42,'Dark Desires','Scroll of Teleportation',5000,4850,4650,4500),
            (43,'Dark Desires','UV Grenade',5000,4850,4650,4500),
            (44,'Dark Desires','Ring of Resistance',20000,19400,18600,18000),
            (45,'Dark Desires','Diamond Ring',100000,97000,93000,90000),
            (46,'Interesting Times','Perfect Dandelion',50,48,46,45),
            (47,'Interesting Times','Sprint Potion',150,145,139,135),
            (48,'Interesting Times','Perfect Red Rose',500,485,465,450),
            (49,'Interesting Times','Scroll of Turning',500,485,465,450),
            (50,'Interesting Times','Scroll of Succour',750,727,697,675),
            (51,'Interesting Times','Scroll of Bondage',910,882,846,819),
            (52,'Interesting Times','Garlic Spray',1000,970,930,900),
            (53,'Interesting Times','Scroll of Displacement',1000,970,930,900),
            (54,'Interesting Times','Perfect Black Orchid',1137,1102,1057,1023),
            (55,'Interesting Times','Scroll of Summoning',1500,1455,1395,1350),
            (56,'Interesting Times','Vial of Holy Water',2000,1940,1860,1800),
            (57,'Interesting Times','Wooden Stake',4000,3880,3720,3600),
            (58,'Interesting Times','Scroll of Accounting',5000,4850,4650,4500),
            (59,'Interesting Times','Scroll of Teleportation',5000,4850,4650,4500),
            (60,'Interesting Times','UV Grenade',5000,4850,4650,4500),
            (61,'Interesting Times','Ring of Resistance',20000,19400,18600,18000),
            (62,'Interesting Times','Diamond Ring',100000,97000,93000,90000),
            (63,'Sparks','Perfect Dandelion',50,48,46,45),
            (64,'Sparks','Sprint Potion',150,145,139,135),
            (65,'Sparks','Perfect Red Rose',500,485,465,450),
            (66,'Sparks','Scroll of Turning',500,485,465,450),
            (67,'Sparks','Scroll of Succour',750,727,697,675),
            (68,'Sparks','Scroll of Bondage',910,882,846,819),
            (69,'Sparks','Garlic Spray',1000,970,930,900),
            (70,'Sparks','Scroll of Displacement',1000,970,930,900),
            (71,'Sparks','Perfect Black Orchid',1137,1102,1057,1023),
            (72,'Sparks','Scroll of Summoning',1500,1455,1395,1350),
            (73,'Sparks','Vial of Holy Water',2000,1940,1860,1800),
            (74,'Sparks','Wooden Stake',4000,3880,3720,3600),
            (75,'Sparks','Scroll of Accounting',5000,4850,4650,4500),
            (76,'Sparks','Scroll of Teleportation',5000,4850,4650,4500),
            (77,'Sparks','UV Grenade',5000,4850,4650,4500),
            (78,'Sparks','Ring of Resistance',20000,19400,18600,18000),
            (79,'Sparks','Diamond Ring',100000,97000,93000,90000),
            (80,'The Magic Box','Perfect Dandelion',50,48,46,45),
            (81,'The Magic Box','Sprint Potion',150,145,139,135),
            (82,'The Magic Box','Perfect Red Rose',500,485,465,450),
            (83,'The Magic Box','Scroll of Turning',500,485,465,450),
            (84,'The Magic Box','Scroll of Succour',750,727,697,675),
            (85,'The Magic Box','Scroll of Bondage',910,882,846,819),
            (86,'The Magic Box','Garlic Spray',1000,970,930,900),
            (87,'The Magic Box','Scroll of Displacement',1000,970,930,900),
            (88,'The Magic Box','Perfect Black Orchid',1137,1102,1057,1023),
            (89,'The Magic Box','Scroll of Summoning',1500,1455,1395,1350),
            (90,'The Magic Box','Vial of Holy Water',2000,1940,1860,1800),
            (91,'The Magic Box','Wooden Stake',4000,3880,3720,3600),
            (92,'The Magic Box','Scroll of Accounting',5000,4850,4650,4500),
            (93,'The Magic Box','Scroll of Teleportation',5000,4850,4650,4500),
            (94,'The Magic Box','UV Grenade',5000,4850,4650,4500),
            (95,'The Magic Box','Ring of Resistance',20000,19400,18600,18000),
            (96,'The Magic Box','Diamond Ring',100000,97000,93000,90000),
            (97,'White Light','Perfect Dandelion',50,48,46,45),
            (98,'White Light','Sprint Potion',150,145,139,135),
            (99,'White Light','Perfect Red Rose',500,485,465,450),
            (100,'White Light','Scroll of Turning',500,485,465,450),
            (101,'White Light','Scroll of Succour',750,727,697,675),
            (102,'White Light','Scroll of Bondage',910,882,846,819),
            (103,'White Light','Garlic Spray',1000,970,930,900),
            (104,'White Light','Scroll of Displacement',1000,970,930,900),
            (105,'White Light','Perfect Black Orchid',1137,1102,1057,1023),
            (106,'White Light','Scroll of Summoning',1500,1455,1395,1350),
            (107,'White Light','Vial of Holy Water',2000,1940,1860,1800),
            (108,'White Light','Wooden Stake',4000,3880,3720,3600),
            (109,'White Light','Scroll of Accounting',5000,4850,4650,4500),
            (110,'White Light','Scroll of Teleportation',5000,4850,4650,4500),
            (111,'White Light','UV Grenade',5000,4850,4650,4500),
            (112,'White Light','Ring of Resistance',20000,19400,18600,18000),
            (113,'White Light','Diamond Ring',100000,97000,93000,90000),
            (114,'McPotions','Sprint Potion',150,145,139,135),
            (115,'McPotions','Garlic Spray',1000,970,930,900),
            (116,'McPotions','Vial of Holy Water',2000,1940,1860,1800),
            (117,'McPotions','Blood Potion',30000,30000,30000,30000),
            (118,'McPotions','Necromancer',25,25,25,25),
            (119,'Potable Potions','Sprint Potion',150,145,139,135),
            (120,'Potable Potions','Garlic Spray',1000,970,930,900),
            (121,'Potable Potions','Vial of Holy Water',2000,1940,1860,1800),
            (122,'Potable Potions','Blood Potion',30000,30000,30000,30000),
            (123,'Potable Potions','Necromancer',25,25,25,25),
            (124,'Potion Distillery','Sprint Potion',150,145,139,135),
            (125,'Potion Distillery','Garlic Spray',1000,970,930,900),
            (126,'Potion Distillery','Vial of Holy Water',2000,1940,1860,1800),
            (127,'Potion Distillery','Blood Potion',30000,30000,30000,30000),
            (128,'Potion Distillery','Necromancer',25,25,25,25),
            (129,'Potionworks','Sprint Potion',150,145,139,135),
            (130,'Potionworks','Garlic Spray',1000,970,930,900),
            (131,'Potionworks','Vial of Holy Water',2000,1940,1860,1800),
            (132,'Potionworks','Blood Potion',30000,30000,30000,30000),
            (133,'Potionworks','Necromancer',25,25,25,25),
            (134,'Silver Apothecary','Sprint Potion',150,145,139,135),
            (135,'Silver Apothecary','Garlic Spray',1000,970,930,900),
            (136,'Silver Apothecary','Vial of Holy Water',2000,1940,1860,1800),
            (137,'Silver Apothecary','Blood Potion',30000,30000,30000,30000),
            (138,'Silver Apothecary','Perfect Dandelion',50,48,46,45),
            (139,'Silver Apothecary','Perfect Red Rose',500,485,465,450),
            (140,'Silver Apothecary','Perfect Black Orchid',1137,1102,1057,1023),
            (141,'Silver Apothecary','Diamond Ring',100000,97000,93000,90000),
            (142,'Silver Apothecary','Necromancer',25,25,25,25),
            (143,'The Potion Shoppe','Sprint Potion',150,145,139,135),
            (144,'The Potion Shoppe','Garlic Spray',1000,970,930,900),
            (145,'The Potion Shoppe','Vial of Holy Water',2000,1940,1860,1800),
            (146,'The Potion Shoppe','Blood Potion',30000,30000,30000,30000),
            (147,'The Potion Shoppe','Necromancer',25,25,25,25),
            (148,'Herman''s Scrolls','Scroll of Turning',500,485,465,450),
            (149,'Herman''s Scrolls','Scroll of Succour',750,727,697,675),
            (150,'Herman''s Scrolls','Scroll of Displacement',1000,970,930,900),
            (151,'Herman''s Scrolls','Scroll of Summoning',1500,1455,1395,1350),
            (152,'Herman''s Scrolls','Scroll of Accounting',5000,4850,4650,4500),
            (153,'Herman''s Scrolls','Scroll of Teleportation',5000,4850,4650,4500),
            (154,'Paper and Scrolls','Scroll of Turning',500,485,465,450),
            (155,'Paper and Scrolls','Scroll of Succour',750,727,697,675),
            (156,'Paper and Scrolls','Scroll of Displacement',1000,970,930,900),
            (157,'Paper and Scrolls','Scroll of Summoning',1500,1455,1395,1350),
            (158,'Paper and Scrolls','Scroll of Accounting',5000,4850,4650,4500),
            (159,'Paper and Scrolls','Scroll of Teleportation',5000,4850,4650,4500),
            (160,'Scrollmania','Scroll of Turning',500,485,465,450),
            (161,'Scrollmania','Scroll of Succour',750,727,697,675),
            (162,'Scrollmania','Scroll of Displacement',1000,970,930,900),
            (163,'Scrollmania','Scroll of Summoning',1500,1455,1395,1350),
            (164,'Scrollmania','Scroll of Accounting',5000,4850,4650,4500),
            (165,'Scrollmania','Scroll of Teleportation',5000,4850,4650,4500),
            (166,'Scrolls ''n'' Stuff','Scroll of Turning',500,485,465,450),
            (167,'Scrolls ''n'' Stuff','Scroll of Succour',750,727,697,675),
            (168,'Scrolls ''n'' Stuff','Scroll of Displacement',1000,970,930,900),
            (169,'Scrolls ''n'' Stuff','Scroll of Summoning',1500,1455,1395,1350),
            (170,'Scrolls ''n'' Stuff','Scroll of Accounting',5000,4850,4650,4500),
            (171,'Scrolls ''n'' Stuff','Scroll of Teleportation',5000,4850,4650,4500),
            (172,'Scrolls R Us','Scroll of Turning',500,485,465,450),
            (173,'Scrolls R Us','Scroll of Succour',750,727,697,675),
            (174,'Scrolls R Us','Scroll of Displacement',1000,970,930,900),
            (175,'Scrolls R Us','Scroll of Summoning',1500,1455,1395,1350),
            (176,'Scrolls R Us','Scroll of Accounting',5000,4850,4650,4500),
            (177,'Scrolls R Us','Scroll of Teleportation',5000,4850,4650,4500),
            (178,'Scrollworks','Scroll of Turning',500,485,465,450),
            (179,'Scrollworks','Scroll of Succour',750,727,697,675),
            (180,'Scrollworks','Scroll of Displacement',1000,970,930,900),
            (181,'Scrollworks','Scroll of Summoning',1500,1455,1395,1350),
            (182,'Scrollworks','Scroll of Accounting',5000,4850,4650,4500),
            (183,'Scrollworks','Scroll of Teleportation',5000,4850,4650,4500),
            (184,'Ye Olde Scrolles','Scroll of Turning',500,485,465,450),
            (185,'Ye Olde Scrolles','Scroll of Succour',750,727,697,675),
            (186,'Ye Olde Scrolles','Scroll of Displacement',1000,970,930,900),
            (187,'Ye Olde Scrolles','Scroll of Summoning',1500,1455,1395,1350),
            (188,'Ye Olde Scrolles','Scroll of Accounting',5000,4850,4650,4500),
            (189,'Ye Olde Scrolles','Scroll of Teleportation',5000,4850,4650,4500),
            (190,'Eternal Aubade of Mystical Treasures','Perfect Dandelion',55,55,55,55),
            (191,'Eternal Aubade of Mystical Treasures','Sprint Potion',165,165,165,165),
            (192,'Eternal Aubade of Mystical Treasures','Perfect Red Rose',550,550,550,550),
            (193,'Eternal Aubade of Mystical Treasures','Scroll of Succour',825,25,25,25),
            (194,'Eternal Aubade of Mystical Treasures','Scroll of Bondage',1001,1001,1001,1001),
            (195,'Eternal Aubade of Mystical Treasures','Perfect Black Orchid',1250,1250,1250,1250),
            (196,'Eternal Aubade of Mystical Treasures','Gold Dawn to Dusk Tulip',1500,1500,1500,1500),
            (197,'Eternal Aubade of Mystical Treasures','Wooden Stake',4400,4400,4400,4400),
            (198,'Eternal Aubade of Mystical Treasures','Kitten',10000,10000,10000,10000),
            (199,'Eternal Aubade of Mystical Treasures','Wolf Pup',12500,12500,12500,12500),
            (200,'Eternal Aubade of Mystical Treasures','Dragon''s Egg',17499,17499,17499,17499),
            (201,'Eternal Aubade of Mystical Treasures','Silver Pocket Watch',20000,20000,20000,20000),
            (202,'Eternal Aubade of Mystical Treasures','Crystal Music Box',25000,25000,25000,25000),
            (203,'Eternal Aubade of Mystical Treasures','Blood Potion',33000,33000,33000,33000),
            (204,'Eternal Aubade of Mystical Treasures','Hand Mirror of Truth',35000,35000,35000,35000),
            (205,'Eternal Aubade of Mystical Treasures','Book of Spells',44999,44999,44999,44999),
            (206,'Eternal Aubade of Mystical Treasures','Ritual Gown',55000,55000,55000,55000),
            (207,'Eternal Aubade of Mystical Treasures','Silver Ruby Dagger',65000,65000,65000,65000),
            (208,'Eternal Aubade of Mystical Treasures','Onyx Coffin',75000,75000,75000,75000),
            (209,'Eternal Aubade of Mystical Treasures','Platinum Puzzle Rings',115000,115000,115000,115000),
            (210,'Eternal Aubade of Mystical Treasures','Diamond Succubus Earrings',125000,125000,125000,125000),
            (211,'The Cloister of Secrets','Perfect Dandelion',55,55,55,55),
            (212,'The Cloister of Secrets','Perfect Red Rose',550,550,550,550),
            (213,'The Cloister of Secrets','Perfect Black Orchid',1250,1250,1250,1250),
            (214,'The Cloister of Secrets','Safety Deposit Box Key',11000,11000,11000,11000),
            (215,'The Cloister of Secrets','Necklace with Locket',55000,55000,55000,55000),
            (216,'The Cloister of Secrets','Flask of Heinous Deceptions',77000,77000,77000,77000),
            (217,'The Cloister of Secrets','Amulet of Insidious Illusions',88000,88000,88000,88000),
            (218,'The Cloister of Secrets','Golden Ring',99000,99000,99000,99000),
            (219,'The Cloister of Secrets','Diamond Ring',110000,110000,110000,110000),
            (220,'The Cloister of Secrets','Titanium-Platinum Ring',110000,110000,110000,110000),
            (221,'Grotto of Deceptions','Scroll of Turning',550,550,550,550),
            (222,'Grotto of Deceptions','Scroll of Teleportation',5500,5500,5500,5500),
            (223,'Grotto of Deceptions','Scroll of Displacement',1100,1100,1100,1100),
            (224,'Grotto of Deceptions','Scroll of Succour',825,825,825,825),
            (225,'Grotto of Deceptions','Vial of Holy Water',2200,2200,2200,2200),
            (226,'Grotto of Deceptions','Garlic Spray',1100,1100,1100,1100),
            (227,'Grotto of Deceptions','Sprint Potion',165,165,165,165),
            (228,'Grotto of Deceptions','Perfect Dandelion',55,55,55,55),
            (229,'Grotto of Deceptions','Perfect Red Rose',550,550,550,550),
            (230,'Grotto of Deceptions','Perfect Black Orchid',1100,1100,1100,1100),
            (231,'NightWatch Headquarters','Memorial Candle',200,200,200,200),
            (232,'NightWatch Headquarters','Perfect Red Rose',550,550,550,550),
            (233,'The Ixora Estate','Perfect Ixora Cluster',550,550,550,550),
            (234,'The Ixora Estate','Perfect Dandelion',55,55,55,55),
            (235,'The Ixora Estate','Perfect Black Orchid',1100,1100,1100,1100),
            (236,'The Ixora Estate','Perfect Red Rose',550,550,550,550),
            (237,'The White House','Perfect Red Rose',550,550,550,550),
            (238,'The White House','Perfect Black Orchid',1250,1250,1250,1250),
            (239,'The White House','Pewter Celtic Cross',10000,10000,10000,10000),
            (240,'The White House','Compass',11999,11999,11999,11999),
            (241,'The White House','Pewter Tankard',15000,15000,15000,15000)
        ]),
        ("INSERT OR IGNORE INTO shops (ID, Name, Column, Row, next_update) VALUES (?, ?, ?, ?, ?)", [
            (1,'Ace Porn','NA','NA',''),
            (2,'Checkers Porn Shop','NA','NA',''),
            (3,'Dark Desires','NA','NA',''),
            (4,'Discount Magic','NA','NA',''),
            (5,'Discount Potions','NA','NA',''),
            (6,'Discount Scrolls','NA','NA',''),
            (7,'Herman''s Scrolls','NA','NA',''),
            (8,'Interesting Times','NA','NA',''),
            (9,'McPotions','NA','NA',''),
            (10,'Paper and Scrolls','NA','NA',''),
            (11,'Potable Potions','NA','NA',''),
            (12,'Potion Distillery','NA','NA',''),
            (13,'Potionworks','NA','NA',''),
            (14,'Reversi Porn','NA','NA',''),
            (15,'Scrollmania','NA','NA',''),
            (16,'Scrolls ''n'' Stuff','NA','NA',''),
            (17,'Scrolls R Us','NA','NA',''),
            (18,'Scrollworks','NA','NA',''),
            (19,'Silver Apothecary','NA','NA',''),
            (20,'Sparks','NA','NA',''),
            (21,'Spinners Porn','NA','NA',''),
            (22,'The Magic Box','NA','NA',''),
            (23,'The Potion Shoppe','NA','NA',''),
            (24,'White Light','NA','NA',''),
            (25,'Ye Olde Scrolles','NA','NA','')
        ]),
        ("INSERT OR IGNORE INTO taverns (ID, Column, Row, Name) VALUES (?, ?, ?, ?)", [
            (1,'Gum','33rd','Abbot''s Tavern'),
            (2,'Knotweed','11th','Archer''s Tavern'),
            (3,'Torment','16th','Baker''s Tavern'),
            (4,'Fir','13th','Balmer''s Tavern'),
            (5,'Nettle','3rd','Barker''s Tavern'),
            (6,'Duck','7th','Bloodwood Canopy Cafe'),
            (7,'Haddock','64th','Bowyer''s Tavern'),
            (8,'Qualms','61st','Butler''s Tavern'),
            (9,'Yew','78th','Carter''s Tavern'),
            (10,'Raven','71st','Chandler''s Tavern'),
            (11,'Bleak','64th','Club Xendom'),
            (12,'Pilchard','48th','Draper''s Tavern'),
            (13,'Yak','90th','Falconer''s Tavern'),
            (14,'Ruby','20th','Fiddler''s Tavern'),
            (15,'Ferret','84th','Fisherman''s Tavern'),
            (16,'Pine','68th','Five French Hens'),
            (17,'Steel','26th','Freeman''s Tavern'),
            (18,'Gibbon','98th','Harper''s Tavern'),
            (19,'Ire','63rd','Hawker''s Tavern'),
            (20,'Hessite','55th','Hell''s Angels Clubhouse'),
            (21,'Fir','72nd','Hunter''s Tavern'),
            (22,'Lion','1st','Leacher''s Tavern'),
            (23,'Malachite','76th','Lovers at Dawn Inn'),
            (24,'Ragweed','78th','Marbler''s Tavern'),
            (25,'Ferret','44th','Miller''s Tavern'),
            (26,'Steel','3rd','Oyler''s Tavern'),
            (27,'Diamond','92nd','Painter''s Tavern'),
            (28,'Walrus','83rd','Peace De Résistance'),
            (29,'Fear','34th','Pub Forty-Two'),
            (30,'Qualms','61st','Ratskeller'),
            (31,'Beryl','98th','Rider''s Tavern'),
            (32,'Qualms','5th','Rogue''s Tavern'),
            (33,'Eagle','67th','Shooter''s Tavern'),
            (34,'Bleak','NCL','Smuggler''s Cove'),
            (35,'Anguish','98th','Ten Turtle Doves'),
            (36,'Oppression','45th','The Angel''s Wing'),
            (37,'Oppression','70th','The Axeman and Guillotine'),
            (38,'Ivory','99th','The Blinking Pixie'),
            (39,'Pessimism','37th','The Book and Beggar'),
            (40,'Malachite','70th','The Booze Hall'),
            (41,'Pyrites','41st','The Brain and Hatchling'),
            (42,'Lonely','87th','The Brimming Brew'),
            (43,'Qualms','43rd','The Broken Lover'),
            (44,'Ruby','90th','The Burning Brand'),
            (45,'Walrus','68th','The Cart and Castle'),
            (46,'Lion','1st','The Celtic Moonligh'),
            (47,'Beech','19th','The Clam and Champion'),
            (48,'Nightingale','32nd','The Cosy Walrus'),
            (49,'Sorrow','70th','The Crossed Swords Tavern'),
            (50,'Gum','10th','The Crouching Tiger'),
            (51,'Killjoy','46th','The Crow''s Nest Tavern'),
            (52,'Pine','51st','The Dead of Night'),
            (53,'Lonely','78th','The Demon''s Heart'),
            (54,'Ragweed','6th','The Dog House'),
            (55,'Zinc','94th','The Drunk Cup'),
            (56,'Yak','30th','The Ferryman''s Arms'),
            (57,'Nervous','2nd','The Flirty Angel'),
            (58,'Sorrow','91st','The Freudian Slip'),
            (59,'Walrus','62nd','The Ghastly Flabber'),
            (60,'Lion','95th','The Golden Partridge'),
            (61,'Zebra','50th','The Guardian Outpost'),
            (62,'Obsidian','54th','The Gunny''s Shack'),
            (63,'Vexation','2nd','The Hearth and Sabre'),
            (64,'Dogwood','54th','The Kestrel'),
            (65,'Mongoose','15th','The Last Days'),
            (66,'Unicorn','92nd','The Lazy Sunflower'),
            (67,'Nervous','42nd','The Lightbringer'),
            (68,'Kyanite','19th','The Lounge'),
            (69,'Yearning','48th','The Marsupial'),
            (70,'Hessite','97th','The McAllister Tavern'),
            (71,'Dogwood','78th','The Moon over Orion'),
            (72,'Gibbon','44th','The Ox and Bow'),
            (73,'Jackal','53rd','The Palm and Parson'),
            (74,'Quail','85th','The Poltroon'),
            (75,'Ruby','21st','The Round Room'),
            (76,'Diamond','1st','The Scupper and Forage'),
            (77,'Pine','91st','The Shattered Platter'),
            (78,'Nickel','57th','The Shining Devil'),
            (79,'Alder','57th','The Sign of the Times'),
            (80,'Ennui','80th','The Stick and Stag'),
            (81,'Oppression','70th','The Stick in the Mud'),
            (82,'Malaise','87th','The Sun'),
            (83,'Eagle','34th','The Sunken Sofa'),
            (84,'Turquoise','71st','The Swords at Dawn'),
            (85,'Elm','93rd','The Teapot and Toxin'),
            (86,'Mongoose','92nd','The Thief of Hearts'),
            (87,'Despair','38th','The Thorn''s Pride'),
            (88,'Zebra','36th','The Two Sisters'),
            (89,'Nettle','86th','The Wart and Whisk'),
            (90,'Sycamore','89th','The Whirling Dervish'),
            (91,'Vulture','11th','The Wild Hunt'),
            (92,'Steel','23rd','Treehouse'),
            (93,'Yew','5th','Vagabond''s Tavern'),
            (94,'Anguish','68th','Xendom Tavern'),
            (95,'Pyrites','70th','Ye Olde Gallows Ale House')
        ]),
        ("INSERT OR IGNORE INTO transits (ID, Column, Row, Name) VALUES (?, ?, ?, ?)", [
            (1,'Mongoose','25th','Calliope'),
            (2,'Zelkova','25th','Clio'),
            (3,'Malachite','25th','Erato'),
            (4,'Mongoose','50th','Euterpe'),
            (5,'Zelkova','50th','Melpomene'),
            (6,'Malachite','50th','Polyhymnia'),
            (7,'Mongoose','75th','Terpsichore'),
            (8,'Zelkova','75th','Thalia'),
            (9,'Malachite','75th','Urania')
        ]),
        ("INSERT OR IGNORE INTO userbuildings (ID, Name, Column, Row) VALUES (?, ?, ?, ?)", [
            (1, 'Ace''s House of Dumont', 'Cedar', '99th'),
            (2, 'Alatáriël Maenor', 'Diamond', '50th'),
            (3, 'Alpha Dragon''s and Lyric''s House of Dragon and Flame', 'Amethyst', '90th'),
            (4, 'AmadisdeGaula''s Stellaburgi', 'Wulfenite', '38th'),
            (5, 'Andre''s Crypt', 'Ferret', '10th'),
            (6, 'Annabelle''s Paradise', 'Emerald', '85th'),
            (7, 'Anthony''s Castle Pacherontis', 'Walrus', '39th'),
            (8, 'Anthony''s Gero Claw', 'Vulture', '39th'),
            (9, 'Anthony''s Training Grounds', 'Vulture', '35th'),
            (10, 'Aphaythean Vineyards', 'Willow', '13th'),
            (11, 'Archangel''s Castle', 'Beech', '4th'),
            (12, 'Avant''s Garden', 'Amethyst', '68th'),
            (13, 'BaShalor''s Rose Garden', 'Cobalt', '41st'),
            (14, 'Bitercat''s mews', 'Lion', '42nd'),
            (15, 'Black dragonet''s mansion', 'Oppression', '80th'),
            (16, 'Blutengel''s Temple of Blood', 'Fear', '13th'),
            (17, 'Café Damari', 'Zelkova', '68th'),
            (18, 'Cair Paravel', 'Lion', '27th'),
            (19, 'Capadocian Castle', 'Larch', '49th'),
            (20, 'Carnal Desires', 'Ivy', '66th'),
            (21, 'Castle of Shadows', 'Turquoise', '86th'),
            (22, 'Castle RavenesQue', 'Raven', 'NCL'),
            (23, 'ChaosRaven''s Dimensional Tower', 'Killjoy', '23rd'),
            (24, 'CHASS''s forever-blues hall', 'Torment', '75th'),
            (25, 'CrimsonClover''s Hideaway', 'Diamond', '85th'),
            (26, 'CrowsSong''s Blackbird Towers', 'Wulfenite', '3rd'),
            (27, 'D''dary Manor', 'Aardvark', '1st'),
            (28, 'Daphne''s Dungeons', 'Malachite', '64th'),
            (29, 'DarkestDesire''s Chambers', 'Despair', '56th'),
            (30, 'Darkwolf''s and liquid-vamp''s Country Cottage', 'Wulfenite', '69th'),
            (31, 'Deaths embrace''s Shadow Keep', 'Holly', '81st'),
            (32, 'Devil Miyu''s Abeir-Toril', 'Fear', '2nd'),
            (33, 'Devil Miyu''s Edge of Reason', 'Fear', 'NCL'),
            (34, 'Devil Miyu''s Lair', 'Fear', '1st'),
            (35, 'Dreamcatcher Haven', 'Torment', '2nd'),
            (36, 'Elijah''s Hall of the Lost', 'Zinc', '99th'),
            (37, 'ElishaDraken''s Sanguine Ankh', 'Nightingale', '59th'),
            (38, 'Epineux Manoir', 'Olive', '70th'),
            (39, 'Espy''s Jaded Sorrows', 'Jaded', '69th'),
            (40, 'Freedom Trade Alliance', 'Amethyst', '46th'),
            (41, 'Gypsychild''s Caravan', 'Torment', '69th'),
            (42, 'Halls of Shadow Court', 'Horror', '99th'),
            (43, 'Hells Gate''s Castle of Destruction', 'Lonely', '45th'),
            (44, 'Hesu''s Place', 'Raven', '24th'),
            (45, 'Hexenkessel', 'Jackal', '83rd'),
            (47, 'Ildiko''s and Brom''s Insanity', 'Killjoy', '53rd'),
            (48, 'Jacomo Varis'' Shadow Manor', 'Raven', '96th'),
            (49, 'Jaxi''s and Speedy''s Cave', 'Raven', '23rd'),
            (50, 'Julia''s Villa', 'Gloom', '76th'),
            (51, 'King Lestat''s Le Paradis Caché', 'Cobalt', '90th'),
            (52, 'La Cucina', 'Diamond', '28th'),
            (53, 'Lady Ophy''s Bougainvillea Mansion', 'Jaded', '84th'),
            (54, 'LadyFae''s and nitenurse''s Solas Gealaí Caisleán', 'Raven', '76th'),
            (55, 'Lasc Talon''s Estate', 'Willow', '42nd'),
            (56, 'Lass'' Lair', 'Vervain', '1st'),
            (57, 'Liski''s Shadow Phial', 'Gloom', '99th'),
            (58, 'Lord Galamushi''s Enchanted Mansion', 'Anguish', '52nd'),
            (59, 'Louvain''s Sanctuary', 'Gibbon', '21st'),
            (60, 'Majica''s Playground', 'Willow', '50th'),
            (61, 'Mandruleanu Manor', 'Diamond', '86th'),
            (62, 'Mansion of Malice', 'Horror', '69th'),
            (63, 'Marlena''s Wishing Well', 'Fear', '56th'),
            (64, 'Moirai''s Gate to the Church of Blood', 'Horror', '13th'),
            (65, 'Moondreamer''s Darkest Desire''s Lighthouse', 'Fear', '9th'),
            (66, 'Moonlight Gardens', 'Turquoise', '87th'),
            (67, 'Ms Delgado''s Manor', 'Sorrow', '69th'),
            (68, 'MyMotherInLaw''s Home for Wayward Ghouls', 'Amethyst', '69th'),
            (69, 'Narcisssa''s Vineyard', 'Aardvark', '60th'),
            (70, 'Nemesis'' Asyl', 'Zinc', '85th'),
            (71, 'NightWatch Headquarters', 'Larch', '51st'),
            (72, 'Obsidian''s Arboretum', 'Obsidian', '88th'),
            (73, 'Obsidian''s Castle of Warwick', 'Obsidian', 'NCL'),
            (74, 'Obsidian''s Château de la Lumière', 'Obsidian', '66th'),
            (75, 'Obsidian''s château noir', 'Obsidian', '99th'),
            (76, 'Obsidian''s Hall of Shifting Realms', 'Obsidian', '15th'),
            (77, 'Obsidian''s Penthouse', 'Obsidian', '29th'),
            (78, 'Obsidian''s Silver Towers', 'Obsidian', '51st'),
            (79, 'Obsidian''s Tranquility', 'Obsidian', '80th'),
            (80, 'Obsidian''s, Phoenixxe''s and Em''s Heaven''s Gate', 'Obsidian', '45th'),
            (81, 'Occamrazor''s House of Ears', 'Yew', '30th'),
            (82, 'Ordo Dracul Sanctum', 'Nightingale', '77th'),
            (83, 'Orgasmerilla''s Warehouse', 'Zinc', '80th'),
            (84, 'Pace Family Ranch', 'Fir', '69th'),
            (85, 'Palazzo Lucius', 'Zebra', '27th'),
            (86, 'Pandrora and CBK''s Chamber of Horrors', 'Torment', '95th'),
            (87, 'RemipunX''s Sacred Yew', 'Cobalt', '42nd'),
            (88, 'Renovate''s grove', 'Umbrella', '71st'),
            (89, 'Saki''s Fondest Wish', 'Nightingale', '17th'),
            (90, 'Samantha Dawn''s Salacious Sojourn', 'Anguish', '53rd'),
            (91, 'Sanctuary Hotel', 'Kraken', '27th'),
            (92, 'Sartori''s Domicile', 'Elm', '1st'),
            (93, 'SCORPIOUS1''s Tower of Truth', 'Yearning', '58th'),
            (94, 'Setitevampyr''s temple', 'Raven', '50th'),
            (95, 'Shaarinya`s Sanguine Sanctuary', 'Raven', '77th'),
            (96, 'Shadow bat''s Sanctorium', 'Cobalt', '76th'),
            (97, 'SIE Compound', 'Raven', '13th'),
            (98, 'Sitrence''s Lab', 'Ferret', '3rd'),
            (99, 'Solanea''s Family Home', 'Ruby', '56th'),
            (100, 'The Angelarium', 'Zinc', 'NCL'),
            (101, 'St. John Bathhouse', 'Sycamore', '76th'),
            (102, 'Starreagle''s Paradise Lair', 'Beryl', '24th'),
            (103, 'Steele Industries', 'Umbrella', '44th'),
            (104, 'Stormy jayne''s web', 'Nickel', '99th'),
            (105, 'Talon Castle', 'Willow', '35th'),
            (106, 'tejas_dragon''s Lair', 'Zelkova', '69th'),
            (107, 'The Ailios Asylum', 'Amethyst', '36th'),
            (108, 'The Belly of the Whale', 'Amethyst', '2nd'),
            (109, 'The Calignite', 'Eagle', '16th'),
            (110, 'The COVE', 'Knowteed', '51st'),
            (111, 'The Dragons Lair Club', 'Vervain', '39th'),
            (112, 'The Eternal Spiral', 'Anguish', '69th'),
            (113, 'The goatsucker''s lair', 'Yak', '13th'),
            (114, 'The Halls of Heorot', 'Jaded', '75th'),
            (115, 'The House of Night', 'Walrus', '38th'),
            (116, 'The Inner Circle Manor', 'Diamond', '26th'),
            (117, 'The Ivory Tower', 'Zelkova', '76th'),
            (118, 'The Ixora Estate', 'Lead', '48th'),
            (119, 'The Kyoto Club', 'Lion', '22nd'),
            (120, 'The Lokason Myrkrasetur', 'Wulfenite', '40th'),
            (121, 'The Path of Enlightenment Castle', 'Willow', '80th'),
            (122, 'The RavenBlack Bite', 'Oppression', '40th'),
            (123, 'The Reynolds'' Estate', 'Beryl', '23rd'),
            (124, 'The River Passage', 'Yew', '33rd'),
            (125, 'The Sakura Garden', 'Nickel', '77th'),
            (126, 'The Sanctum of Vermathrax-rex and Bellina', 'Vexation', '99th'),
            (127, 'The Sanguinarium', 'Fear', '4th'),
            (128, 'The Scythe''s Negotiation Offices', 'Vauxite', '88th'),
            (129, 'The Sepulchre of Shadows', 'Ennui', '1st'),
            (130, 'The Tower of Thorns', 'Pilchard', '70th'),
            (131, 'The Towers of the Crossed Swords', 'Torment', '66th'),
            (132, 'The White House', 'Nervous', '75th'),
            (133, 'University of Vampiric Enlightenment', 'Yak', '80th'),
            (134, 'Virgo''s obsidian waygate', 'Obsidian', '2nd'),
            (135, 'Vulture''s Pagoda', 'Vulture', '50th'),
            (136, 'Wilde Sanctuary', 'Willow', '51st'),
            (137, 'Wilde Wolfe Estate', 'Vervain', '50th'),
            (138, 'Willhelm''s Warrior House', 'Horror', '53rd'),
            (139, 'Willow Lake Manse', 'Willow', '99th'),
            (140, 'Willow Woods'' & The Ent Moot', 'Willow', '54th'),
            (141, 'Wolfshadow''s and Crazy''s RBC Casino', 'Lead', '72nd'),
            (142, 'Wyndcryer''s TygerNight''s and Bambi''s Lair', 'Unicorn', '77th'),
            (143, 'Wyvernhall', 'Ivy', '38th'),
            (144, 'X', 'Emerald', 'NCL'),
            (145, 'Requiem of Hades', 'Walrus', '41st')
        ]),
        ("INSERT OR IGNORE INTO discord_servers (id, name, invite_link) VALUES (?, ?, ?)", [
            (1, "Ab Antiquo Headquarters", "https://discord.gg/AhPEzkJyA4"),
            (2, "Hellfire Club", "https://discord.gg/qZCbbKEt3z"),
            (3, "RB Improvement Group", "https://discord.gg/8ent8jn54u"),
            (4, "RBCH", "https://discord.gg/ktdG9FZ"),
            (5, "Raven Black: Boroughs and Barrios", "https://discord.gg/RTSXJ5tC4d"),
            (6, "RavenBlack Community Center", "https://discord.gg/SVMmGcvNCV"),
            (7, "The Moon over Orion", "https://discord.gg/EArPr7vqHC"),
            (8, "The Ravenblack Historical Society", "https://discord.gg/zqPXpw8sMw"),
            (9, "rêverie", "https://discord.gg/jAVHpGvgCf")
        ])

    ]
    for query, data in initial_data:
        try:
            cursor.executemany(query, data)
            logging.debug(f"Inserted initial data into: {query.split('INTO ')[1].split(' ')[0]}")
        except sqlite3.Error as e:
            logging.error(f"Failed to insert data into {query.split('INTO ')[1].split(' ')[0]}: {e}")
            raise
    conn.commit()

def migrate_schema(conn: sqlite3.Connection) -> None:
    """
    Migrate the database schema to the latest version.

    Handles sequential migrations:
    - v1 -> v2: Fixes custom_css, guilds, and shops tables.
    - v2 -> v3: Adds active_cookie column to characters table.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA user_version")
    version = cursor.fetchone()[0]

    if version < 2:
        logging.info("Applying schema migration: v1 → v2 (fixing custom_css, guilds, and shops)")

        try:
            # --- Step 1: Fix custom_css table ---
            cursor.execute("PRAGMA table_info(custom_css)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'profile_name' not in columns:
                logging.info("custom_css missing profile_name column. Rebuilding custom_css table.")
                cursor.execute("ALTER TABLE custom_css RENAME TO custom_css_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_css (
                        profile_name TEXT NOT NULL,
                        element TEXT NOT NULL,
                        value TEXT NOT NULL,
                        PRIMARY KEY (profile_name, element),
                        FOREIGN KEY (profile_name) REFERENCES css_profiles(profile_name) ON DELETE CASCADE
                    )
                """)
                try:
                    cursor.execute("""
                        INSERT INTO custom_css (element, value, profile_name)
                        SELECT element, value, 'Default' FROM custom_css_old
                    """)
                    logging.info("Migrated old custom_css data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate custom_css data: {e}")
                cursor.execute("DROP TABLE IF EXISTS custom_css_old")

            # --- Step 2: Fix guilds table ---
            cursor.execute("PRAGMA index_list(guilds)")
            indexes = cursor.fetchall()
            unique_names = [index[1] for index in indexes if index[2]]  # index[2] == 1 means UNIQUE
            if not any('Name' in idx for idx in unique_names):
                logging.info("guilds table missing UNIQUE constraint on Name. Rebuilding guilds table.")
                cursor.execute("ALTER TABLE guilds RENAME TO guilds_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS guilds (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL UNIQUE,
                        Column TEXT NOT NULL,
                        Row TEXT NOT NULL,
                        next_update TIMESTAMP DEFAULT NULL
                    )
                """)
                try:
                    cursor.execute("""
                        INSERT INTO guilds (ID, Name, Column, Row, next_update)
                        SELECT ID, Name, Column, Row, next_update FROM guilds_old
                    """)
                    logging.info("Migrated old guilds data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate guilds data: {e}")
                cursor.execute("DROP TABLE IF EXISTS guilds_old")

            # --- Step 3: Fix shops table ---
            cursor.execute("PRAGMA index_list(shops)")
            shops_indexes = cursor.fetchall()
            shops_has_unique_name = any('Name' in idx for idx in shops_indexes if idx[2])

            if not shops_has_unique_name:
                logging.info("shops table missing UNIQUE constraint on Name. Rebuilding shops table.")
                cursor.execute("ALTER TABLE shops RENAME TO shops_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shops (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL UNIQUE,
                        Column TEXT NOT NULL,
                        Row TEXT NOT NULL,
                        next_update TIMESTAMP DEFAULT NULL
                    )
                """)
                try:
                    cursor.execute("""
                        INSERT INTO shops (ID, Name, Column, Row, next_update)
                        SELECT ID, Name, Column, Row, next_update FROM shops_old
                    """)
                    logging.info("Migrated old shops data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate shops data: {e}")
                cursor.execute("DROP TABLE IF EXISTS shops_old")

            # --- Finish migration ---
            conn.execute("PRAGMA user_version = 2")
            conn.commit()
            logging.info("Migration to v2 complete.")

        except sqlite3.Error as e:
            logging.error(f"Migration v2 failed: {e}")
            conn.rollback()
            raise

    if version < 3:
        logging.info("Applying schema migration: v2 → v3 (add active_cookie to characters)")

        try:
            cursor.execute("PRAGMA table_info(characters)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'active_cookie' not in columns:
                logging.info("characters table missing active_cookie column. Adding column.")
                cursor.execute("ALTER TABLE characters ADD COLUMN active_cookie INTEGER DEFAULT NULL")
            else:
                logging.info("characters table already has active_cookie column. Skipping.")

            conn.execute("PRAGMA user_version = 3")
            conn.commit()
            logging.info("Migration to v3 complete.")

        except sqlite3.Error as e:
            logging.error(f"Migration v3 failed: {e}")
            conn.rollback()
            raise

def initialize_database(db_path: str = DB_PATH) -> bool:
    """
    Initialize the SQLite database with the required schema and data.

    Args:
        db_path (str, optional): Path to the SQLite database file. Defaults to DB_PATH.

    Returns:
        bool: True if initialization succeeds, False if an error occurs.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
            create_tables(conn)                       # Fist create missing tables
            migrate_schema(conn)                      # Then migrate schema
            insert_initial_data(conn)                 # THEN populate defaults
            logging.info(f"Database initialized successfully at {db_path}")
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to initialize database at {db_path}: {e}")
        return False

# Call database initialization
if not ensure_directories_exist():  # Ensure directories exist first
    logging.error("Required directories could not be created. Aborting database initialization.")
elif not initialize_database(DB_PATH):
    logging.warning("Database initialization failed. Application may encounter issues.")

# -----------------------
# Load Data from Database
# -----------------------

def load_data() -> tuple:
    """
    Load map-related data from the SQLite database efficiently.

    Also loads the last active character and their most recent destination.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Coordinate mappings
            cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
            columns = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
            rows = {row[0]: row[1] for row in cursor.fetchall()}

            def to_coords(col_name: str, row_name: str) -> tuple[int, int]:
                if col_name not in columns or row_name not in rows:
                    logging.warning(f"Could not resolve coordinates for {col_name} & {row_name}")
                    return None, None

                col = columns[col_name] + 1
                row = rows[row_name] + 1
                return col, row

            # Banks
            banks_coordinates = {}
            cursor.execute("SELECT `Column`, `Row`, Name, ID FROM banks")
            for col_name, row_name, _, _ in cursor.fetchall():
                banks_coordinates[f"{col_name} & {row_name}"] = (col_name, row_name)

            # Other coordinate-based structures
            taverns_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM taverns")
            }
            transits_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM transits")
            }
            user_buildings_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM userbuildings")
            }

            # Color mappings
            color_mappings = {}
            for type_, color in cursor.execute("SELECT Type, Color FROM color_mappings"):
                try:
                    qcolor = QColor(color)
                    if not qcolor.isValid():
                        logging.warning(f"Invalid color for type '{type_}': '{color}'")
                    color_mappings[type_] = qcolor
                except Exception as e:
                    logging.error(f"Failed to load QColor for '{type_}': {e}")
                    color_mappings[type_] = QColor("#000000")

            # Shops and Guilds
            shops_coordinates = {}
            for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM shops"):
                if col != "NA" and row != "NA":
                    shops_coordinates[name] = to_coords(col, row)
            guilds_coordinates = {}
            for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM guilds"):
                if col != "NA" and row != "NA":
                    guilds_coordinates[name] = to_coords(col, row)

            # Points of Interest
            places_of_interest_coordinates = {}
            cursor.execute("SELECT Name, `Column`, `Row` FROM placesofinterest")
            rows_data = cursor.fetchall()

            logging.debug("Resolved POI coordinates:")
            for name, col, row in rows_data:
                coords = to_coords(col, row)
                if coords == (None, None):
                    logging.warning(f"Skipping POI {name} due to unresolved coordinates: {col}, {row}")
                else:
                    places_of_interest_coordinates[name] = coords
                    logging.debug(f"{name}: {coords}")

            # Load settings
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'keybind_config'")
            row = cursor.fetchone()
            keybind_config = int(row[0]) if row else 1

            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'css_profile'")
            row = cursor.fetchone()
            current_css_profile = row[0] if row else "Default"

            # Load last active character
            selected_character = None
            last_destination = None
            cursor.execute("SELECT character_id FROM last_active_character LIMIT 1")
            row = cursor.fetchone()
            character_id = row[0] if row else None

            if character_id:
                cursor.execute("SELECT id, name, password FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                if char_row:
                    selected_character = {
                        "id": char_row[0],
                        "name": char_row[1],
                        "password": char_row[2]
                    }

                    # Load last destination for this character
                    cursor.execute(
                        "SELECT col, row FROM destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 1",
                        (character_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        last_destination = (row[0], row[1])

            logging.debug("Loaded data from database successfully")
            return (
                columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates,
                user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates,
                places_of_interest_coordinates, keybind_config, current_css_profile,
                selected_character, last_destination
            )

    except sqlite3.Error as e:
        logging.error(f"Failed to load data from database {DB_PATH}: {e}")
        raise


# Load data at startup
try:
    (
        columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates,
        user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates,
        places_of_interest_coordinates, keybind_config, current_css_profile,
        selected_character, last_destination
    ) = load_data()
except sqlite3.Error:
    logging.critical("Database load failed. Using fallback empty data.")
    columns = rows = taverns_coordinates = transits_coordinates = user_buildings_coordinates = \
        shops_coordinates = guilds_coordinates = places_of_interest_coordinates = {}
    banks_coordinates = {}
    color_mappings = {'default': QColor('#000000')}  # Minimal fallback
    keybind_config = 1
    current_css_profile = "Default"
    selected_character = None
    last_destination = None

# -----------------------
# Webview Cookie Database
# -----------------------

def save_cookie_to_db(cookie: QNetworkCookie) -> bool:
    """
    Save or update a single cookie in the SQLite database, overwriting if it exists.

    Args:
        cookie (QNetworkCookie): The cookie to save or update.

    Returns:
        bool: True if the cookie was saved/updated successfully, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            name = cookie.name().data().decode('utf-8', errors='replace')
            domain = cookie.domain()
            path = cookie.path()
            value = cookie.value().data().decode('utf-8', errors='replace')
            # noinspection PyUnresolvedReferences
            expiration = cookie.expirationDate().toString(Qt.ISODate) if not cookie.isSessionCookie() else None
            secure = int(cookie.isSecure())
            httponly = int(cookie.isHttpOnly())

            # Use UPSERT (INSERT OR REPLACE) to overwrite existing cookies based on name, domain, and path
            cursor.execute('''
                INSERT OR REPLACE INTO cookies (name, value, domain, path, expiration, secure, httponly)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, value, domain, path, expiration, secure, httponly))

            conn.commit()
            logging.debug(f"Saved/updated cookie: {name} for domain {domain}")
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to save/update cookie {cookie.name().data()}: {e}")
        return False

def load_cookies_from_db() -> List[QNetworkCookie]:
    """
    Load all cookies from the SQLite database.

    Returns:
        list[QNetworkCookie]: List of QNetworkCookie objects from the database.
    """
    cookies = []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, value, domain, path, expiration, secure, httponly FROM cookies')
            for name, value, domain, path, expiration, secure, httponly in cursor.fetchall():
                cookie = QNetworkCookie(
                    name.encode('utf-8'),
                    value.encode('utf-8')
                )
                cookie.setDomain(domain)
                cookie.setPath(path)
                if expiration:
                    # noinspection PyUnresolvedReferences
                    cookie.setExpirationDate(QDateTime.fromString(expiration, Qt.ISODate))
                cookie.setSecure(bool(secure))
                cookie.setHttpOnly(bool(httponly))
                cookies.append(cookie)
            logging.debug(f"Loaded {len(cookies)} cookies from database")
    except sqlite3.Error as e:
        logging.error(f"Failed to load cookies: {e}")
    return cookies

def clear_cookie_db() -> bool:
    """
    Clear all cookies from the SQLite database.

    Returns:
        bool: True if cookies were cleared successfully, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cookies')
            conn.commit()
            logging.info("Cleared all cookies from database")
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to clear cookies: {e}")
        return False

# -----------------------
# Splash Messages Decorator
# -----------------------

def splash_message(splash):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if splash and not splash.isHidden():
                splash.show_message(func.__name__)  # Show the original method name
            return func(self, *args, **kwargs)
        wrapper.__name__ = func.__name__  # Preserve the original method name
        return wrapper
    return decorator

# -----------------------
# RBC Community Map Main Class
# -----------------------

class RBCCommunityMap(QMainWindow):
    """
    Main application class for the RBC Community Map.
    """

    def __init__(self):
        """
        Initialize the RBCCommunityMap and its components efficiently.

        Sets up the main window, scraper, cookie handling, data loading, and UI components
        with proper error handling and asynchronous initialization where possible.
        """
        super().__init__()

        # Core state flags
        self.is_updating_minimap = False
        self.pending_login = False
        self.pending_character_id_for_map = None
        self.webview_loaded = False
        self.splash = None
        self.selected_route_label = None  # Can be "Direct Route", "Transit Route", or None for auto

        # Initialize character coordinates
        self.character_x = None
        self.character_y = None
        self.selected_character = None
        self.destination = None

        # Initialize essential components early
        self._init_data()
        self._init_scraper()
        self._init_window_properties()
        self._init_web_profile()

        # UI and character setup
        self._init_ui_state()
        self._init_characters()
        self._init_ui_components()

        # Final setup steps
        self._finalize_setup()

    @splash_message(None)
    def _init_scraper(self) -> None:
        """Initialize the AVITD scraper and start scraping in a separate thread."""
        self.AVITD_scraper = AVITDScraper()
        # Use QThread for non-blocking scraping (assuming AVITDScraper supports it)
        from PySide6.QtCore import QThreadPool
        QThreadPool.globalInstance().start(lambda: self.AVITD_scraper.scrape_guilds_and_shops())
        logging.debug("Started scraper in background thread")

    @splash_message(None)
    def _init_window_properties(self) -> None:
        """Set up main window properties."""
        try:
            self.setWindowIcon(QIcon('images/favicon.ico'))
            self.setWindowTitle('RBC Community Map')
            self.setGeometry(100, 100, 1200, 800)
            self.load_theme_settings()
            self.apply_theme()
        except Exception as e:
            logging.error(f"Failed to set window properties: {e}")
            # Fallback to default icon/title if needed
            self.setWindowTitle('RBC Community Map (Fallback)')

    @splash_message(None)
    def _init_web_profile(self) -> None:
        """Set up QWebEngineProfile for cookie handling."""
        self.web_profile = QWebEngineProfile.defaultProfile()
        cookie_storage_path = os.path.join(os.getcwd(), 'sessions')
        try:
            os.makedirs(cookie_storage_path, exist_ok=True)
            # noinspection PyUnresolvedReferences
            self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            self.web_profile.setPersistentStoragePath(cookie_storage_path)
            self.setup_cookie_handling()
        except OSError as e:
            logging.error(f"Failed to set up cookie storage at {cookie_storage_path}: {e}")
            # Continue with in-memory cookies if storage fails

    @splash_message(None)
    def _init_data(self) -> None:
        """Load initial data from the database with fallback."""
        try:
            (
                self.columns, self.rows, self.banks_coordinates, self.taverns_coordinates,
                self.transits_coordinates, self.user_buildings_coordinates, self.color_mappings,
                self.shops_coordinates, self.guilds_coordinates, self.places_of_interest_coordinates,
                self.keybind_config, self.current_css_profile,
                self.selected_character, self.destination  # <-- just store, don't update minimap yet
            ) = load_data()

        except sqlite3.Error as e:
            logging.critical(f"Failed to load initial data: {e}")
            # Use fallback data
            self.columns = self.rows = self.banks_coordinates = self.taverns_coordinates = \
                self.transits_coordinates = self.user_buildings_coordinates = \
                self.shops_coordinates = self.guilds_coordinates = self.places_of_interest_coordinates = {}
            self.color_mappings = {'default': QColor('#000000')}
            self.keybind_config = 1
            self.current_css_profile = "Default"
            self.selected_character = None
            self.destination = None

    @splash_message(None)
    def _init_ui_state(self) -> None:
        """Initialize UI-related state variables."""
        self.zoom_level = 3
        self.load_zoom_level_from_database()  # May override zoom_level
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None

    @splash_message(None)
    def _init_characters(self) -> None:
        """Initialize character-related data and widgets."""
        self.characters = []
        self.character_list = QListWidget()
        self.selected_character = None
        self.load_characters()
        if not self.characters:
            self.firstrun_character_creation()

    @splash_message(None)
    def _init_ui_components(self) -> None:
        """Set up UI components and console logging."""
        self.setup_ui_components()
        self.setup_console_logging()

    @splash_message(None)
    def _finalize_setup(self) -> None:
        """Complete initialization with UI display and final configurations."""
        self.show()

        if self.selected_character and self.destination:
            self.update_minimap()

        self.load_last_active_character()
        self.setup_keybindings()
        # noinspection PyUnresolvedReferences
        self.setFocusPolicy(Qt.StrongFocus)
        if hasattr(self, 'website_frame'):
            # noinspection PyUnresolvedReferences
            self.website_frame.setFocusPolicy(Qt.StrongFocus)
        else:
            logging.warning("website_frame not initialized before focus setup")
        css = self.load_current_css()
        self.apply_custom_css(css)

    def load_current_css(self) -> str:
        """Load CSS for the current profile from the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'css_profile'")
                result = cursor.fetchone()
                profile = result[0] if result else "Default"
                cursor.execute("SELECT element, value FROM custom_css WHERE profile_name = ?", (profile,))
                return "\n".join(f"{elem} {{ {val} }}" for elem, val in cursor.fetchall())
        except sqlite3.Error as e:
            logging.error(f"Failed to load CSS: {e}")
            return ""

# -----------------------
# Keybindings
# -----------------------

    def load_keybind_config(self) -> int:
        """
        Load keybind configuration from the database.

        Returns:
            int: Keybind mode (0=Off, 1=WASD, 2=Arrows), defaults to 1 (WASD) if not found.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'keybind_config'")
                result = cursor.fetchone()
                return int(result[0]) if result else 1  # Default to WASD
        except sqlite3.Error as e:
            logging.error(f"Failed to load keybind config: {e}")
            return 1  # Fallback to WASD on error

    def setup_keybindings(self) -> None:
        """Set up keybindings for character movement based on current config."""
        movement_configs = {
            1: {  # WASD Mode
                Qt.Key.Key_W: 1,  # Top-center
                Qt.Key.Key_A: 3,  # Middle-left
                Qt.Key.Key_S: 7,  # Bottom-center
                Qt.Key.Key_D: 5  # Middle-right
            },
            2: {  # Arrow Keys Mode
                Qt.Key.Key_Up: 1,
                Qt.Key.Key_Left: 3,
                Qt.Key.Key_Down: 7,
                Qt.Key.Key_Right: 5
            },
            0: {}  # Off mode (no keybindings)
        }

        self.movement_keys = movement_configs.get(self.keybind_config, movement_configs[1])
        logging.debug(f"Setting up keybindings: {self.movement_keys}")

        self.clear_existing_keybindings()

        if self.keybind_config == 0:
            logging.info("Keybindings disabled (mode 0)")
            return

        if not hasattr(self, 'website_frame'):
            logging.error("website_frame not initialized; skipping keybinding setup")
            return

        for key, move_index in self.movement_keys.items():
            shortcut = QShortcut(QKeySequence(key), self.website_frame, context=Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(lambda idx=move_index: self.move_character(idx))
            logging.debug(f"Bound key {key} to move index {move_index}")

    def move_character(self, move_index: int) -> None:
        """
        Move character to the specified grid position via JavaScript,
        but only if the currently focused widget is not an input field.

        Args:
            move_index (int): Index in the 3x3 movement grid (0-8).
        """
        widget = QApplication.focusWidget()
        if isinstance(widget, (QLineEdit, QComboBox)):
            logging.debug(f"Ignored movement key {move_index} due to focus on input: {widget}")
            return

        if not hasattr(self, 'website_frame') or not self.website_frame.page():
            logging.warning("Cannot move character: website_frame or page not initialized")
            return

        logging.debug(f"Attempting move to grid index: {move_index}")
        js_code = """
            (function() {
                const table = document.querySelector('table table');
                if (!table) return 'No table';
                const spaces = Array.from(table.querySelectorAll('td'));
                if (spaces.length !== 9) return 'Invalid grid size: ' + spaces.length;
                const targetSpace = spaces[%d];
                if (!targetSpace) return 'No target space';
                const form = targetSpace.querySelector('form[action="/blood.pl"][method="POST"]');
                if (!form) return 'No form';
                const x = form.querySelector('input[name="x"]').value;
                const y = form.querySelector('input[name="y"]').value;
                form.submit();
                return 'Submitted to x=' + x + ', y=' + y;
            })();
        """ % move_index
        self.website_frame.page().runJavaScript(js_code, lambda result: logging.debug(f"Move result: {result}"))
        self.website_frame.setFocus()

    def toggle_keybind_config(self, mode: int) -> None:
        """
        Switch between keybinding modes (0=Off, 1=WASD, 2=Arrows) and update settings.

        Args:
            mode (int): Keybind mode to switch to.
        """
        if mode not in {0, 1, 2}:
            logging.warning(f"Invalid keybind mode: {mode}; ignoring")
            return

        self.keybind_config = mode
        mode_text = {0: "Off", 1: "WASD", 2: "Arrow Keys"}[mode]
        logging.info(f"Switching to keybind mode {mode} ({mode_text})")

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (setting_name, setting_value) VALUES ('keybind_config', ?)",
                    (mode,)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save keybind config {mode}: {e}")
            return  # Don’t proceed if database fails

        self.setup_keybindings()
        self.update_keybind_menu()
        # noinspection PyArgumentList
        QMessageBox.information(self, "Keybind Config", f"Switched to {mode_text}")

    def update_keybind_menu(self) -> None:
        """Update keybinding menu checkmarks based on current config."""
        if not hasattr(self, 'keybind_wasd_action') or not hasattr(self, 'keybind_arrow_action') or \
           not hasattr(self, 'keybind_off_action'):
            logging.warning("Keybind menu actions not initialized; skipping update")
            return

        self.keybind_wasd_action.setChecked(self.keybind_config == 1)
        self.keybind_arrow_action.setChecked(self.keybind_config == 2)
        self.keybind_off_action.setChecked(self.keybind_config == 0)
        logging.debug(f"Updated keybind menu: WASD={self.keybind_config == 1}, Arrows={self.keybind_config == 2}, Off={self.keybind_config == 0}")

    def clear_existing_keybindings(self) -> None:
        """Remove existing shortcuts from website_frame to prevent duplicates."""
        if not hasattr(self, 'website_frame'):
            logging.debug("No website_frame to clear keybindings from")
            return

        shortcuts = list(self.website_frame.findChildren(QShortcut))
        for shortcut in shortcuts:
            shortcut.setParent(None)
            shortcut.deleteLater()  # Ensure cleanup
        logging.debug(f"Cleared {len(shortcuts)} existing keybindings")

# -----------------------
# Load and Apply Customized UI Theme
# -----------------------

    def load_theme_settings(self) -> None:
        """
        Load theme colors from the color_mappings table into self.color_mappings.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT type, color FROM color_mappings")
                rows = cursor.fetchall()
                self.color_mappings.update({type_: QColor(color) for type_, color in rows})
                logging.debug(f"Loaded {len(rows)} theme entries from color_mappings.")
        except sqlite3.Error as e:
            logging.error(f"Failed to load theme from color_mappings: {e}")

    def save_theme_settings(self) -> bool:
        """
        Save current color mappings to the color_mappings table in the database.

        Returns:
            bool: True if saved successfully, False otherwise.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    '''
                    INSERT INTO color_mappings (type, color)
                    VALUES (?, ?)
                    ON CONFLICT(type) DO UPDATE SET color = excluded.color
                    ''',
                    [(key, color.name()) for key, color in self.color_mappings.items()]
                )
                conn.commit()
                logging.debug("Theme settings saved to color_mappings table.")
                return True
        except sqlite3.Error as e:
            logging.error(f"Failed to save theme to color_mappings: {e}")
            return False

    def apply_theme(self) -> None:
        """Apply current theme settings to the application's stylesheet."""
        try:
            bg_color = self.color_mappings.get("background", QColor("#d4d4d4")).name()
            text_color = self.color_mappings.get("text_color", QColor("#000000")).name()
            btn_color = self.color_mappings.get("button_color", QColor("#b1b1b1")).name()

            stylesheet = (
                f"QWidget {{ background-color: {bg_color}; color: {text_color}; }}"
                f"QPushButton {{ background-color: {btn_color}; color: {text_color}; }}"
                f"QLabel {{ color: {text_color}; }}"
            )
            self.setStyleSheet(stylesheet)
            logging.debug("Theme applied successfully")
        except Exception as e:
            logging.error(f"Failed to apply theme: {e}")
            self.setStyleSheet("")  # Reset to default on failure

    def change_theme(self) -> None:
        """
        Open theme customization dialog and apply/save selected theme.

        Assumes ThemeCustomizationDialog is defined elsewhere with exec() and color_mappings.
        """
        dialog = ThemeCustomizationDialog(self, color_mappings=self.color_mappings)
        if dialog.exec():
            self.color_mappings = dialog.color_mappings
            self.apply_theme()
            if self.save_theme_settings():
                logging.info("Theme updated and saved")
            else:
                logging.warning("Theme applied but not saved due to database error")

# -----------------------
# Cookie Handling
# -----------------------

    def setup_cookie_handling(self) -> None:
        """
        Set up cookie handling by connecting the QWebEngineProfile's cookie store and loading saved cookies.
        """
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        self.load_cookies()
        logging.debug("Cookie handling initialized")

    def load_cookies(self) -> None:
        """
        Load cookies from the 'cookies' table and inject them into the QWebEngineProfile.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, domain, path, value, expiration, secure, httponly FROM cookies")
                cookies = cursor.fetchall()

                for name, domain, path, value, expiration, secure, httponly in cookies:
                    cookie = QNetworkCookie(name.encode('utf-8'), value.encode('utf-8'))
                    cookie.setDomain(domain)
                    cookie.setPath(path)
                    cookie.setSecure(bool(secure))
                    cookie.setHttpOnly(bool(httponly))
                    if expiration:
                        try:
                            # Handle both string (ISO) and int (epoch) expiration formats
                            if isinstance(expiration, str):
                                # noinspection PyUnresolvedReferences
                                cookie.setExpirationDate(QDateTime.fromString(expiration, Qt.ISODate))
                            elif isinstance(expiration, int):
                                cookie.setExpirationDate(QDateTime.fromSecsSinceEpoch(expiration))
                            else:
                                logging.warning(f"Invalid expiration type for cookie '{name}': {type(expiration)}")
                        except ValueError as e:
                            logging.warning(f"Failed to parse expiration '{expiration}' for cookie '{name}': {e}")
                    self.cookie_store.setCookie(cookie, QUrl(f"https://{domain}"))
                logging.debug(f"Loaded {len(cookies)} cookies from database")
        except sqlite3.Error as e:
            logging.error(f"Failed to load cookies: {e}")

    def on_cookie_added(self, cookie: QNetworkCookie) -> None:
        name = cookie.name().data().decode()
        value = cookie.value().data().decode()
        domain = cookie.domain().lstrip('.')  # Normalize domain
        path = cookie.path()

        if domain != 'quiz.ravenblack.net':
            return

        if name == 'stamp':
            return  # skip churn cookie

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Check if this exact cookie already exists
                cursor.execute("""
                    SELECT id FROM cookies 
                    WHERE name = ? AND value = ? AND domain = ? AND path = ?
                """, (name, value, domain, path))
                existing = cursor.fetchone()

                if existing:
                    logging.debug(f"Duplicate cookie '{name}' for value '{value}' not saved.")
                    return

                # Insert new cookie
                cursor.execute("""
                    INSERT INTO cookies (name, value, domain, path, expiration, secure, httponly)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, value, domain, path,
                    cookie.expirationDate().toString(Qt.ISODate) if not cookie.isSessionCookie() else None,
                    int(cookie.isSecure()), int(cookie.isHttpOnly())
                ))

                new_cookie_id = cursor.lastrowid
                conn.commit()
                logging.debug(f"Saved new cookie '{name}' (ID {new_cookie_id}) for domain '{domain}'")

                # If it's an ip cookie, consider linking to character
                if name == 'ip' and '#' in value:
                    username, password = value.split('#', 1)
                    is_login = bool(password.strip())

                    logging.debug(
                        f"Captured IP cookie for user '{username}' — {'login' if is_login else 'logout'} state."
                    )

                    # Update character only if this is a login cookie
                    if is_login:
                        cursor.execute("""
                            UPDATE characters SET active_cookie = ? WHERE name = ?
                        """, (new_cookie_id, username))
                        conn.commit()
                        logging.debug(f"Set active_cookie for character '{username}' to cookie ID {new_cookie_id}")

        except Exception as e:
            logging.error(f"Error saving cookie '{name}': {e}")

    def set_ip_cookie(self, name: str, password: str):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                value = f"{name}#{password}"
                domain = 'quiz.ravenblack.net'
                path = '/'

                # Avoid duplicate
                cursor.execute("""
                    SELECT id FROM cookies WHERE name = 'ip' AND value = ? AND domain = ? AND path = ?
                """, (value, domain, path))
                row = cursor.fetchone()

                if row:
                    cookie_id = row[0]
                else:
                    cursor.execute('''
                        INSERT INTO cookies (name, value, domain, path, expiration, secure, httponly)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        'ip', value, domain, path,
                        QDateTime.currentDateTime().addDays(30).toString(Qt.ISODate),
                        0, 0
                    ))
                    cookie_id = cursor.lastrowid

                # Set this cookie as active, clear others
                cursor.execute("UPDATE characters SET active_cookie = NULL")
                cursor.execute("UPDATE characters SET active_cookie = ? WHERE name = ?", (cookie_id, name))
                conn.commit()
                logging.debug(f"Set active_cookie ID {cookie_id} for {name}")

        except sqlite3.Error as e:
            logging.error(f"Failed to insert 'ip' cookie for {name}: {e}")

# -----------------------
# UI Setup
# -----------------------

    def setup_ui_components(self):
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

        # Disable GPU-related features
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)

        # Add Keybindings
        self.setup_keybindings()

        # Browser controls layout
        self.browser_controls_layout = QHBoxLayout()

        # Back button using Qt's built-in style
        back_button = QPushButton()
        back_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setIconSize(QSize(30, 30))
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet("background-color: transparent; border: none;")
        back_button.clicked.connect(self.website_frame.back)
        self.browser_controls_layout.addWidget(back_button)

        # Forward button using Qt's built-in style
        forward_button = QPushButton()
        forward_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        forward_button.setCursor(Qt.PointingHandCursor)
        forward_button.setIconSize(QSize(30, 30))
        forward_button.setFixedSize(30, 30)
        forward_button.setStyleSheet("background-color: transparent; border: none;")
        forward_button.clicked.connect(self.website_frame.forward)
        self.browser_controls_layout.addWidget(forward_button)

        refresh_button = QPushButton()
        refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.setIconSize(QSize(30, 30))
        refresh_button.setFixedSize(30, 30)
        refresh_button.setStyleSheet("background-color: transparent; border: none;")
        refresh_button.clicked.connect(lambda: self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl')))
        self.browser_controls_layout.addWidget(refresh_button)

        self.browser_controls_layout.addStretch(1)

        # AP and compass container
        ap_compass_container = QWidget()
        ap_compass_layout = QHBoxLayout(ap_compass_container)
        ap_compass_layout.setContentsMargins(0, 0, 0, 0)
        ap_compass_layout.setSpacing(10)

        # Compass Icon Button
        self.compass_button = QPushButton()
        self.compass_button.setIcon(QIcon(QPixmap("images/compass.png")))
        self.compass_button.setIconSize(QSize(28, 28))  # Adjust as needed
        self.compass_button.setFixedSize(34, 34)
        self.compass_button.setStyleSheet("background-color: transparent; border: none;")
        self.compass_button.setToolTip("Open Compass Overlay")
        self.compass_button.clicked.connect(self.show_compass_overlay)
        ap_compass_layout.addWidget(self.compass_button)

        # AP Direction Label
        self.ap_direction_label = QLabel()
        self.ap_direction_label.setAlignment(Qt.AlignCenter)
        self.ap_direction_label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
        ap_compass_layout.addWidget(self.ap_direction_label)

        self.browser_controls_layout.addWidget(ap_compass_container)
        self.browser_controls_layout.addStretch(1)

        # Ko-Fi button with a programmatically generated icon
        kofi_button = QPushButton()
        kofi_icon = QPixmap(30, 30)
        kofi_icon.fill(Qt.transparent)
        painter = QPainter(kofi_icon)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor(0, 188, 212)))  # Ko-Fi teal color
        painter.drawEllipse(5, 5, 20, 20)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawText(kofi_icon.rect(), Qt.AlignCenter, "K")
        painter.end()
        kofi_button.setIcon(QIcon(kofi_icon))
        kofi_button.setIconSize(QSize(30, 30))
        kofi_button.setToolTip("Support me on Ko-fi")
        # noinspection PyUnresolvedReferences
        kofi_button.setCursor(Qt.PointingHandCursor)
        kofi_button.setFlat(True)
        kofi_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ko-fi.com/jelollis")))

        # Set spacing between buttons to make them closer together
        # Add spacing and the Ko-fi button to the end of the toolbar
        self.browser_controls_layout.setSpacing(5)
        self.browser_controls_layout.addStretch(1)
        self.browser_controls_layout.addWidget(kofi_button)

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

        # Information frame to display nearest locations and AP costs
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setFixedHeight(260)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Common style for each info label with padding, border, and smaller font size
        label_style = """
            background-color: {color};
            color: white;
            font-weight: bold;
            padding: 5px;
            border: 2px solid black;
            font-size: 12px;
        """

        # Closest Bank Info
        self.bank_label = QLabel("Bank")
        self.bank_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.bank_label.setStyleSheet(label_style.format(color="blue"))
        self.bank_label.setWordWrap(True)
        self.bank_label.setFixedHeight(45)
        info_layout.addWidget(self.bank_label)

        # Closest Transit Info
        self.transit_label = QLabel("Transit")
        self.transit_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.transit_label.setStyleSheet(label_style.format(color="red"))
        self.transit_label.setWordWrap(True)
        self.transit_label.setFixedHeight(45)
        info_layout.addWidget(self.transit_label)

        # Closest Tavern Info
        self.tavern_label = QLabel("Tavern")
        self.tavern_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tavern_label.setStyleSheet(label_style.format(color="orange"))
        self.tavern_label.setWordWrap(True)
        self.tavern_label.setFixedHeight(45)
        info_layout.addWidget(self.tavern_label)

        # Set Destination Info
        self.destination_label = QLabel("Set Destination")
        self.destination_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.destination_label.setStyleSheet(label_style.format(color="green"))
        self.destination_label.setWordWrap(True)
        self.destination_label.setFixedHeight(45)
        info_layout.addWidget(self.destination_label)

        # Transit-Based AP for Set Destination Info
        self.transit_destination_label = QLabel("Set Destination - Transit Route")
        self.transit_destination_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.transit_destination_label.setStyleSheet(label_style.format(color="purple"))
        self.transit_destination_label.setWordWrap(True)
        self.transit_destination_label.setFixedHeight(45)
        info_layout.addWidget(self.transit_destination_label)

        # ComboBox and Go Button
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        # --- Editable, searchable COLUMN ComboBox ---
        self.combo_columns = QComboBox()
        self.combo_columns.setEditable(True)
        self.combo_columns.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_columns.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_columns.addItem("Select Column")  # Placeholder
        self.combo_columns.addItems(list(columns.keys()))
        self.combo_columns.setCurrentIndex(0)
        self.combo_columns.model().item(0).setEnabled(False)  # Disable placeholder

        column_completer = QCompleter(list(columns.keys()))
        column_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo_columns.setCompleter(column_completer)

        # Install event filters for clearing behavior
        self.combo_columns.lineEdit().installEventFilter(self)
        self.combo_columns.installEventFilter(self)

        # --- Editable, searchable ROW ComboBox ---
        self.combo_rows = QComboBox()
        self.combo_rows.setEditable(True)
        self.combo_rows.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_rows.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_rows.addItem("Select Row")
        self.combo_rows.addItems(list(rows.keys()))
        self.combo_rows.setCurrentIndex(0)
        self.combo_rows.model().item(0).setEnabled(False)

        row_completer = QCompleter(list(rows.keys()))
        row_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo_rows.setCompleter(row_completer)

        self.combo_rows.lineEdit().installEventFilter(self)
        self.combo_rows.installEventFilter(self)

        # Go Button
        go_button = QPushButton('Go')
        go_button.setFixedSize(25, 25)
        go_button.clicked.connect(self.go_to_location)

        # Layout assembly
        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        # Label for dropdowns to indicate their function
        dropdown_label = QLabel("Recenter Minimap to Location")
        dropdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dropdown_label.setStyleSheet("font-size: 12px; padding: 5px;")
        left_layout.addWidget(dropdown_label)

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
        set_destination_button.clicked.connect(self.open_SetDestinationDialog)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        # Layout for refresh, discord, and website buttons
        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 25)
        refresh_button.clicked.connect(lambda: self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl')))
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
                    self.selected_character['id'] = character_id
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
        """Navigate the web browser back to the previous page."""
        self.website_frame.back()

    def go_forward(self):
        """Navigate the web browser forward to the next page."""
        self.website_frame.forward()

    def refresh_page(self):
        """Refresh the current page displayed in the web browser."""
        self.website_frame.reload()

    def create_menu_bar(self) -> None:
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

        css_customization_action = QAction('CSS Customization', self)
        css_customization_action.triggered.connect(self.open_css_customization_dialog)
        settings_menu.addAction(css_customization_action)

        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in_browser)
        settings_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out_browser)
        settings_menu.addAction(zoom_out_action)

        # Keybindings Submenu
        keybindings_menu = settings_menu.addMenu("Keybindings")

        self.keybind_wasd_action = QAction("WASD", self, checkable=True)
        self.keybind_wasd_action.triggered.connect(lambda: self.toggle_keybind_config(1))

        self.keybind_arrow_action = QAction("Arrow Keys", self, checkable=True)
        self.keybind_arrow_action.triggered.connect(lambda: self.toggle_keybind_config(2))

        self.keybind_off_action = QAction("Off", self, checkable=True)
        self.keybind_off_action.triggered.connect(lambda: self.toggle_keybind_config(0))

        keybindings_menu.addAction(self.keybind_wasd_action)
        keybindings_menu.addAction(self.keybind_arrow_action)
        keybindings_menu.addAction(self.keybind_off_action)

        # Update checkmark based on current keybind setting
        self.update_keybind_menu()

        # Logging Level Submenu
        log_level_menu = settings_menu.addMenu("Logging Level")

        self.log_level_actions = {}

        log_levels = [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
            ("OFF", logging.CRITICAL + 10)  # OFF = disables all logging
        ]

        for name, level in log_levels:
            action = QAction(name, self, checkable=True)
            action.triggered.connect(lambda checked, lvl=level: self.set_log_level(lvl))
            log_level_menu.addAction(action)
            self.log_level_actions[level] = action

        self.update_log_level_menu()

        # Tools menu
        tools_menu = menu_bar.addMenu('Tools')

        database_viewer_action = QAction('Database Viewer', self)
        database_viewer_action.triggered.connect(self.open_database_viewer)
        tools_menu.addAction(database_viewer_action)

        shopping_list_action = QAction('Shopping List Generator', self)
        shopping_list_action.triggered.connect(self.open_shopping_list_tool)
        tools_menu.addAction(shopping_list_action)

        damage_calculator_action = QAction('Damage Calculator', self)
        damage_calculator_action.triggered.connect(self.open_damage_calculator_tool)
        tools_menu.addAction(damage_calculator_action)

        power_reference_action = QAction('Power Reference Tool', self)
        power_reference_action.triggered.connect(self.open_powers_dialog)
        tools_menu.addAction(power_reference_action)

        logs_action = QAction('View Logs', self)
        logs_action.triggered.connect(self.open_log_viewer)
        tools_menu.addAction(logs_action)

        # Resources
        resources_menu = menu_bar.addMenu('Resources')

        avitd_action = QAction('AVITD', self)
        avitd_action.triggered.connect(lambda: webbrowser.open('https://aviewinthedark.net/'))
        resources_menu.addAction(avitd_action)

        rb_wiki_action = QAction('RB Wiki', self)
        rb_wiki_action.triggered.connect(lambda: webbrowser.open('https://ravenblack.city/'))
        resources_menu.addAction(rb_wiki_action)

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

        report_issue_action = QAction('Report an Issue', self)
        report_issue_action.triggered.connect(lambda: webbrowser.open('https://github.com/JELollis/RBC-Map/issues/new'))
        help_menu.addAction(report_issue_action)

        view_help_action = QAction('View Help', self)
        view_help_action.setShortcut(QKeySequence('F1'))
        view_help_action.triggered.connect(self.open_help_file)
        help_menu.addAction(view_help_action)

    def zoom_in_browser(self):
        """Zoom in on the web page displayed in the QWebEngineView."""
        self.website_frame.setZoomFactor(self.website_frame.zoomFactor() + 0.1)

    def zoom_out_browser(self):
        """Zoom out on the web page displayed in the QWebEngineView."""
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

    def get_default_screenshot_path(self, suffix: str) -> str:
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures", "RBC Map")
        os.makedirs(pictures_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"{timestamp}_{suffix}.png"
        return os.path.join(pictures_dir, default_filename)

    def save_webpage_screenshot(self):
        """
        Save the current webpage as a screenshot to Pictures/RBC Map with a timestamped filename.
        """
        default_path = self.get_default_screenshot_path("webpage")
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Webpage Screenshot", default_path,
                                                   "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.website_frame.grab().save(file_name)

    def save_app_screenshot(self):
        """
        Save the current application window as a screenshot to Pictures/RBC Map with a timestamped filename.
        """
        default_path = self.get_default_screenshot_path("app")
        file_name, _ = QFileDialog.getSaveFileName(self, "Save App Screenshot", default_path,
                                                   "PNG Files (*.png);;All Files (*)")
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
            character_name = current_item.text()
        else:
            # Show an error message if no character is selected
            QMessageBox.warning(self, "No Character Selected", "Please select a character from the list.")
            return

        # Open the ShoppingListTool with the selected character and unified database path
        self.shopping_list_tool = ShoppingListTool(character_name, DB_PATH)
        self.shopping_list_tool.show()

    def open_damage_calculator_tool(self):
        """
        Opens the Damage Calculator dialog within RBCCommunityMap.
        """
        # Initialize the DamageCalculator dialog with the SQLite database connection
        connection = sqlite3.connect(DB_PATH)
        damage_calculator = DamageCalculator(connection)

        # Set the default selection in the combobox to 'No Charisma'
        damage_calculator.charisma_dropdown.setCurrentIndex(0)  # Index 0 corresponds to 'No Charisma'

        # Show the DamageCalculator dialog as a modal
        damage_calculator.exec()

        # Close the database connection after use
        connection.close()

    def display_shopping_list(self, shopping_list):
        """
        Display the shopping list in a dialog.
        """
        shopping_list_text = "\n".join(
            f"{entry['shop']} - {entry['item']} - {entry['quantity']}x - {entry['total_cost']} coins"
            for entry in shopping_list
        )
        total_cost = sum(entry['total_cost'] for entry in shopping_list)
        shopping_list_text += f"\n\nTotal Coins - {total_cost}"
        # noinspection PyArgumentList
        QMessageBox.information(self, "Damage Calculator Shopping List", shopping_list_text)

    def open_powers_dialog(self):
        """
        Opens the Powers Dialog and ensures character coordinates are passed correctly.
        """
        powers_dialog = PowersDialog(self, self.character_x, self.character_y, DB_PATH)  # Ensure correct parameters
        powers_dialog.exec()

    def open_css_customization_dialog(self):
        """Open the CSS customization dialog."""
        dialog = CSSCustomizationDialog(self)
        dialog.exec()

    def update_log_level_menu(self) -> None:
        """
        Update the check state of log level actions based on current level from DB.
        """
        current_level = get_logging_level_from_db()
        for level, action in self.log_level_actions.items():
            action.setChecked(level == current_level)

    def set_log_level(self, level: int) -> None:
        """
        Set the log level and persist it in the database.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO settings (setting_name, setting_value)
                    VALUES ('log_level', ?)
                    ON CONFLICT(setting_name) DO UPDATE SET setting_value = excluded.setting_value
                """, (level,))
                conn.commit()

            logging.getLogger().setLevel(level)
            self.update_log_level_menu()
            logging.info(f"Log level set to {logging.getLevelName(level)}")

        except sqlite3.Error as e:
            logging.error(f"Failed to save log level to database: {e}")

    def open_help_file(self):
        """
        Open the compiled .chm help file from the help folder.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the folder of the current script
        help_path = os.path.join(base_dir, "docs", "help", "RBCMap Help.chm")

        if os.path.exists(help_path):
            os.startfile(help_path)
        else:
            QMessageBox.warning(
                self,
                "Help File Missing",
                f"Could not find help file:\n{help_path}"
            )

# -----------------------
# Character Management
# -----------------------

    def load_characters(self):
        connection = None
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, password FROM characters")
            character_data = cursor.fetchall()
            self.characters = [
                {'id': char_id, 'name': name, 'password': password}
                for char_id, name, password in character_data
            ]

            self.character_list.clear()
            for character in self.characters:
                item = QListWidgetItem(character['name'])
                item.setData(Qt.UserRole, character['id'])  # 🔥 Attach ID!
                self.character_list.addItem(item)

            logging.debug(f"Loaded {len(self.characters)} characters from the database.")
            if not self.characters:
                logging.warning("No characters found in the database.")
                self.selected_character = None

        except sqlite3.Error as e:
            logging.error(f"Failed to load characters from database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load characters: {e}")
            self.characters = []
            self.selected_character = None
        finally:
            if connection:
                connection.close()

    def save_characters(self):
        connection = None
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            for character in self.characters:
                cursor.execute('''
                    INSERT OR REPLACE INTO characters (id, name, password) VALUES (?, ?, ?)
                ''', (character.get('id'), character['name'], character['password']))
            connection.commit()
            logging.debug("Characters saved successfully to the database in plaintext.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save characters to database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save characters: {e}")
        finally:
            if connection:
                connection.close()

    def on_character_selected(self, item):
        """
        Handle character selection: set the selected character, load cookie,
        and trigger login + destination load after webview reload.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)

        if not selected_character:
            logging.error(f"Character selection failed: {character_name}")
            return

        logging.debug(f"Selected character: {character_name}")
        self.selected_character = selected_character

        # Ensure character has ID
        if 'id' not in self.selected_character:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM characters WHERE name = ?", (character_name,))
                    row = cursor.fetchone()
                    if row:
                        self.selected_character['id'] = row[0]
            except sqlite3.Error as e:
                logging.error(f"Failed to retrieve character ID for '{character_name}': {e}")
                return

        # Final ID check before proceeding
        character_id = self.selected_character.get('id')
        if not character_id:
            logging.error(f"Character '{character_name}' has no valid ID.")
            return

        # Mark destination and login to be handled on next page load
        self.pending_character_id_for_map = character_id
        self.pending_login = True
        self.save_last_active_character(character_id)

        # Inject cookie and trigger page reload
        self.switch_to_character(character_name)

    def switch_to_character(self, character_name: str) -> None:
        """
        Switch to the selected character by loading its saved IP cookie into the WebEngine.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.active_cookie, k.value 
                    FROM characters c
                    JOIN cookies k ON c.active_cookie = k.id
                    WHERE c.name = ?
                """, (character_name,))
                row = cursor.fetchone()

                if not row:
                    logging.error(f"No saved login cookie found for character '{character_name}'.")
                    return

                cookie_id, cookie_value = row

                ip_cookie = QNetworkCookie(b'ip', cookie_value.encode('utf-8'))
                ip_cookie.setDomain('quiz.ravenblack.net')
                ip_cookie.setPath('/')
                ip_cookie.setExpirationDate(QDateTime.currentDateTime().addDays(30))

                self.cookie_store.setCookie(ip_cookie, QUrl("https://quiz.ravenblack.net"))
                logging.debug(f"Injected saved 'ip' cookie ID {cookie_id} for {character_name}.")

                # Reload page after injecting cookie
                self.website_frame.setUrl(QUrl("https://quiz.ravenblack.net/blood.pl"))

        except sqlite3.Error as e:
            logging.error(f"Failed to switch character '{character_name}': {e}")

    def login_selected_character(self):
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        name = self.selected_character['name']
        password = self.selected_character['password']
        logging.debug(f"Injecting login for character: {name} (ID: {self.selected_character.get('id')})")

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
        Then injects login form to let the server issue a valid IP cookie.
        """
        logging.debug("First-run character creation.")
        dialog = CharacterDialog(self)

        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('INSERT INTO characters (name, password) VALUES (?, ?)', (name, password))
                    character_id = cursor.lastrowid
                    cursor.execute('INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)', (character_id,))
                    conn.commit()

                    self.save_last_active_character(character_id)

                    # Add to in-memory list and UI
                    character = {'name': name, 'password': password, 'id': character_id}
                    self.characters.append(character)
                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, character_id)
                    self.character_list.addItem(item)

                    # Select and login to generate cookie
                    self.selected_character = character
                    self.character_list.setCurrentRow(self.character_list.count() - 1)
                    QTimer.singleShot(1000, self.login_selected_character)

                    logging.debug(f"First-run character '{name}' created and login initiated.")

                except sqlite3.Error as e:
                    logging.error(f"Failed to create character '{name}': {e}")
                    QMessageBox.critical(self, "Error", f"Failed to create character: {e}")
        else:
            sys.exit("No characters added. Exiting the application.")

    def add_new_character(self):
        """
        Add a new character, logout current user, log in new character.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)

        if not dialog.exec():
            return  # User canceled or closed

        name = dialog.name_edit.text().strip()
        password = dialog.password_edit.text().strip()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO characters (name, password) VALUES (?, ?)', (name, password))
                character_id = cursor.lastrowid
                cursor.execute('INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)', (character_id,))
                conn.commit()

                character = {'id': character_id, 'name': name, 'password': password}
                self.characters.append(character)
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, character_id)
                self.character_list.addItem(item)

                self.selected_character = character
                self.character_list.setCurrentRow(self.character_list.count() - 1)
                self.save_last_active_character(character_id)

                logging.debug(f"New character '{name}' added and selected. Logging out current user...")

                # 🚪 Force logout and prepare for JS login
                self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))

                def delayed_login():
                    self.login_selected_character()

                QTimer.singleShot(1500, delayed_login)

            except sqlite3.Error as e:
                logging.error(f"Failed to add character '{name}': {e}")
                QMessageBox.critical(self, "Error", f"Failed to add character: {e}")

    def modify_character(self):
        """
        Modify the selected character's details, with validation to prevent blank name/password.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for modification.")
            return

        name = current_item.text()
        character = next((char for char in self.characters if char['name'] == name), None)
        if not character:
            logging.warning(f"Character '{name}' not found for modification.")
            return

        logging.debug(f"Modifying character: {name}")
        dialog = CharacterDialog(self, character)

        if not dialog.exec():
            return  # User canceled

        new_name = dialog.name_edit.text().strip()
        new_password = dialog.password_edit.text().strip()

        if not new_name or not new_password:
            QMessageBox.warning(self, "Validation Error", "Character name and password cannot be empty.")
            return  # 🚨 Do not proceed if fields are blank

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE characters SET name = ?, password = ? WHERE id = ?
                """, (new_name, new_password, character['id']))
                conn.commit()

            # Update in-memory character and UI
            character['name'] = new_name
            character['password'] = new_password
            self.selected_character = character
            current_item.setText(new_name)

            logging.debug(f"Character '{new_name}' modified successfully.")

        except sqlite3.Error as e:
            logging.error(f"Failed to modify character '{name}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to modify character: {e}")

    def delete_character(self):
        """Delete the selected character from the list."""
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for deletion.")
            return

        char_id = current_item.data(Qt.UserRole)  # 🔥 Read ID!

        if char_id is None:
            logging.error("Selected character has no ID associated with it.")
            return

        # Delete from database first
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
                conn.commit()
                logging.debug(f"Character ID {char_id} deleted from database.")
        except sqlite3.Error as e:
            logging.error(f"Failed to delete character ID {char_id} from database: {e}")
            return

        # Then update in-memory list and UI
        self.characters = [char for char in self.characters if char['id'] != char_id]
        self.save_characters()
        self.character_list.takeItem(self.character_list.row(current_item))
        logging.debug(f"Character ID {char_id} deleted from UI.")

    def save_last_active_character(self, character_id):
        """
        Save the last active character's ID to the last_active_character table.
        Ensures that only one entry exists, replacing any previous entry.
        """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM last_active_character")
                cursor.execute('INSERT INTO last_active_character (character_id) VALUES (?)', (character_id,))
                conn.commit()
                logging.debug(f"Last active character set to character_id: {character_id}")
            except sqlite3.Error as e:
                logging.error(f"Failed to save last active character: {e}")

    def load_last_active_character(self):
        """
        Load the last active character from the database by character_id, set the selected character,
        inject their cookie, and auto-login them on load.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT character_id FROM last_active_character")
                result = cursor.fetchone()
                if result:
                    character_id = result[0]
                    self.selected_character = next((char for char in self.characters if char.get('id') == character_id),
                                                   None)

                    if self.selected_character:
                        # Highlight in UI
                        for i in range(self.character_list.count()):
                            if self.character_list.item(i).text() == self.selected_character['name']:
                                self.character_list.setCurrentRow(i)
                                break

                        logging.debug(f"Last active character loaded and selected: {self.selected_character['name']}")

                        self.load_last_destination_for_character(character_id)

                        # ✅ Inject correct cookie for selected character
                        self.switch_to_character(self.selected_character['name'])

                        # ✅ After injecting cookie, navigate and login
                        def delayed_login():
                            self.login_selected_character()

                        QTimer.singleShot(1500, delayed_login)

                    else:
                        logging.warning(f"Last active character ID '{character_id}' not found in character list.")
                        self.set_default_character()

                else:
                    logging.warning("No last active character found in the database.")
                    self.set_default_character()

        except sqlite3.Error as e:
            logging.error(f"Failed to load last active character from database: {e}")
            self.set_default_character()

    def set_default_character(self):
        """
        Set the first character in the database as the default selected character,
        update the UI, and save it as the last active character.
        """
        if self.characters:
            self.selected_character = self.characters[0]
            self.character_list.setCurrentRow(0)
            logging.debug(f"No valid last active character; defaulting to: {self.selected_character['name']}")
            self.save_last_active_character(self.selected_character['id'])
            
            self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        else:
            self.selected_character = None
            logging.warning("No characters available to set as default.")

    def load_last_destination_for_character(self, character_id: int) -> None:
        """Load the last destination from the destinations table."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT col, row FROM destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 1",
                    (character_id,)
                )
                result = cursor.fetchone()
                if result:
                    col, row = result
                    self.destination = (col, row)
                    logging.info(f"Loaded last destination ({col}, {row}) for character {character_id}")
                else:
                    self.destination = None
                    logging.info(f"No previous destination for character {character_id}")

        except sqlite3.Error as e:
            logging.error(f"Failed to load last destination: {e}")

# -----------------------
# Web View Handling
# -----------------------

    def refresh_webview(self):
        """Refresh the webview content."""
        self.website_frame.reload()

    def apply_custom_css(self, css: str = None) -> None:
        """
        Apply either the given raw CSS, or load and apply the current profile's CSS from the database.

        Args:
            css (str, optional): If provided, apply this CSS directly. If None, fetch from the database using the current profile.
        """
        if css is None:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT element, value FROM custom_css WHERE profile_name = ?",
                                   (self.current_css_profile,))
                    css_rules = cursor.fetchall()
            except sqlite3.Error as e:
                logging.error(f"Failed to load CSS rules for profile '{self.current_css_profile}': {e}")
                return

            if not css_rules:
                logging.warning(f"No CSS rules found for profile '{self.current_css_profile}'")
                return

            css = "\n".join(f"{element} {{{value}}}" for element, value in css_rules)

        # Inject the CSS into the web page
        script = f"""
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `{css}`;
            document.head.appendChild(style);
        """
        self.website_frame.page().runJavaScript(script)
        logging.debug("Custom CSS applied.")

    def on_webview_load_finished(self, success):
        if not success:
            logging.error("Failed to load the webpage.")
            QMessageBox.critical(self, "Error", "Failed to load the webpage. Check your network or try again.")
            return

        logging.info("Webpage loaded successfully.")
        self.website_frame.page().toHtml(self.process_html)
        css = self.load_current_css()
        self.apply_custom_css(css)

        if self.pending_login:
            logging.debug("Logging in selected character via JS injection...")
            self.login_selected_character()
            self.pending_login = False
            return  # 🚫 wait for login to finish and reload first

        if self.pending_character_id_for_map:
            logging.debug(f"Loading destination for character {self.pending_character_id_for_map}")
            self.load_destination(self.pending_character_id_for_map)
            self.update_minimap()
            self.pending_character_id_for_map = None

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
                # Set character coordinates directly
                self.character_x, self.character_y = x_coord, y_coord
                logging.debug(f"Set character coordinates to x={self.character_x}, y={self.character_y}")

                # Call recenter_minimap to update the minimap based on character's position
                self.recenter_minimap()

            # Call the method to extract bank coins and pocket changes from the HTML
            self.extract_coins_from_html(html)
            logging.debug("HTML processed successfully for coordinates and coin count.")
        except Exception as e:
            logging.error(f"Unexpected error in process_html: {e}")

    def extract_coordinates_from_html(self, html):

        soup = BeautifulSoup(html, 'html.parser')
        # logging.debug("Extracting coordinates from HTML...")

        # Try to extract the intersection label (like "Aardvark and 1st")
        intersect_span = soup.find('span', class_='intersect')
        text = intersect_span.text.strip() if intersect_span else ""
        # logging.debug(f"Intersection label found: {text}")

        # Check for city limits
        city_limit_cells = soup.find_all('td', class_='cityblock')

        # Extract coordinate inputs
        inputs = soup.find_all('input')
        x_vals = [int(inp['value']) for inp in inputs if
                  inp.get('name') == 'x' and inp.get('value') and inp['value'].isdigit()]
        y_vals = [int(inp['value']) for inp in inputs if
                  inp.get('name') == 'y' and inp.get('value') and inp['value'].isdigit()]
        last_x = max(x_vals) if x_vals else None
        last_y = max(y_vals) if y_vals else None

        # Get the first x/y (center of grid)
        first_x_input = soup.find('input', {'name': 'x'})
        first_y_input = soup.find('input', {'name': 'y'})
        first_x = int(first_x_input['value']) if first_x_input else None
        first_y = int(first_y_input['value']) if first_y_input else None

        logging.debug(f"First detected coordinate: x={first_x}, y={first_y}")
        logging.debug(f"Last detected coordinate: x={last_x}, y={last_y}")

        if city_limit_cells:
            logging.debug(f"Found {len(city_limit_cells)} city limit blocks.")

            # Check for first available coordinates
            first_x_input = soup.find('input', {'name': 'x'})
            first_y_input = soup.find('input', {'name': 'y'})

            first_x = int(first_x_input['value']) if first_x_input else None
            first_y = int(first_y_input['value']) if first_y_input else None

            logging.debug(f"First detected coordinate: x={first_x}, y={first_y}")

            if self.zoom_level == 3:
                if text == "Aardvark and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-left corner detected with full border row: Aardvark and 1st")
                    return -1, -1

                if text == "Zestless and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-right corner detected: Zestless and 1st")
                    return 198, -1

                if text == "Aardvark and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-left corner detected: Aardvark and 100th")
                    return -1, 198

                if text == "Zestless and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-right corner detected: Zestless and 100th")
                    return 198, 198

                # Adjust for Aardvark and NCL
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0 and last_x == 2 and last_y == 1:
                    logging.debug(f"Detected Cell 0,1.")
                    return 0, -1

                # Adjust for WCL and 1st (0,1)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0:
                    logging.debug(f"Detected Cell 0,1.")
                    return -1, 0

                # Adjust for ON Zestless and 1st (198,1)
                if len(city_limit_cells) == 3 and first_x == 198 and first_y == 0:
                    logging.debug("Detected special case: on Zestless and 1st")
                    return first_x, first_y

                # Adjust for Northern Edge (Y=0)
                if len(city_limit_cells) == 3 and first_y == 0:
                    logging.debug(f"Detected Northern City Limit at y={first_y}")
                    return first_x, -1

                # Adjust for Western Edge (X=0)
                if len(city_limit_cells) == 3 and first_x == 0:
                    logging.debug(f"Detected Western City Limit at x={first_x}")
                    return -1, first_y

                # If no adjustments, return detected values
                return first_x, first_y

            if self.zoom_level == 5:
                if text == "Aardvark and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-left corner detected with full border row: Aardvark and 1st")
                    return -2, -2

                if text == "Zestless and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-right corner detected: Zestless and 1st")
                    return 197, -2

                if text == "Aardvark and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-left corner detected: Aardvark and 100th")
                    return -2, 197

                if text == "Zestless and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-right corner detected: Zestless and 100th")
                    return 197, 197

                # Adjust for Aardvark and NCL (1,0)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0 and last_x == 2 and last_y == 1:
                    logging.debug(f"Detected Cell 1,0.")
                    return -1, -2

                # Adjust for WCL and 1st (0,1)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0:
                    logging.debug(f"Detected Cell 0,1.")
                    return -2, -1

                # Adjust for ON Zestless and 1st (198,1)
                if len(city_limit_cells) == 3 and first_x == 198 and first_y == 0:
                    logging.debug("Detected special case: on Zestless and 1st")
                    return first_x - 1, first_y - 1

                # Adjust for Northern Edge (Y=0)
                if len(city_limit_cells) == 3 and first_y == 0:
                    logging.debug(f"Detected Northern City Limit at y={first_y}")
                    return first_x - 1, -2

                # Adjust for Western Edge (X=0)
                if len(city_limit_cells) == 3 and first_x == 0:
                    logging.debug(f"Detected Western City Limit at x={first_x}")
                    return -2, first_y - 1

                return first_x - 1, first_y - 1

            if self.zoom_level == 7:
                if text == "Aardvark and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-left corner detected with full border row: Aardvark and 1st")
                    return -3, -3

                if text == "Zestless and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-right corner detected: Zestless and 1st")
                    return 196, -3

                if text == "Aardvark and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-left corner detected: Aardvark and 100th")
                    return -3, 196

                if text == "Zestless and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-right corner detected: Zestless and 100th")
                    return 196, 196

                # Adjust for Aardvark and NCL (1,0)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0 and last_x == 2 and last_y == 1:
                    logging.debug(f"Detected Cell 1,0.")
                    return -2, -3

                # Adjust for WCL and 1st (0,1)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0:
                    logging.debug(f"Detected Cell 0,1.")
                    return -3, -2

                # Adjust for ON Zestless and 1st (198,1)
                if len(city_limit_cells) == 3 and first_x == 198 and first_y == 0:
                    logging.debug("Detected special case: on Zestless and 1st")
                    return first_x - 2, first_y - 2

                # Adjust for Northern Edge (Y=0)
                if len(city_limit_cells) == 3 and first_y == 0:
                    logging.debug(f"Detected Northern City Limit at y={first_y}")
                    return first_x - 2, -3

                # Adjust for Western Edge (X=0)
                if len(city_limit_cells) == 3 and first_x == 0:
                    logging.debug(f"Detected Western City Limit at x={first_x}")
                    return -3, first_y - 2

                return first_x - 2, first_y - 2

        logging.debug(f"Safe Fallback: x={first_x}, y={first_y}")
        return first_x, first_y

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
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            character_id = self.selected_character['id']
            updates = []

            bank_match = re.search(r"Welcome to Omnibank. Your account has (\d+) coins in it.", html)
            if bank_match:
                bank_coins = int(bank_match.group(1))
                logging.info(f"Bank coins found: {bank_coins}")
                updates.append(("UPDATE coins SET bank = ? WHERE character_id = ?", (bank_coins, character_id)))

            pocket_match = re.search(r"You have (\d+) coins", html) or re.search(r"Money: (\d+) coins", html)
            if pocket_match:
                pocket_coins = int(pocket_match.group(1))
                logging.info(f"Pocket coins found: {pocket_coins}")
                updates.append(("UPDATE coins SET pocket = ? WHERE character_id = ?", (pocket_coins, character_id)))

            deposit_match = re.search(r"You deposit (\d+) coins.", html)
            if deposit_match:
                deposit_coins = int(deposit_match.group(1))
                logging.info(f"Deposit found: {deposit_coins} coins")
                updates.append(("UPDATE coins SET pocket = pocket - ? WHERE character_id = ?", (deposit_coins, character_id)))

            withdraw_match = re.search(r"You withdraw (\d+) coins.", html)
            if withdraw_match:
                withdraw_coins = int(withdraw_match.group(1))
                logging.info(f"Withdrawal found: {withdraw_coins} coins")
                updates.append(("UPDATE coins SET pocket = pocket + ? WHERE character_id = ?", (withdraw_coins, character_id)))

            transit_match = re.search(r"It costs 5 coins to ride. You have (\d+).", html)
            if transit_match:
                coins_in_pocket = int(transit_match.group(1))
                logging.info(f"Transit found: Pocket coins updated to {coins_in_pocket}")
                updates.append(("UPDATE coins SET pocket = ? WHERE character_id = ?", (coins_in_pocket, character_id)))

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

            for action, pattern in actions.items():
                match = re.search(pattern, html)
                if match:
                    coin_count = int(match.group(1 if action != 'given_coins' else 2))
                    if action == 'getting_robbed':
                        vamp_name = match.group(1)
                        updates.append(("UPDATE coins SET pocket = pocket - ? WHERE character_id = ?", (coin_count, character_id)))
                        logging.info(f"Lost {coin_count} coins to {vamp_name}.")
                    else:
                        updates.append(("UPDATE coins SET pocket = pocket + ? WHERE character_id = ?", (coin_count, character_id)))
                        logging.info(f"Gained {coin_count} coins from {action}.")
                    break

            for query, params in updates:
                cursor.execute(query, params)
            conn.commit()
            logging.info(f"Updated coins for character ID {character_id}.")

    def switch_css_profile(self, profile_name: str) -> None:
        self.current_css_profile = profile_name
        self.apply_custom_css()
        logging.info(f"Switched to profile: {profile_name} and applied CSS")

# -----------------------
# Minimap Drawing and Update
# -----------------------

    def draw_minimap(self) -> None:
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

        font = painter.font()
        font.setPointSize(font_size)
        painter.setFont(font)

        font_metrics = QFontMetrics(font)

        logging.debug(f"Drawing minimap with column_start={self.column_start}, row_start={self.row_start}, "f"zoom_level={self.zoom_level}, block_size={block_size}")

        def draw_label_box(x, y, width, height, bg_color, text):
            """
            Draws a text label box with a background color, white border, and properly formatted text.
            """
            # Draw background
            painter.fillRect(QRect(x, y, width, height), bg_color)

            # Draw white border
            painter.setPen(QColor('white'))
            painter.drawRect(QRect(x, y, width, height))

            # Set font
            font = painter.font()
            font.setPointSize(max(4, min(8, block_size // 4)))  # Keep text readable
            painter.setFont(font)

            # Draw text (aligned top-center, allowing wrapping)
            text_rect = QRect(x, y, width, height)
            painter.setPen(QColor('white'))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap, text)

        # Draw the grid
        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                column_index = self.column_start + j
                row_index = self.row_start + i

                x0, y0 = j * block_size, i * block_size
                logging.debug(f"Drawing grid cell at column_index={column_index}, row_index={row_index}, "f"x0={x0}, y0={y0}")

                # Draw the cell background
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                # Special location handling
                column_name = next((name for name, coord in self.columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in self.rows.items() if coord == row_index), None)

                # Draw cell background color to match in-game city grid
                if column_index < 1 or column_index > 200 or row_index < 1 or row_index > 200:
                    # Map edges (border)
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, QColor(self.color_mappings["edge"]))
                elif column_index % 2 == 0 or row_index % 2 == 0:
                    # If either coordinate is even → Streets (Gray)
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, QColor(self.color_mappings["street"]))
                else:
                    # Both coordinates odd → City Blocks (Black)
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, QColor(self.color_mappings["alley"]))

                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"
                    label_height = block_size // 3  # Set label height
                    draw_label_box(x0 + 2, y0 + 2, block_size - 4, label_height, self.color_mappings["intersect"], label_text)

        # Draw special locations (banks with correct offsets)
        for bank_key in self.banks_coordinates.keys():
            if " & " in bank_key:  # Ensure it's in the correct format
                col_name, row_name = bank_key.split(" & ")
                col = self.columns.get(col_name, 0)
                row = self.rows.get(row_name, 0)

                if col is not None and row is not None:
                    adjusted_column_index = col + 1
                    adjusted_row_index = row + 1

                    draw_label_box(
                        (adjusted_column_index - self.column_start) * block_size,
                        (adjusted_row_index - self.row_start) * block_size,
                        block_size, block_size // 3, self.color_mappings["bank"], "BANK"
                    )
                else:
                    logging.warning(f"Skipping bank at {col_name} & {row_name} due to missing coordinates")
            else:
                logging.warning(f"Skipping invalid bank_key format: {bank_key}")


        # Draw other locations without the offset
        for name, (column_index, row_index) in self.taverns_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, block_size // 3, self.color_mappings["tavern"], name
                )

        for name, (column_index, row_index) in self.transits_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, block_size // 3, self.color_mappings["transit"], name
                )

        for name, (column_index, row_index) in self.user_buildings_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, block_size // 3, self.color_mappings["user_building"], name
                )

        for name, (column_index, row_index) in self.shops_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, block_size // 3, self.color_mappings["shop"], name
                )

        for name, (column_index, row_index) in self.guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, block_size // 3, self.color_mappings["guild"], name
                )

        for name, (column_index, row_index) in self.places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                # Special-case Graveyard color
                if name.lower() == "graveyard":
                    color = self.color_mappings.get("graveyard", self.color_mappings["placesofinterest"])
                else:
                    color = self.color_mappings["placesofinterest"]

                logging.debug(f"Drawing {name} with color {color.name()}")
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, block_size // 3,
                    color, name
                )

            # Get current location
            current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

            # Find and draw lines to nearest locations
            nearest_tavern = self.find_nearest_tavern(current_x, current_y)
            nearest_bank = self.find_nearest_bank(current_x, current_y)
            nearest_transit = self.find_nearest_transit(current_x, current_y)

            # Draw nearest tavern line
            if nearest_tavern:
                nearest_tavern_coords = nearest_tavern[0][1]
                painter.setPen(QPen(QColor('orange'), 3))
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (nearest_tavern_coords[0] - self.column_start) * block_size + block_size // 2,
                    (nearest_tavern_coords[1] - self.row_start) * block_size + block_size // 2
                )

            # Draw nearest bank line
            if nearest_bank:
                nearest_bank_coords = nearest_bank  # Already a (col, row) tuple
                painter.setPen(QPen(QColor('blue'), 3))
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (nearest_bank_coords[0] + 1 - self.column_start) * block_size + block_size // 2,
                    (nearest_bank_coords[1] + 1 - self.row_start) * block_size + block_size // 2
                )

            # Draw nearest transit line
            if nearest_transit:
                nearest_transit_coords = nearest_transit[0][1]
                painter.setPen(QPen(QColor('red'), 3))
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (nearest_transit_coords[0] - self.column_start) * block_size + block_size // 2,
                    (nearest_transit_coords[1] - self.row_start) * block_size + block_size // 2
                )

            # Draw destination line
            if self.destination:
                painter.setPen(QPen(QColor('green'), 3))
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
        if not self.is_updating_minimap:
            self.is_updating_minimap = True
            self.draw_minimap()
            self.update_info_frame()
            if hasattr(self, 'compass_overlay') and self.compass_overlay.isVisible():
                self.show_compass_overlay()
            self.is_updating_minimap = False

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
        distances = [(max(abs(lx - x), abs(ly - y)), (lx, ly)) for lx, ly in locations]
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

    def find_nearest_bank(self, current_x, current_y):
        min_distance = float("inf")
        nearest_bank = None

        for bank_key, (col_name, row_name) in self.banks_coordinates.items():
            if isinstance(bank_key, str):  # Convert from street name format if necessary
                col_name, row_name = bank_key.split(" & ")

            col = self.columns.get(col_name, 0)
            row = self.rows.get(row_name, 0)

            if col and row:
                distance = abs(col - current_x) + abs(row - current_y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_bank = (col, row)  # Return actual coordinates

        return nearest_bank  # Returns (x, y) tuple

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
        """Open the set destination dialog to select a new destination."""
        dialog = SetDestinationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Reload the destination from the DB to ensure it's per-character and persisted
            if self.selected_character:
                self.load_last_destination_for_character(self.selected_character['id'])
            self.update_minimap()

    def get_current_destination(self, character_id: int):
        """Retrieve the latest destination for the selected character."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT col, row FROM destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 1", (character_id,))
            result = cursor.fetchone()
            return (result[0], result[1]) if result else None

    def load_destination(self, character_id: int | None = None) -> None:
        """
        Load the destination for a given character (or selected character if not provided).
        """
        if character_id is None:
            if not self.selected_character:
                logging.warning("No character selected; cannot load destination.")
                return
            character_id = self.selected_character.get('id')

        if not character_id:
            logging.warning("Character ID missing; cannot load destination.")
            return

        destination_coords = self.get_current_destination(character_id)
        if destination_coords:
            self.destination = destination_coords
            logging.info(f"Loaded destination {self.destination} for character {character_id}")
        else:
            self.destination = None
            logging.info(f"No destination found for character {character_id}")

# -----------------------
# Minimap Controls
# -----------------------

    def zoom_in(self):
        """
        Zoom in the minimap, ensuring the character stays centered.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 2
            self.zoom_level_changed = True
            self.save_zoom_level_to_database()
            self.website_frame.page().toHtml(self.process_html)

    def zoom_out(self):
        """
        Zoom out the minimap, ensuring the character stays centered.
        """
        if self.zoom_level < 7:
            self.zoom_level += 2
            self.zoom_level_changed = True
            self.save_zoom_level_to_database()
            self.website_frame.page().toHtml(self.process_html)

    def save_zoom_level_to_database(self):
        """Save the current zoom level to the settings table in the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO settings (setting_name, setting_value)
                    VALUES ('minimap_zoom', ?)
                    ON CONFLICT(setting_name) DO UPDATE SET setting_value = ?;
                """, (self.zoom_level, self.zoom_level))
                conn.commit()
                logging.debug(f"Zoom level saved to database: {self.zoom_level}")
        except sqlite3.Error as e:
            logging.error(f"Failed to save zoom level to database: {e}")

    def load_zoom_level_from_database(self):
        """
        Load the saved zoom level from the settings table in the database.
        If no value is found, set it to the default (3).
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                result = cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'minimap_zoom'").fetchone()
                self.zoom_level = int(result[0]) if result else 3
                logging.debug(f"Zoom level loaded from database: {self.zoom_level}")
        except sqlite3.Error as e:
            self.zoom_level = 3  # Fallback default zoom level
            logging.error(f"Failed to load zoom level from database: {e}")

    def recenter_minimap(self):
        """
        Recenter the minimap so that the character's location is at the center cell,
        including visible but non-traversable areas beyond the traversable range.
        """
        if not hasattr(self, 'character_x') or not hasattr(self, 'character_y'):
            logging.error("Character position not set. Cannot recenter minimap.")
            return

        logging.debug(f"Before recentering: character_x={self.character_x}, character_y={self.character_y}")

        # Calculate zoom offset (-1 for 5x5, -2 for 7x7, etc.)
        if self.zoom_level == 3:
            zoom_offset = -1
        elif self.zoom_level == 5:
            zoom_offset = -2
        elif self.zoom_level == 7:
            zoom_offset = -3
        else:
            zoom_offset = -(self.zoom_level // 2)  # Safe fallback
        logging.debug(f"Zoom Level: {self.zoom_level}")
        logging.debug(f"Zoom Offset: {zoom_offset}")
        logging.debug(f"Debug: char_y={self.character_y}, row_start={self.row_start}, zoom_offset={zoom_offset}")
        logging.debug(f"Clamping min: {min(self.character_y + zoom_offset, 200 - self.zoom_level)}")

        self.column_start = self.character_x + 1
        self.row_start = self.character_y + 1

        logging.debug(f"Recentered minimap: x={self.character_x}, y={self.character_y}, col_start={self.column_start}, row_start={self.row_start}")
        self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location.
        Adjusts the minimap's starting column and row based on the selected location from the combo boxes.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()

        if column_name in self.columns:
            self.column_start = self.columns[column_name] - self.zoom_level // 2
            logging.debug(f"Set column_start to {self.column_start} for column '{column_name}'")
        else:
            logging.error(f"Column '{column_name}' not found in self.columns")

        if row_name in self.rows:
            self.row_start = self.rows[row_name] - self.zoom_level // 2
            logging.debug(f"Set row_start to {self.row_start} for row '{row_name}'")
        else:
            logging.error(f"Row '{row_name}' not found in self.rows")

        # Update the minimap after setting the new location
        self.update_minimap()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks on the minimap to recenter it."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Map global click position to minimap's local coordinates
            local_position = self.minimap_label.mapFromGlobal(event.globalPosition().toPoint())
            click_x, click_y = local_position.x(), local_position.y()

            # Validate click is within the minimap
            if 0 <= click_x < self.minimap_label.width() and 0 <= click_y < self.minimap_label.height():
                # Calculate relative coordinates and block size
                block_size = self.minimap_size // self.zoom_level
                clicked_column = self.column_start + (click_x // block_size)
                clicked_row = self.row_start + (click_y // block_size)
                center_offset = self.zoom_level // 2
                min_start, max_start = -(self.zoom_level // 2), 201 + (self.zoom_level // 2) - self.zoom_level
                self.column_start = max(min_start, min(clicked_column - center_offset, max_start))
                self.row_start = max(min_start, min(clicked_row - center_offset, max_start))
                logging.debug(f"Click at ({click_x}, {click_y}) -> Cell: ({clicked_column}, {clicked_row})")
                logging.debug(f"New minimap start: column={self.column_start}, row={self.row_start}")

                # Update the minimap display
                self.update_minimap()
            else:
                logging.debug(f"Click ({click_x}, {click_y}) is outside the minimap bounds.")

    def cycle_character(self, direction):
        """Cycle through characters in the QListWidget."""
        current_row = self.character_list.currentRow()
        new_row = (current_row + direction) % self.character_list.count()
        if new_row < 0:
            new_row = self.character_list.count() - 1
        self.character_list.setCurrentRow(new_row)
        self.on_character_selected(self.character_list.item(new_row))

    def open_SetDestinationDialog(self):
        """
        Open the set destination dialog.
        Opens a dialog that allows the user to set a destination and updates the minimap if confirmed.
        """
        dialog = SetDestinationDialog(self)

        # Execute dialog and check for acceptance
        if dialog.exec() == QDialog.accepted:
            # Load the newly set destination from the database
            self.load_destination()

            # Update the minimap with the new destination
            self.update_minimap()

    def save_to_recent_destinations(self, character_id: int, col: int, row: int):
        """
        Save the current destination to the recent destinations for the specific character,
        keeping only the last 10 entries per character.

        Args:
            character_id (int): ID of the character.
            col (int): Column coordinate of the destination.
            row (int): Row coordinate of the destination.
        """
        if character_id is None:
            return

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO recent_destinations (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                """, (character_id, col, row))

                cursor.execute("""
                    DELETE FROM recent_destinations 
                    WHERE character_id = ? AND id NOT IN (
                        SELECT id FROM recent_destinations
                        WHERE character_id = ?
                        ORDER BY timestamp DESC LIMIT 10
                    )
                """, (character_id, character_id))

                conn.commit()
                logging.info(f"Destination ({col}, {row}) saved for character ID {character_id}.")

        except sqlite3.Error as e:
            logging.error(f"Failed to save recent destination: {e}")

    def eventFilter(self, source, event):
        # Only clear on actual user interaction, not initial app load
        if event.type() == QEvent.Type.MouseButtonPress:
            if source in (self.combo_columns, self.combo_rows) and source.isEditable():
                source.lineEdit().clear()
                source.lineEdit().setFocus()

        elif event.type() == QEvent.Type.KeyPress:
            if isinstance(source, QLineEdit) and source.text().startswith("Select"):
                source.clear()

        return super().eventFilter(source, event)

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

        # Closest Bank
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        if nearest_bank:
            bank_coords = nearest_bank  # No need for `[0][1]`
            adjusted_bank_coords = (bank_coords[0] + 1, bank_coords[1] + 1)
            bank_ap_cost = self.calculate_ap_cost((current_x, current_y), adjusted_bank_coords)
            bank_intersection = self.get_intersection_name(adjusted_bank_coords)
            self.bank_label.setText(f"Bank\n{bank_intersection} - AP: {bank_ap_cost}")

        # Closest Transit
        nearest_transit = self.find_nearest_transit(current_x, current_y)
        if nearest_transit:
            transit_coords = nearest_transit[0][1]
            transit_name = next(name for name, coords in self.transits_coordinates.items() if coords == transit_coords)
            transit_ap_cost = self.calculate_ap_cost((current_x, current_y), transit_coords)
            transit_intersection = self.get_intersection_name(transit_coords)
            self.transit_label.setText(f"Transit - {transit_name}\n{transit_intersection} - AP: {transit_ap_cost}")

        # Closest Tavern
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        if nearest_tavern:
            tavern_coords = nearest_tavern[0][1]
            tavern_name = next(name for name, coords in self.taverns_coordinates.items() if coords == tavern_coords)
            tavern_ap_cost = self.calculate_ap_cost((current_x, current_y), tavern_coords)
            tavern_intersection = self.get_intersection_name(tavern_coords)
            self.tavern_label.setText(f"{tavern_name}\n{tavern_intersection} - AP: {tavern_ap_cost}")

        # Set Destination Info
        if self.destination:
            destination_coords = self.destination
            destination_ap_cost = self.calculate_ap_cost((current_x, current_y), destination_coords)
            destination_intersection = self.get_intersection_name(destination_coords)

            # Check for a named place at destination
            place_name = next(
                (name for name, coords in {
                    **self.guilds_coordinates,
                    **self.shops_coordinates,
                    **self.user_buildings_coordinates,
                    **self.places_of_interest_coordinates
                }.items() if coords == destination_coords),
                None
            )

            destination_label_text = place_name if place_name else "Set Destination"
            self.destination_label.setText(
                f"{destination_label_text}\n{destination_intersection} - AP: {destination_ap_cost}"
            )

            # Transit-Based AP Cost for Set Destination
            nearest_transit_to_character = self.find_nearest_transit(current_x, current_y)
            nearest_transit_to_destination = self.find_nearest_transit(destination_coords[0], destination_coords[1])

            if nearest_transit_to_character and nearest_transit_to_destination:
                char_transit_coords = nearest_transit_to_character[0][1]
                dest_transit_coords = nearest_transit_to_destination[0][1]
                char_to_transit_ap = self.calculate_ap_cost((current_x, current_y), char_transit_coords)
                dest_to_transit_ap = self.calculate_ap_cost(destination_coords, dest_transit_coords)
                total_ap_via_transit = char_to_transit_ap + dest_to_transit_ap

                # Get transit names
                char_transit_name = next(
                    name for name, coords in self.transits_coordinates.items() if coords == char_transit_coords)
                dest_transit_name = next(
                    name for name, coords in self.transits_coordinates.items() if coords == dest_transit_coords)

                # Update the transit destination label to include destination name
                destination_name = place_name if place_name else "Set Destination"
                self.transit_destination_label.setText(
                    f"{destination_name} - {char_transit_name} to {dest_transit_name}\n"
                    f"{self.get_intersection_name(dest_transit_coords)} - Total AP: {total_ap_via_transit}"
                )

            else:
                self.transit_destination_label.setText("Transit Route Info Unavailable")

        else:
            # Clear labels when no destination is set
            self.destination_label.setText("No Destination Set")
            self.transit_destination_label.setText("No Destination Set")

        self.update_ap_direction_label()

    def get_intersection_name(self, coords):
        """
        Get the intersection name for the given coordinates, including edge cases.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: Readable intersection like "Nickel & 55th" or fallback "x, y".
        """
        x, y = coords

        # Try direct match
        column_name = next((name for name, coord in self.columns.items() if coord == x), None)
        row_name = next((name for name, coord in self.rows.items() if coord == y), None)

        # Fallback to offset-based match
        if not column_name:
            column_name = next((name for name, coord in self.columns.items() if coord == x - 1), None)
        if not row_name:
            row_name = next((name for name, coord in self.rows.items() if coord == y - 1), None)

        if column_name and row_name:
            return f"{column_name} & {row_name}"
        elif column_name:
            return f"{column_name} & Unknown Row"
        elif row_name:
            return f"Unknown Column & {row_name}"
        else:
            return f"{x}, {y}"  # raw coords as fallback

    def update_ap_direction_label(self):
        """
        Update the compass label at the top of the screen.
        Shows either the selected route from overlay or the shortest by default.
        """
        if not self.destination:
            self.ap_direction_label.setText("Compass: None")
            return

        # If user clicked a route, keep using the stored text
        if self.selected_route_label and self.selected_route_description:
            self.ap_direction_label.setText(f"Compass: {self.selected_route_description}")
            return

        # Otherwise, fallback to default route selection
        direct_route, transit_route = self.get_compass_routes()
        label, route_info = (
            ("Direct Route", direct_route)
            if direct_route[0] <= transit_route[0]
            else ("Transit Route", transit_route)
        )

        ap_cost, description = route_info
        self.ap_direction_label.setText(f"Compass: {description}")

# -----------------------
# Menu Actions
# -----------------------

    def open_discord(self):
        """Opens a dialog with a listing of public Discord servers for the community"""
        dialog = DiscordServerDialog(self)
        dialog.exec()

    def open_website(self):
        """Open the RBC Website in the system's default web browser."""
        webbrowser.open('https://lollis-home.ddns.net/viewpage.php?page_id=2')

    def show_about_dialog(self):
        """
        Display an "About" dialog with details about the RBC City Map application.
        """
        QMessageBox.about(self, "About RBC City Map",
                          "RBC City Map Application\n\n"
                          f"Version {VERSION_NUMBER}\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Development team shown in credits.\n\n\n"
                          "This program is based on the LIAM² app by Leprichaun")

    def show_credits_dialog(self):
        """
        Display a "Credits" dialog with a list of contributors to the RBC City Map project.
        """
        credits_text = (
            "Credits to the team who made this happen:\n\n"
            "Windows: Jonathan Lollis (Nesmuth), Justin Solivan\n\n"
            "Apple OSx Compatibility: Joseph Lemois\n\n"
            "Linux Compatibility: Josh \"Blaskewitts\" Corse, Fern Lovebond\n\n"
            "Design and Layout: Shuvi, Blair Wilson (Ikunnaprinsess)\n\n\n\n"
            "Special Thanks:\n\n"
            "Cain \"Leprechaun\" McBride for the LIAM² program \nthat inspired this program\n\n"
            "Cliff Burton for A View in the Dark which is \nwhere Shops and Guilds data is retrieved\n\n"
            "Everyone who contributes to the \nRavenBlack Wiki and A View in the Dark\n\n"
            "Anders for RBNav and the help along the way\n\n\n\n"
            "Most importantly, thank YOU for using this app. \nWe all hope it serves you well!"
        )

        credits_dialog = QDialog()
        credits_dialog.setWindowTitle('Credits')
        self.setWindowIcon(APP_ICON)
        credits_dialog.setFixedSize(650, 400)

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
        animation = QPropertyAnimation(credits_label, QByteArray(b"geometry"))
        animation.setDuration(35000)
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        def close_after_delay():
            QTimer.singleShot(2500, credits_dialog.accept)
        animation.finished.connect(close_after_delay)
        animation.start()

        credits_dialog.exec()

    def open_database_viewer(self):
        """
        Open the database viewer to browse and inspect data from the RBC City Map database.
        """
        try:
            # Create a new SQLite database connection every time the viewer is opened
            database_connection = sqlite3.connect(DB_PATH)

            # Show the database viewer, passing the new connection
            self.database_viewer = DatabaseViewer(database_connection)
            self.database_viewer.show()
        except Exception as e:
            logging.error(f"Error opening Database Viewer: {e}")
            QMessageBox.critical(self, "Error", f"Error opening Database Viewer: {e}")

    def open_log_viewer(self):
        self.log_viewer = LogViewer(self, LOG_DIR)  # or pass None if you want it fully standalone
        self.log_viewer.show()

    def fetch_table_data(self, cursor, table_name):
        """
        Fetch data from the specified table and return it as a list of tuples, including column names.

        Args:
            cursor: SQLite cursor object.
            table_name: Name of the table to fetch data from.

        Returns:
            Tuple: (List of column names, List of table data)
        """
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        column_names = [col[1] for col in cursor.fetchall()]
        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()
        return column_names, data

    def show_compass_overlay(self):
        if not self.destination:
            QMessageBox.information(self, "No Destination", "Please set a destination first.")
            return

        direct_route, transit_route = self.get_compass_routes()

        if hasattr(self, 'compass_overlay') and self.compass_overlay.isVisible():
            self.compass_overlay.refresh(direct_route, transit_route)
        else:
            self.compass_overlay = CompassOverlay(direct_route, transit_route, self)
            self.compass_overlay.show()

    def get_compass_routes(self):
        def get_arrow_description(start, end):
            dx = end[0] - start[0]
            dy = end[1] - start[1]

            steps_diagonal = min(abs(dx), abs(dy))
            steps_straight = abs(abs(dx) - abs(dy))

            diagonal_arrow = ''
            if dx < 0 and dy < 0:
                diagonal_arrow = '↖'
            elif dx > 0 and dy < 0:
                diagonal_arrow = '↗'
            elif dx < 0 and dy > 0:
                diagonal_arrow = '↙'
            elif dx > 0 and dy > 0:
                diagonal_arrow = '↘'

            straight_arrow = ''
            if abs(dx) > abs(dy):
                straight_arrow = '→' if dx > 0 else '←'
            elif abs(dy) > abs(dx):
                straight_arrow = '↓' if dy > 0 else '↑'

            parts = []
            if steps_diagonal:
                parts.append(f"{steps_diagonal}{diagonal_arrow}")
            if steps_straight:
                parts.append(f"{steps_straight}{straight_arrow}")
            return " + ".join(parts) if parts else "0⦿"

        current_x = self.column_start + self.zoom_level // 2
        current_y = self.row_start + self.zoom_level // 2
        dest_x, dest_y = self.destination

        # ----------------------------
        # Direct Route
        # ----------------------------
        direct_ap = max(abs(dest_x - current_x), abs(dest_y - current_y))
        direct_desc = get_arrow_description((current_x, current_y), (dest_x, dest_y))
        direct_route = (direct_ap, direct_desc)

        # ----------------------------
        # Transit Route
        # ----------------------------
        nearest_transit_to_character = self.find_nearest_transit(current_x, current_y)
        nearest_transit_to_destination = self.find_nearest_transit(dest_x, dest_y)

        if nearest_transit_to_character and nearest_transit_to_destination:
            char_transit_coords = nearest_transit_to_character[0][1]
            dest_transit_coords = nearest_transit_to_destination[0][1]

            char_to_transit_ap = self.calculate_ap_cost((current_x, current_y), char_transit_coords)
            dest_to_transit_ap = self.calculate_ap_cost((dest_x, dest_y), dest_transit_coords)
            total_ap_transit = char_to_transit_ap + dest_to_transit_ap

            # Get arrow segments for each leg
            to_transit_arrows = get_arrow_description((current_x, current_y), char_transit_coords)
            from_transit_arrows = get_arrow_description(dest_transit_coords, (dest_x, dest_y))

            transit_desc = f"{to_transit_arrows} + Transit + {from_transit_arrows}"
            transit_route = (total_ap_transit, transit_desc)
        else:
            transit_route = (9999, "Transit route unavailable")

        return direct_route, transit_route

    def set_compass_display_from_overlay(self, label, route_info):
        """
        Called when user clicks a route in CompassOverlay.
        Stores and displays the selected route’s full directional breakdown.
        """
        self.selected_route_label = label
        ap_cost, direction_desc = route_info
        self.selected_route_description = direction_desc
        self.ap_direction_label.setText(f"Compass: {direction_desc}")

# -----------------------
# Database Viewer Class
# -----------------------

class DatabaseViewer(QDialog):
    """
    Graphical interface for viewing SQLite database tables in a tabbed layout.
    """

    def __init__(self, db_connection, parent=None) -> None:
        """
        Initialize the DatabaseViewer with a database connection.

        Args:
            db_connection: Active SQLite database connection.
            parent: Parent widget (default is None).
        """
        super().__init__(parent)  # Ensure it gets QDialog properties
        self.setWindowTitle('SQLite Database Viewer')
        self.setWindowIcon(APP_ICON)
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.db_connection = db_connection
        self.cursor = db_connection.cursor()

        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]
            for table_name in tables:
                column_names, data = self.get_table_data(table_name)
                self.add_table_tab(table_name, column_names, data)
            logging.debug(f"Loaded {len(tables)} tables into viewer")
        except sqlite3.Error as e:
            logging.error(f"Failed to load tables: {e}")
            QMessageBox.critical(self, "Error", "Failed to load database tables.")

    def get_table_data(self, table_name: str) -> tuple[list[str], list[tuple]]:
        """
        Fetch column names and data for a specified table.

        Args:
            table_name: Name of the table to query.

        Returns:
            tuple: (list of column names, list of row data).
        """
        try:
            self.cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            column_names = [col[1] for col in self.cursor.fetchall()]
            self.cursor.execute(f"SELECT * FROM `{table_name}`")
            data = self.cursor.fetchall()
            return column_names, data
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch data for table '{table_name}': {e}")
            return [], []

    def add_table_tab(self, table_name: str, column_names: list[str], data: list[tuple]) -> None:
        """
        Add a tab displaying table data.

        Args:
            table_name: Name of the table.
            column_names: List of column names.
            data: List of row data tuples.
        """
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(column_names))
        table_widget.setHorizontalHeaderLabels(column_names)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value or "")))

        table_widget.resizeColumnsToContents()  # Improve readability
        self.tab_widget.addTab(table_widget, table_name)
        logging.debug(f"Added tab for table '{table_name}' with {len(data)} rows")

    def closeEvent(self, event) -> None:
        """
        Close database connection when the window is closed.

        Args:
            event: QCloseEvent object.
        """
        try:
            self.cursor.close()
            self.db_connection.close()
            logging.debug("Database connection closed")
        except sqlite3.Error as e:
            logging.error(f"Failed to close database connection: {e}")
        event.accept()

# -----------------------
# Character Dialog Class
# -----------------------

class CharacterDialog(QDialog):
    """
    A dialog for adding or modifying a character, with validation.
    """

    def __init__(self, parent=None, character=None):
        super().__init__(parent)
        self.setWindowTitle("Character")
        self.setWindowIcon(APP_ICON)

        # Input fields
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        # Form layout
        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        # OK and Cancel buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)
        self.setLayout(layout)

        # Connect buttons
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)

    def validate_and_accept(self):
        """Check if inputs are valid before accepting."""
        name = self.name_edit.text().strip()
        password = self.password_edit.text().strip()

        if not name or not password:
            QMessageBox.warning(self, "Validation Error", "Character name and password cannot be empty.")
            return  # 🚨 Do NOT call accept(), keep dialog open

        self.accept()  # ✅ Only accept if valid

# -----------------------
# Theme Customization Dialog
# -----------------------

class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing application theme colors for UI and minimap elements.
    """

    def __init__(self, parent=None, color_mappings: dict | None = None) -> None:
        """
        Initialize the theme customization dialog.

        Args:
            parent: Parent widget (optional).
            color_mappings: Current color mappings dict (optional).
        """
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')
        self.setWindowIcon(APP_ICON)
        self.setMinimumSize(400, 300)

        self.color_mappings = color_mappings.copy() if color_mappings else {}

        # Main layout
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Tabs
        self.ui_tab = QWidget()
        self.minimap_tab = QWidget()
        self.tabs.addTab(self.ui_tab, "UI, Buttons, and Text")
        self.tabs.addTab(self.minimap_tab, "Minimap Content")

        self.setup_ui_tab()
        self.setup_minimap_tab()

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        logging.debug("Theme customization dialog initialized")

    def setup_ui_tab(self) -> None:
        """Set up the UI tab for background, text, and button color customization."""
        layout = QGridLayout(self.ui_tab)
        ui_elements = [
            'background',
            'text_color',
            'button_color',
            'button_hover_color',
            'button_pressed_color',
            'button_border_color'
        ]

        for idx, elem in enumerate(ui_elements):
            color_square = QLabel(self.ui_tab)
            color_square.setFixedSize(20, 20)
            color = self.color_mappings.get(elem, QColor('white'))
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color', self.ui_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.replace('_', ' ').capitalize()}:", self.ui_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def setup_minimap_tab(self) -> None:
        """Set up the Minimap tab for customizing minimap element colors."""
        layout = QGridLayout(self.minimap_tab)
        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']

        for idx, elem in enumerate(minimap_elements):
            color_square = QLabel(self.minimap_tab)
            color_square.setFixedSize(20, 20)
            color = self.color_mappings.get(elem, QColor('white'))

            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color', self.minimap_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.capitalize()}:", self.minimap_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def change_color(self, element_name: str, color_square: QLabel) -> None:
        """
        Open a color picker to update an element’s color.

        Args:
            element_name: Key in color_mappings to update.
            color_square: QLabel displaying the current color.
        """
        color = QColorDialog.getColor(self.color_mappings.get(element_name, QColor('white')), self)
        if color.isValid():
            self.color_mappings[element_name] = color
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)
            logging.debug(f"Changed color for '{element_name}' to {color.name()}")

    def apply_theme(self) -> None:
        """Apply the selected theme colors to the dialog’s stylesheet."""
        try:
            bg_color = self.color_mappings.get('background', QColor('white')).name()
            text_color = self.color_mappings.get('text_color', QColor('black')).name()
            btn_color = self.color_mappings.get('button_color', QColor('lightgrey')).name()
            btn_hover_color = self.color_mappings.get('button_hover_color', QColor('grey')).name()
            btn_pressed_color = self.color_mappings.get('button_pressed_color', QColor('darkgrey')).name()
            btn_border_color = self.color_mappings.get('button_border_color', QColor('black')).name()

            self.setStyleSheet(
                f"""
                QWidget {{
                    background-color: {bg_color};
                }}
                QPushButton {{
                    background-color: {btn_color};
                    color: {text_color};
                    border: 2px solid {btn_border_color};
                    border-radius: 6px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {btn_pressed_color};
                }}
                QLabel {{
                    color: {text_color};
                }}
                """
            )
            logging.debug("Theme applied to dialog")
        except Exception as e:
            logging.error(f"Failed to apply theme to dialog: {e}")
            self.setStyleSheet("")  # Reset on failure

# -----------------------
# CSS Customization Dialog
# -----------------------

class CSSCustomizationDialog(QDialog):
    def __init__(self, parent: QWidget = None, current_profile: str = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.current_profile = current_profile or self.get_current_profile()
        self.setWindowTitle("CSS Customization")
        self.setWindowIcon(APP_ICON)
        self.resize(600, 400)
        self.tabs = {}
        self.setup_ui()
        self.load_existing_customizations()
        logging.debug(f"CSSCustomizationDialog initialized with profile '{self.current_profile}'")

    def get_current_profile(self) -> str:
        """Retrieve the current CSS profile from settings."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'css_profile'")
                result = cursor.fetchone()
                return result[0] if result else "Default"
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve current profile: {e}")
            return "Default"

    def update_current_profile(self, profile: str) -> None:
        """Update the css_profile setting in the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (setting_name, setting_value) VALUES (?, ?)",
                    ("css_profile", profile)
                )
                conn.commit()
            self.current_profile = profile
            logging.debug(f"Updated css_profile to: {profile}")
        except sqlite3.Error as e:
            logging.error(f"Failed to update css_profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update profile: {e}")

    def setup_ui(self) -> None:
        """Set up the UI for CSS customization."""
        main_layout = QVBoxLayout(self)

        # Profile selection
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profile:"))
        self.profile_dropdown = QComboBox()
        self.load_profiles()
        self.profile_dropdown.setCurrentText(self.current_profile)
        self.profile_dropdown.currentTextChanged.connect(self.on_profile_change)
        profile_layout.addWidget(self.profile_dropdown)

        new_profile_btn = QPushButton("New Profile")
        new_profile_btn.clicked.connect(self.create_new_profile)
        profile_layout.addWidget(new_profile_btn)

        delete_profile_btn = QPushButton("Delete Profile")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_layout.addWidget(delete_profile_btn)

        main_layout.addLayout(profile_layout)

        # Tabs for CSS categories
        self.tab_widget = QTabWidget()
        self.add_tab("Background", ["BODY"])
        self.add_tab("Text", ["H1", "P", "A", "TD", "DIV"])
        self.add_tab("City Elements", ["TD.cityblock", "TD.intersect", "TD.street", "TD.city"])
        self.add_tab("Special Elements", [
            "SPAN.intersect", "SPAN.transit", "SPAN.pub", "SPAN.bank", "SPAN.shop",
            "SPAN.grave", "SPAN.pk", "SPAN.lair", "SPAN.alchemy"
        ])
        main_layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload CSS File")
        upload_btn.clicked.connect(self.upload_css_file)
        button_layout.addWidget(upload_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_customizations)
        button_layout.addWidget(clear_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.save_and_apply_changes)
        button_layout.addWidget(apply_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Ensure preview updates even if currentTextChanged isn't triggered
        self.on_profile_change(self.current_profile)

    def on_profile_change(self, profile: str) -> None:
        """Handle profile change: update DB, load styles, apply CSS."""
        if profile != self.current_profile:
            self.update_current_profile(profile)

        self.current_profile = profile
        self.load_existing_customizations()
        css = self.generate_custom_css()

        if css and self.parent:
            parent = cast("MainWindowType", self.parent)
            parent.apply_custom_css(css)
            parent.website_frame.reload()

        logging.info(f"Switched to profile: {profile} and applied CSS")

    def load_profiles(self) -> None:
        """Load available CSS profiles from the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT profile_name FROM css_profiles")
                profiles = [row[0] for row in cursor.fetchall()]
            self.profile_dropdown.clear()
            self.profile_dropdown.addItems(profiles)
            logging.debug(f"Loaded {len(profiles)} profiles")
        except sqlite3.Error as e:
            logging.error(f"Failed to load profiles: {e}")
            QMessageBox.critical(self, "Error", "Failed to load profiles")

    def create_new_profile(self) -> None:
        """Create a new CSS profile."""
        profile_name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and profile_name:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR IGNORE INTO css_profiles (profile_name) VALUES (?)", (profile_name,))
                    conn.commit()
                self.load_profiles()
                self.profile_dropdown.setCurrentText(profile_name)
                self.on_profile_change(profile_name)
                logging.info(f"Created new profile: {profile_name}")
            except sqlite3.Error as e:
                logging.error(f"Failed to create profile: {e}")
                QMessageBox.critical(self, "Error", "Failed to create profile")

    def delete_profile(self) -> None:
        """Delete the selected CSS profile."""
        profile = self.profile_dropdown.currentText()
        if profile == "Default":
            QMessageBox.warning(self, "Warning", "Cannot delete the Default profile")
            return
        # noinspection PyUnresolvedReferences
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete profile '{profile}'?", QMessageBox.Yes | QMessageBox.No)
        # noinspection PyUnresolvedReferences
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM css_profiles WHERE profile_name = ?", (profile,))
                    conn.commit()
                self.load_profiles()
                self.profile_dropdown.setCurrentText("Default")
                self.on_profile_change("Default")
                logging.info(f"Deleted profile: {profile}")
            except sqlite3.Error as e:
                logging.error(f"Failed to delete profile: {e}")
                QMessageBox.critical(self, "Error", "Failed to delete profile")

    def add_tab(self, tab_title: str, elements: list[str]) -> None:
        """Add a tab for a category of CSS elements."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)

        grid.addWidget(QLabel("Element"), 0, 0)
        grid.addWidget(QLabel("Preview"), 0, 1)
        grid.addWidget(QLabel("Color"), 0, 2)
        grid.addWidget(QLabel("Image"), 0, 3)
        grid.addWidget(QLabel("Shadow"), 0, 4)
        grid.addWidget(QLabel("Reset"), 0, 5)

        for i, element in enumerate(elements, 1):
            label = QLabel(element)
            preview = QLabel("Preview")
            preview.setFixedSize(100, 30)
            preview.setStyleSheet("border: 1px solid black;")
            color_btn = QPushButton("Pick Color")
            color_btn.clicked.connect(lambda _, e=element, p=preview: self.pick_color(e, p))
            image_btn = QPushButton("Pick Image")
            image_btn.clicked.connect(lambda _, e=element, p=preview: self.pick_image(e, p))
            shadow_btn = QPushButton("Add Shadow")
            shadow_btn.clicked.connect(lambda _, e=element: self.add_shadow(e))
            reset_btn = QPushButton("Reset")
            reset_btn.clicked.connect(lambda _, e=element, p=preview: self.reset_css_item(e, p))
            grid.addWidget(label, i, 0)
            grid.addWidget(preview, i, 1)
            grid.addWidget(color_btn, i, 2)
            grid.addWidget(image_btn, i, 3)
            grid.addWidget(shadow_btn, i, 4)
            grid.addWidget(reset_btn, i, 5)

        scroll.setWidget(container)
        tab.setLayout(QVBoxLayout())
        tab.layout().addWidget(scroll)
        self.tab_widget.addTab(tab, tab_title)
        self.tabs[tab_title] = tab
        tab.grid = grid  # Preserve reference

    def pick_color(self, css_item: str, preview: QLabel) -> None:
        """Open a color picker and apply the selected color."""
        color = QColorDialog.getColor()
        if color.isValid():
            style = f"background-color: {color.name()};"
            preview.setStyleSheet(style)
            self.save_css_item(css_item, style)
            logging.debug(f"Set color for '{css_item}': {color.name()}")

    def pick_image(self, css_item: str, preview: QLabel) -> None:
        """Open a file dialog to select an image and apply it as a background."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            style = f"background-image: url({file_path}); background-size: cover;"
            preview.setStyleSheet(style)
            self.save_css_item(css_item, style)
            logging.debug(f"Set image for '{css_item}': {file_path}")

    def add_shadow(self, css_item: str) -> None:
        """Add a default shadow effect to the element."""
        style = "box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);"
        self.save_css_item(css_item, style)
        self.load_existing_customizations()
        logging.debug(f"Added shadow to '{css_item}'")

    def save_css_item(self, css_item: str, value: str) -> None:
        """Save a CSS customization to the database under the current profile."""
        if not value.strip():
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)",
                    (self.current_profile, css_item, value)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save CSS for '{css_item}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to save CSS: {e}")

    def load_existing_customizations(self) -> None:
        """Load and apply existing CSS customizations for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT element, value FROM custom_css WHERE profile_name = ?",
                    (self.current_profile,)
                )
                customizations = dict(cursor.fetchall())

            for tab in self.tabs.values():
                grid = tab.grid
                for row in range(1, grid.rowCount()):
                    label = grid.itemAtPosition(row, 0).widget()
                    preview = grid.itemAtPosition(row, 1).widget()
                    preview.setStyleSheet(customizations.get(label.text(), ""))
        except sqlite3.Error as e:
            logging.error(f"Failed to load CSS customizations: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load customizations: {e}")

    def save_and_apply_changes(self) -> None:
        selected_profile = self.profile_dropdown.currentText()
        self.update_current_profile(selected_profile)
        self.current_profile = selected_profile
        css = self.generate_custom_css()
        if css and self.parent:
            parent = cast("MainWindowType", self.parent)
            parent.current_css_profile = self.current_profile
            parent.apply_custom_css(css)
            parent.website_frame.reload()
        self.accept()
        logging.info("CSS changes saved and applied")

    def generate_custom_css(self) -> str:
        """Generate CSS string from database customizations for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT element, value FROM custom_css WHERE profile_name = ?",
                    (self.current_profile,)
                )
                return "\n".join(f"{elem} {{ {val} }}" for elem, val in cursor.fetchall())
        except sqlite3.Error as e:
            logging.error(f"Failed to generate CSS: {e}")
            return ""

    def upload_css_file(self) -> None:
        """Upload and apply a CSS file to the current profile."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSS", "", "CSS Files (*.css)")
        if file_path:
            try:
                with open(file_path, "r") as f, sqlite3.connect(DB_PATH) as conn:
                    css = f.read()
                    rules = re.findall(r'([^{]+){([^}]+)}', css, re.DOTALL)
                    cursor = conn.cursor()
                    cursor.executemany(
                        "INSERT OR REPLACE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)",
                        [(self.current_profile, sel.strip(), prop.strip()) for sel, prop in rules]
                    )
                    conn.commit()
                self.load_existing_customizations()
                if self.parent:
                    parent = cast("MainWindowType", self.parent)
                    parent.apply_custom_css(css)
                    parent.website_frame.reload()
                logging.info(f"Uploaded CSS file: {file_path} to profile '{self.current_profile}'")
            except (IOError, sqlite3.Error) as e:
                logging.error(f"Failed to upload CSS file: {e}")
                QMessageBox.critical(self, "Error", f"Upload failed: {e}")

    def reset_css_item(self, css_item: str, preview: QLabel) -> None:
        """Reset a specific CSS item to default for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM custom_css WHERE profile_name = ? AND element = ?",
                    (self.current_profile, css_item)
                )
                conn.commit()
            preview.setStyleSheet("")
            logging.debug(f"Reset CSS for '{css_item}' in profile '{self.current_profile}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to reset CSS for '{css_item}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to reset CSS: {e}")

    def clear_all_customizations(self) -> None:
        """Clear all CSS customizations for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_css WHERE profile_name = ?", (self.current_profile,))
                conn.commit()
            self.load_existing_customizations()
            if self.parent:
                parent = cast("MainWindowType", self.parent)
                parent.apply_custom_css("")
                parent.website_frame.reload()
            logging.info(f"Cleared all CSS customizations for profile '{self.current_profile}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to clear CSS customizations: {e}")
            QMessageBox.critical(self, "Error", "Failed to clear customizations")

# -----------------------
# AVITD Scraper Class
# -----------------------

class AVITDScraper:
    """
    A scraper class for 'A View in the Dark' to update guilds and shops data in the SQLite database.
    """

    def __init__(self):
        """
        Initialize the scraper with the required headers and database connection.
        """
        self.url = "https://aviewinthedark.net/"
        self.connection = sqlite3.connect(DB_PATH)  # SQLite connection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("AVITDScraper initialized.")

    def scrape_guilds_and_shops(self):
        """
        Scrape the guilds and shops data from the website and update the SQLite database.
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

        # Update the SQLite database with scraped data
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

        # Find all divs with the 'next_change' class
        section_divs = soup.find_all('div', class_='next_change')

        # Iterate through the divs to find the matching section
        for div in section_divs:
            if section_name in div.text:
                # Search for the time pattern
                match = re.search(r'(\d+)\s+days?,\s+(\d+)h\s+(\d+)m\s+(\d+)s', div.text)
                if match:
                    # Parse time components
                    days = int(match.group(1))
                    hours = int(match.group(2))
                    minutes = int(match.group(3))
                    seconds = int(match.group(4))

                    # Calculate the next update time
                    next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                    logging.debug(f"Next update time for {section_name}: {next_update}")

                    # Return the formatted date-time string
                    return next_update.strftime('%Y-%m-%d %H:%M:%S')

        # Return 'NA' if no match is found
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
        Thread-safe update for the SQLite database.

        Args:
            data (list): List of tuples containing (name, col, row) entries.
            table (str): 'guilds' or 'shops'.
            next_update (str): Timestamp for next update.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Step 1: Set all entries to 'NA', conditionally
                logging.debug(f"Setting all {table} entries' Row and Column to 'NA'...")
                if table == "guilds":
                    cursor.execute(f"""
                        UPDATE {table}
                        SET `Column`='NA', `Row`='NA', `next_update`=?
                        WHERE Name NOT LIKE 'Peacekeepers Mission%'
                    """, (next_update,))
                else:
                    cursor.execute(f"""
                        UPDATE {table}
                        SET `Column`='NA', `Row`='NA', `next_update`=?
                    """, (next_update,))

                # Step 2: Insert or update scraped entries
                for name, column, row in data:
                    if table == "shops" and "Peacekeepers Mission" in name:
                        logging.warning(f"Skipping {name} as it belongs in guilds, not shops.")
                        continue

                    try:
                        cursor.execute(f"""
                            INSERT INTO {table} (Name, `Column`, `Row`, `next_update`)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(Name) DO UPDATE SET
                                `Column`=excluded.`Column`,
                                `Row`=excluded.`Row`,
                                `next_update`=excluded.`next_update`
                        """, (name, column, row, next_update))
                    except sqlite3.Error as e:
                        logging.error(f"Failed to update {table} entry '{name}': {e}")

                # Step 3: Always persist Peacekeeper's Missions in guilds
                if table == "guilds":
                    logging.debug("Ensuring Peacekeeper's Mission locations persist in guilds.")
                    cursor.executemany(f"""
                        INSERT INTO {table} (Name, `Column`, `Row`, `next_update`)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(Name) DO UPDATE SET
                            `Column`=excluded.`Column`,
                            `Row`=excluded.`Row`,
                            `next_update`=excluded.`next_update`
                    """, [
                        ("Peacekeepers Mission 1", "Emerald", "67th", next_update),
                        ("Peacekeepers Mission 2", "Unicorn", "33rd", next_update),
                        ("Peacekeepers Mission 3", "Emerald", "33rd", next_update),
                    ])

                conn.commit()
                logging.info(f"Database updated for {table}.")

        except sqlite3.Error as e:
            logging.error(f"Database operation for {table} failed: {e}")

    def close_connection(self):
        """
        Close the SQLite database connection.
        """
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")

# -----------------------
# Set Destination Dialog
# -----------------------

class SetDestinationDialog(QDialog):
    """Dialog for setting a destination on the map."""

    def __init__(self, parent: QWidget = None) -> None:
        """
        Initialize the Set Destination dialog.

        Args:
            parent: Reference to RBCCommunityMap.
        """
        super().__init__(parent)
        self.setWindowTitle("Set Destination")
        self.setWindowIcon(APP_ICON)
        self.resize(650, 300)
        self.parent = parent
        logging.debug("SetDestinationDialog initialized")

        main_layout = QVBoxLayout(self)
        dropdown_style = "QComboBox { border: 2px solid #5F6368; padding: 5px; border-radius: 4px; }"

        # Create all dropdowns
        self.recent_destinations_dropdown = QComboBox()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()
        self.columns_dropdown = QComboBox()
        self.rows_dropdown = QComboBox()
        self.directional_dropdown = QComboBox()

        # Apply style and search to all dropdowns
        all_dropdowns = [
            self.recent_destinations_dropdown,
            self.tavern_dropdown, self.bank_dropdown, self.transit_dropdown,
            self.shop_dropdown, self.guild_dropdown, self.poi_dropdown,
            self.user_building_dropdown,
            self.columns_dropdown, self.rows_dropdown, self.directional_dropdown,
        ]

        for dropdown in all_dropdowns:
            dropdown.setStyleSheet(dropdown_style)
            dropdown.setEditable(True)
            # noinspection PyUnresolvedReferences
            dropdown.setInsertPolicy(QComboBox.NoInsert)
            completer = dropdown.completer()
            # noinspection PyUnresolvedReferences
            completer.setCompletionMode(QCompleter.PopupCompletion)
            # noinspection PyUnresolvedReferences
            completer.setFilterMode(Qt.MatchContains)

        # Populate dropdowns
        self.populate_recent_destinations()
        self._populate_initial_dropdowns()

        if self.parent:
            parent = cast("MainWindowType", self.parent)
            self.populate_dropdown(self.columns_dropdown, list(parent.columns.keys()))
            self.populate_dropdown(self.rows_dropdown, list(parent.rows.keys()))
        else:
            self.populate_dropdown(self.columns_dropdown, [])
            self.populate_dropdown(self.rows_dropdown, [])

        self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "South East"])

        # Layout: Predefined dropdowns
        dropdown_layout = QFormLayout()
        dropdown_layout.addRow("Recent:", self.recent_destinations_dropdown)
        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

        # Layout: Custom XY + direction
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("ABC Street:"))
        custom_layout.addWidget(self.columns_dropdown, 1)
        custom_layout.addWidget(QLabel("123 Street:"))
        custom_layout.addWidget(self.rows_dropdown, 1)
        custom_layout.addWidget(QLabel("Direction:"))
        custom_layout.addWidget(self.directional_dropdown, 1)

        self.columns_dropdown.setMinimumWidth(120)
        self.rows_dropdown.setMinimumWidth(120)
        self.directional_dropdown.setMinimumWidth(120)

        # Layout: Buttons
        button_layout = QGridLayout()
        set_btn = QPushButton("Set")
        set_btn.clicked.connect(lambda: self.set_destination())
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_destination)
        update_btn = QPushButton("Update Data")
        update_btn.clicked.connect(self.update_combo_boxes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(set_btn, 0, 0)
        button_layout.addWidget(clear_btn, 0, 1)
        button_layout.addWidget(update_btn, 1, 0)
        button_layout.addWidget(cancel_btn, 1, 1)

        # Final layout
        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(custom_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _populate_initial_dropdowns(self) -> None:
        """Populate predefined destination dropdowns with initial data."""
        if not self.parent:
            logging.warning("No parent; skipping dropdown population")
            return

        parent = cast("MainWindowType", self.parent)

        self.populate_dropdown(self.tavern_dropdown, list(parent.taverns_coordinates.keys()))
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for col, row, *_ in parent.banks_coordinates.values()])
        self.populate_dropdown(self.transit_dropdown, list(parent.transits_coordinates.keys()))
        self.populate_dropdown(self.shop_dropdown, list(parent.shops_coordinates.keys()))
        self.populate_dropdown(self.guild_dropdown, list(parent.guilds_coordinates.keys()))
        self.populate_dropdown(self.poi_dropdown, list(parent.places_of_interest_coordinates.keys()))
        self.populate_dropdown(self.user_building_dropdown, list(parent.user_buildings_coordinates.keys()))

        logging.debug("Initial dropdowns populated")

    def populate_recent_destinations(self) -> None:
        """Populate recent destinations dropdown for the selected character."""
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem("Select a recent destination")

        if not self.parent:
            logging.debug("No parent; skipping recent destinations")
            return

        parent = cast("MainWindowType", self.parent)

        if not parent.selected_character:
            logging.debug("No character selected; skipping recent destinations")
            return

        character_id = parent.selected_character.get('id')

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT col, row FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10",
                    (character_id,)
                )

                # Create inverse mappings (coord → name)
                inverse_columns = {v: k for k, v in parent.columns.items()}
                inverse_rows = {v: k for k, v in parent.rows.items()}

                for col, row in cursor.fetchall():
                    # Round down to nearest even coordinate for label mapping
                    even_col = col - (col % 2)
                    even_row = row - (row % 2)

                    col_name = inverse_columns.get(even_col, f"Column {even_col}")
                    row_name = inverse_rows.get(even_row, f"Row {even_row}")
                    building_name = self._get_building_name(cursor, col_name, row_name)

                    display = f"{col_name} & {row_name}" + (f" - {building_name}" if building_name else "")
                    self.recent_destinations_dropdown.addItem(display, (col, row))

                logging.debug(f"Loaded {self.recent_destinations_dropdown.count() - 1} recent destinations")

        except sqlite3.Error as e:
            logging.error(f"Failed to load recent destinations: {e}")

    def _get_building_name(self, cursor: sqlite3.Cursor, col: str, row: str) -> str | None:
        """Get building name at given coordinates."""
        tables = ["banks", "guilds", "placesofinterest", "shops", "taverns", "transits", "userbuildings"]
        for table in tables:
            cursor.execute(f"SELECT Name FROM `{table}` WHERE `Column` = ? AND `Row` = ?", (col, row))
            if result := cursor.fetchone():
                return result[0]
        return None

    def populate_dropdown(self, dropdown: QComboBox, items: list | KeysView) -> None:
        """Populate a dropdown with items."""
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems([str(item) for item in items])
        logging.debug(f"Populated dropdown with {len(items)} items")

    def update_combo_boxes(self):
        logging.info("Updating combo boxes.")
        self.show_notification("Updating Shop and Guild Data. Please wait...")

        try:
            if not self.parent:
                logging.warning("No parent found; cannot update combo boxes.")
                return

            parent = cast("MainWindowType", self.parent)

            # Run scraper to update shops and guilds
            parent.AVITD_scraper.scrape_guilds_and_shops()

            # Update only shops and guilds coordinates from database
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Fetch columns and rows for coordinate conversion
                cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
                columns = {row[0]: row[1] for row in cursor.fetchall()}
                cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
                rows = {row[0]: row[1] for row in cursor.fetchall()}

                def to_coords(col_name: str, row_name: str) -> tuple[int, int]:
                    return (columns.get(col_name, 0) + 1, rows.get(row_name, 0) + 1)

                # Update shops_coordinates
                cursor.execute("SELECT Name, `Column`, `Row` FROM shops")
                parent.shops_coordinates = {
                    name: to_coords(col, row)
                    for name, col, row in cursor.fetchall()
                    if col != "NA" and row != "NA"
                }

                # Update guilds_coordinates
                cursor.execute("SELECT Name, `Column`, `Row` FROM guilds")
                parent.guilds_coordinates = {
                    name: to_coords(col, row)
                    for name, col, row in cursor.fetchall()
                    if col != "NA" and row != "NA"
                }

            # Populate dropdowns
            self.populate_dropdown(self.tavern_dropdown, parent.taverns_coordinates.keys())
            self.populate_dropdown(self.bank_dropdown, parent.banks_coordinates.keys())
            self.populate_dropdown(self.transit_dropdown, parent.transits_coordinates.keys())
            self.populate_dropdown(self.shop_dropdown, parent.shops_coordinates.keys())
            self.populate_dropdown(self.guild_dropdown, parent.guilds_coordinates.keys())
            self.populate_dropdown(self.poi_dropdown, parent.places_of_interest_coordinates.keys())
            self.populate_dropdown(self.user_building_dropdown, parent.user_buildings_coordinates.keys())

            parent.update_minimap()
            logging.info("Combo boxes updated successfully.")

        except Exception as e:
            logging.error(f"Failed to update Combo boxes: {e}")
            self.show_error_dialog("Update Failed", str(e))

    def show_notification(self, message: str) -> None:
        """Show a temporary notification."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Notification")
        # noinspection PyUnresolvedReferences
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        dialog.setFixedSize(300, 100)
        QTimer.singleShot(5000, dialog.accept)
        dialog.exec()
        logging.debug(f"Notification shown: {message}")

    def clear_destination(self) -> None:
        """Clear the current destination for the selected character."""
        if not self.parent:
            logging.warning("No parent found; cannot clear destination.")
            return

        parent = cast("MainWindowType", self.parent)

        if not parent.selected_character:
            logging.warning("No character selected to clear destination")
            return

        character_id = parent.selected_character['id']

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM destinations WHERE character_id = ?", (character_id,))
                conn.commit()

            parent.destination = None
            parent.update_minimap()
            logging.info(f"Cleared destination for character {character_id}")
            self.accept()

        except sqlite3.Error as e:
            logging.error(f"Failed to clear destination: {e}")

    def set_destination(self) -> None:
        """Set the selected destination for the current character."""
        if not self.parent:
            self.show_error_dialog("No Character", "Please select a character first")
            return

        parent = cast("MainWindowType", self.parent)
        parent.selected_route_label = None

        if not parent.selected_character:
            self.show_error_dialog("No Character", "Please select a character first")
            return

        coords = self.get_selected_destination()
        if not coords:
            self.show_error_dialog("No Destination", "Please select a valid destination")
            return

        character_id = parent.selected_character['id']

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                """, (character_id, coords[0], coords[1]))

                conn.commit()

            # ✅ Save to recent using centralized logic
            parent.save_to_recent_destinations(character_id, coords[0], coords[1])

            # ✅ Reload destination from DB to sync to current character context
            parent.load_last_destination_for_character(character_id)
            parent.update_minimap()
            logging.info(f"Set destination for character {character_id} to {coords}")
            self.accept()

        except sqlite3.Error as e:
            logging.error(f"Failed to set destination: {e}")

    def get_selected_destination(self) -> tuple[int, int] | None:
        """Retrieve coordinates of the selected destination."""
        if not self.parent:
            return None

        parent = cast("MainWindowType", self.parent)

        if (recent := self.recent_destinations_dropdown.currentText()) != "Select a recent destination":
            return self.recent_destinations_dropdown.currentData()

        dropdowns = [
            (self.tavern_dropdown, parent.taverns_coordinates),
            (self.transit_dropdown, parent.transits_coordinates),
            (self.shop_dropdown, parent.shops_coordinates),
            (self.guild_dropdown, parent.guilds_coordinates),
            (self.poi_dropdown, parent.places_of_interest_coordinates),
            (self.user_building_dropdown, parent.user_buildings_coordinates),
        ]
        for dropdown, data in dropdowns:
            if (sel := dropdown.currentText()) != "Select a destination":
                return data[sel]

        if (bank := self.bank_dropdown.currentText()) != "Select a destination":
            col_name, row_name = bank.split(" & ")
            col = parent.columns.get(col_name.strip())
            row = parent.rows.get(row_name.strip())
            if col is not None and row is not None:
                return col + 1, row + 1

        col = parent.columns.get(self.columns_dropdown.currentText())
        row = parent.rows.get(self.rows_dropdown.currentText())
        if col is not None and row is not None:
            return col, row

        logging.debug("No valid destination selected")
        return None

    def set_external_destination(self, col: int, row: int, guild_name: str) -> None:
        """Set a destination externally."""
        self.parent().selected_route_label = None
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem(f"{guild_name} - {col}, {row}", (col, row))
        self.recent_destinations_dropdown.setCurrentIndex(0)  # Select the added item
        self.set_destination()
        logging.info(f"External destination set: {guild_name} at ({col}, {row})")

    def show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        # noinspection PyUnresolvedReferences
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setFixedSize(300, 100)
        dialog.exec()
        logging.debug(f"Error dialog shown: {title} - {message}")

# -----------------------
# Shopping List Tools
# -----------------------

class ShoppingListTool(QDialog):
    """Tool for managing a character’s shopping list with SQLite-backed shop data."""

    def __init__(self, character_name: str, db_path: str, parent=None) -> None:
        """
        Initialize the Shopping List Tool.

        Args:
            character_name: Name of the character using the tool.
            db_path: Path to the SQLite database.
            parent: Parent widget (default is None).
        """
        super().__init__(parent)  # Ensure it gets QDialog properties
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)
        self.character_name = character_name
        self.DB_PATH = db_path
        self.list_total = 0

        try:
            self.sqlite_connection = sqlite3.connect(self.DB_PATH)
            self.sqlite_cursor = self.sqlite_connection.cursor()
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            self.sqlite_connection = None
            self.sqlite_cursor = None

        self.setup_ui()
        if self.sqlite_connection:
            self.populate_shop_dropdown()
        logging.debug(f"ShoppingListTool initialized for {character_name}")

    def setup_ui(self) -> None:
        """Set up the UI elements and layout."""
        layout = QVBoxLayout(self)  # Use QVBoxLayout for QDialog

        self.shop_combobox = QComboBox()
        self.charisma_combobox = QComboBox()
        self.charisma_combobox.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        self.available_items_list = QListWidget()
        self.shopping_list = QListWidget()
        self.add_item_button = QPushButton("Add Item")
        self.remove_item_button = QPushButton("Remove Item")
        self.total_label = QLabel(f"List total: 0 Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}")

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
        layout.addWidget(self.total_label)

        self.setLayout(layout)  # Set the layout for QDialog

        # Signal connections
        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self._update_all)

    def populate_shop_dropdown(self) -> None:
        """Populate the shop dropdown with data from SQLite."""
        if not self.sqlite_cursor:
            return
        try:
            self.sqlite_cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
            shops = [row[0] for row in self.sqlite_cursor.fetchall()]
            self.shop_combobox.addItems(shops)
            logging.debug(f"Populated shop dropdown with {len(shops)} shops")
        except sqlite3.Error as e:
            logging.error(f"Failed to populate shop dropdown: {e}")

    def load_items(self) -> None:
        """Load available items based on selected shop and charisma level."""
        if not self.sqlite_cursor or not self.shop_combobox.currentText():
            self.available_items_list.clear()
            return

        self.available_items_list.clear()
        shop_name = self.shop_combobox.currentText()
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(self.charisma_combobox.currentText(), "base_price")

        try:
            self.sqlite_cursor.execute(
                f"SELECT item_name, {price_column} FROM shop_items WHERE shop_name = ?",
                (shop_name,)
            )
            for name, price in self.sqlite_cursor.fetchall():
                self.available_items_list.addItem(f"{name} - {price} Coins")
            logging.debug(f"Loaded {self.available_items_list.count()} items for {shop_name}")
        except sqlite3.Error as e:
            logging.error(f"Failed to load items: {e}")

    def add_item(self) -> None:
        """Add an item from available items to the shopping list."""
        if not (item := self.available_items_list.currentItem()):
            return

        name, price_str = item.text().split(" - ")
        price = int(price_str.split(" Coins")[0])
        quantity, ok = QInputDialog.getInt(self, "Quantity", f"How many {name}?", 1, 1)
        if not ok:
            return

        for i in range(self.shopping_list.count()):
            if (existing := self.shopping_list.item(i).text()).startswith(f"{name} - "):
                curr_qty = int(existing.split(" - ")[2].split("x")[0])
                self.shopping_list.item(i).setText(f"{name} - {price} Coins - {curr_qty + quantity}x")
                self.update_total()
                return

        self.shopping_list.addItem(f"{name} - {price} Coins - {quantity}x")
        self.update_total()
        logging.debug(f"Added {name} x{quantity} to shopping list")

    def remove_item(self) -> None:
        """Remove or reduce quantity of an item from the shopping list."""
        if not (item := self.shopping_list.currentItem()):
            return

        name, price_str, qty_str = item.text().split(" - ")
        price = int(price_str.split(" Coins")[0])
        curr_qty = int(qty_str.split("x")[0])
        qty_to_remove, ok = QInputDialog.getInt(self, "Remove", f"How many {name}?", 1, 1, curr_qty)
        if not ok:
            return

        new_qty = curr_qty - qty_to_remove
        if new_qty > 0:
            item.setText(f"{name} - {price} Coins - {new_qty}x")
        else:
            self.shopping_list.takeItem(self.shopping_list.row(item))
        self.update_total()
        logging.debug(f"Removed {qty_to_remove}x {name} from shopping list")

    def _update_all(self) -> None:
        """Update both available items and shopping list prices."""
        self.load_items()
        self.update_shopping_list_prices()

    def update_shopping_list_prices(self) -> None:
        """Update prices in the shopping list based on charisma level."""
        if not self.sqlite_cursor or not self.shop_combobox.currentText():
            return

        shop_name = self.shop_combobox.currentText()
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(self.charisma_combobox.currentText(), "base_price")

        try:
            items = {self.shopping_list.item(i).text().split(" - ")[0]: i for i in range(self.shopping_list.count())}
            if items:
                self.sqlite_cursor.execute(
                    f"SELECT item_name, {price_column} FROM shop_items WHERE shop_name = ? AND item_name IN ({','.join('?' * len(items))})",
                    (shop_name, *items.keys())
                )
                for name, price in self.sqlite_cursor.fetchall():
                    i = items[name]
                    qty = int(self.shopping_list.item(i).text().split(" - ")[2].split("x")[0])
                    self.shopping_list.item(i).setText(f"{name} - {price} Coins - {qty}x")
            self.update_total()
            logging.debug(f"Updated prices for {len(items)} shopping list items")
        except sqlite3.Error as e:
            logging.error(f"Failed to update shopping list prices: {e}")

    def update_total(self) -> None:
        """Update and display the total cost of the shopping list."""
        self.list_total = sum(
            int(item.text().split(" - ")[1].split(" Coins")[0]) * int(item.text().split(" - ")[2].split("x")[0])
            for item in [self.shopping_list.item(i) for i in range(self.shopping_list.count())]
        )
        self.total_label.setText(
            f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}"
        )

    def coins_in_pocket(self) -> int:
        """Retrieve coins in pocket for the character."""
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute("SELECT pocket FROM coins WHERE character_id = (SELECT id FROM characters WHERE name = ?)",
                                     (self.character_name,))
            result = self.sqlite_cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch pocket coins: {e}")
            return 0

    def coins_in_bank(self) -> int:
        """Retrieve coins in bank for the character."""
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute("SELECT bank FROM coins WHERE character_id = (SELECT id FROM characters WHERE name = ?)",
                                     (self.character_name,))
            result = self.sqlite_cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch bank coins: {e}")
            return 0

    def closeEvent(self, event) -> None:
        """Close the SQLite connection when the window closes."""
        if self.sqlite_connection:
            try:
                self.sqlite_connection.close()
                logging.debug("SQLite connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close connection: {e}")
        event.accept()

# -----------------------
# Damage Calculator Tool
# -----------------------

class DamageCalculator(QDialog):
    """Dialog for calculating weapons needed to reduce a target BP."""

    def __init__(self, db_connection: sqlite3.Connection, parent=None) -> None:
        """
        Initialize the Damage Calculator.

        Args:
            db_connection: SQLite database connection (unused currently).
            parent: Parent widget (default is None).
        """
        super().__init__(parent)  # Ensure it gets QDialog properties
        self.db_connection = db_connection
        self.charisma_level = 0
        self.setWindowTitle("Damage Calculator")
        self.setWindowIcon(APP_ICON)
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)  # Use QVBoxLayout for QDialog

        # Target BP
        bp_layout = QHBoxLayout()
        bp_layout.addWidget(QLabel("Target BP:"))
        self.bp_input = QLineEdit()
        self.bp_input.setValidator(QIntValidator(0, 100000000))
        bp_layout.addWidget(self.bp_input)
        main_layout.addLayout(bp_layout)

        # Charisma level
        charisma_layout = QHBoxLayout()
        charisma_layout.addWidget(QLabel("Charisma Level:"))
        self.charisma_dropdown = QComboBox()
        self.charisma_dropdown.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        self.charisma_dropdown.currentIndexChanged.connect(self.update_charisma_level)
        charisma_layout.addWidget(self.charisma_dropdown)
        main_layout.addLayout(charisma_layout)

        # Results
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("Weapons needed will be displayed here.")
        main_layout.addWidget(self.result_display)

        self.total_cost_label = QLabel("Total Cost: 0 Coins")
        main_layout.addWidget(self.total_cost_label)

        # Calculate button
        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_damage)
        main_layout.addWidget(calc_button)

        self.setLayout(main_layout)  # Set the layout for QDialog

        # Static prices [No Charisma, Charisma 1, Charisma 2, Charisma 3]
        self.discount_magic_prices = {
            "Vial of Holy Water": [1400, 1357, 1302, 1260],
            "Garlic Spray": [700, 678, 651, 630],
            "Wooden Stake": [2800, 2715, 2604, 2520],
        }
        logging.debug("DamageCalculator initialized")

    def update_charisma_level(self) -> None:
        """Update charisma level based on dropdown selection."""
        self.charisma_level = self.charisma_dropdown.currentIndex()
        logging.debug(f"Charisma level set to {self.charisma_level}")

    def calculate_damage(self) -> None:
        """Calculate weapons needed to reduce target BP to 0."""
        self.result_display.clear()
        try:
            target_bp = int(self.bp_input.text())
            if target_bp <= 0:
                raise ValueError("BP must be positive")
        except ValueError:
            self.result_display.setText("Please enter a valid positive BP value")
            logging.warning("Invalid BP input")
            return

        vial_cost = self.discount_magic_prices["Vial of Holy Water"][self.charisma_level]
        spray_cost = self.discount_magic_prices["Garlic Spray"][self.charisma_level]
        stake_cost = self.discount_magic_prices["Wooden Stake"][self.charisma_level]

        remaining_bp = target_bp
        total_cost = 0
        total_hits = 0
        results = []

        # Vials until BP <= 1350
        vial_hits = 0
        while remaining_bp > 1350:
            damage = math.floor(remaining_bp * 0.6)
            remaining_bp -= damage
            vial_hits += 1
            total_cost += vial_cost
            total_hits += 1
        if vial_hits:
            results.append(f"Discount Magic - Vial of Holy Water - Qty: {vial_hits} - Total Cost: {vial_hits * vial_cost:,} coins")

        # Sprays until BP <= 200
        spray_hits = 0
        while remaining_bp > 200:
            remaining_bp -= 75
            spray_hits += 1
            total_cost += spray_cost
            total_hits += 1
        if spray_hits:
            results.append(f"Discount Magic - Garlic Spray - Qty: {spray_hits} - Total Cost: {spray_hits * spray_cost:,} coins")

        # Stake if BP <= 200
        if 0 < remaining_bp <= 200:
            total_cost += stake_cost
            total_hits += 1
            results.append(f"Discount Magic - Wooden Stake - Qty: 1 - Total Cost: {stake_cost:,} coins")
            remaining_bp = 0

        # Summary
        results.append(f"Totals: Hits: {total_hits} Coins: {total_cost:,}")
        self.result_display.setText("\n".join(results))
        self.total_cost_label.setText(f"Total Cost: {total_cost:,} Coins")
        logging.debug(f"Calculated for BP {target_bp}: {total_hits} hits, {total_cost} coins")

# -----------------------
# Powers Reference Tool
# -----------------------

class PowersDialog(QDialog):
    """Dialog displaying power information with destination-setting functionality."""

    def __init__(self, parent: QWidget, character_x: int, character_y: int, db_path: str) -> None:
        """
        Initialize the PowersDialog.

        Args:
            parent: Reference to RBCCommunityMap.
            character_x: Character's X coordinate.
            character_y: Character's Y coordinate.
            db_path: Path to SQLite database.
        """
        super().__init__(parent)  # Ensure QDialog properties are inherited
        self.setWindowTitle("Powers Information")
        self.setWindowIcon(APP_ICON)
        self.setMinimumSize(600, 400)
        self.parent = parent
        self.character_x = character_x
        self.character_y = character_y
        self.DB_PATH = db_path

        try:
            self.db_connection = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            self.db_connection = None

        # Main layout
        main_layout = QHBoxLayout(self)

        # Powers List
        self.powers_list = QListWidget()
        self.powers_list.itemClicked.connect(self.load_power_info)
        main_layout.addWidget(self.powers_list)

        # Details Panel
        self.details_panel = QVBoxLayout()
        self.power_name_label: QLabel = self._create_labeled_field("Power")
        self.guild_label: QLabel = self._create_labeled_field("Guild")
        self.cost_label: QLabel = self._create_labeled_field("Cost")
        self.quest_info_text: QTextEdit = self._create_labeled_field("Quest Info", QTextEdit)
        self.skill_info_text: QTextEdit = self._create_labeled_field("Skill Info", QTextEdit)

        self.set_destination_button = QPushButton("Set Destination")
        self.set_destination_button.setEnabled(False)
        self.set_destination_button.clicked.connect(self.set_destination)
        self.details_panel.addWidget(self.set_destination_button)

        main_layout.addLayout(self.details_panel)

        # Load powers if DB is available
        if self.db_connection:
            self.load_powers()

        self.setLayout(main_layout)  # Set QDialog layout
        logging.debug(f"PowersDialog initialized at ({character_x}, {character_y})")

    T = TypeVar("T", QLabel, QTextEdit)

    def _create_labeled_field(self, label_text: str, widget_type: Type[T] = QLabel) -> T:
        """Create a labeled field with a widget."""
        label = QLabel(f"<b>{label_text}:</b>", self)
        widget = widget_type(self)
        if isinstance(widget, QTextEdit):
            widget.setReadOnly(True)
        self.details_panel.addWidget(label)
        self.details_panel.addWidget(widget)
        return widget

    def load_powers(self) -> None:
        """Load powers from the database into the list."""
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT name FROM powers ORDER BY name ASC")
                for name, in cursor.fetchall():
                    self.powers_list.addItem(name)
            logging.debug(f"Loaded {self.powers_list.count()} powers")
        except sqlite3.Error as e:
            logging.error(f"Failed to load powers: {e}")
            QMessageBox.critical(self, "Database Error", "Failed to load powers")

    def load_power_info(self, item: QListWidgetItem) -> None:
        """Display details for the selected power."""
        power_name = item.text()
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT name, guild, cost, quest_info, skill_info FROM powers WHERE name = ?",
                    (power_name,)
                )
                details = cursor.fetchone()
                if not details:
                    raise ValueError(f"No details for {power_name}")

                name, guild, cost, quest_info, skill_info = details
                self.power_name_label.setText(f"<b>Power:</b> {name}")
                self.guild_label.setText(f"<b>Guild:</b> {guild or 'Unknown'}")
                self.cost_label.setText(f"<b>Cost:</b> {cost or 'Unknown'} coins")
                self.quest_info_text.setPlainText(quest_info or "None")
                self.skill_info_text.setPlainText(skill_info or "None")

                if power_name == "Battle Cloak":
                    self._enable_nearest_peacekeeper_mission()
                elif guild:
                    cursor.execute("""
                        SELECT c.Coordinate, r.Coordinate
                        FROM guilds g
                        JOIN columns c ON g.Column = c.Name
                        JOIN rows r ON g.Row = r.Name
                        WHERE g.Name = ?
                    """, (guild,))
                    if loc := cursor.fetchone():
                        self._configure_destination_button(guild, loc[0], loc[1])

                    else:
                        self.set_destination_button.setEnabled(False)
                else:
                    self.set_destination_button.setEnabled(False)
            logging.debug(f"Loaded info for {power_name}")
        except (sqlite3.Error, ValueError) as e:
            logging.error(f"Failed to load power info for {power_name}: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load details for '{power_name}'")

    def _enable_nearest_peacekeeper_mission(self) -> None:
        """Enable destination button with the nearest Peacekeeper's Mission."""
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT c.`Coordinate`, r.`Coordinate` FROM `columns` c JOIN `rows` r "
                    "WHERE (c.`Name` = 'Emerald' AND r.`Name` IN ('67th', '33rd')) "
                    "OR (c.`Name` = 'Unicorn' AND r.`Name` = '33rd')"
                )
                missions = cursor.fetchall()
            if missions:
                closest = min(missions, key=lambda m: max(abs(m[0] - self.character_x), abs(m[1] - self.character_y)))
                self._configure_destination_button("Peacekeeper's Mission", closest[0], closest[1])
            else:
                self.set_destination_button.setEnabled(False)
                logging.debug("No Peacekeeper's Missions found")
        except sqlite3.Error as e:
            logging.error(f"Failed to find Peacekeeper's Mission: {e}")

    def _configure_destination_button(self, guild: str, col: str | int | None, row: str | int | None) -> None:
        """Configure the destination button with guild location."""
        try:
            col_val = int(col) if col not in ("NA", None) else None
            row_val = int(row) if row not in ("NA", None) else None
        except (ValueError, TypeError):
            logging.warning(f"Invalid col/row for destination: col={col}, row={row}")
            self.set_destination_button.setEnabled(False)
            return

        enabled = col_val is not None and row_val is not None
        self.set_destination_button.setEnabled(enabled)
        if enabled:
            self.set_destination_button.setProperty("guild", guild)
            self.set_destination_button.setProperty("Column", col_val)
            self.set_destination_button.setProperty("Row", row_val)

        logging.debug(f"Destination button {'enabled' if enabled else 'disabled'} for {guild} at ({col}, {row})")

    def set_destination(self) -> None:
        """Set the destination in the database and update the minimap."""
        guild = self.set_destination_button.property("guild")
        col = self.set_destination_button.property("Column")
        row = self.set_destination_button.property("Row")

        if not self.parent:
            logging.warning("No parent window set; cannot update destination.")
            return

        parent = cast("MainWindowType", self.parent)

        if not guild or not parent.selected_character:
            logging.warning("Missing guild or character for destination")
            QMessageBox.warning(self, "Error", "No character selected or invalid guild")
            return

        character_id = parent.selected_character['id']
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp) "
                    "VALUES (?, ?, ?, datetime('now'))",
                    (character_id, col, row)
                )
                conn.commit()
            parent.destination = (col, row)
            parent.update_minimap()
            logging.info(f"Destination set for {character_id} to {guild} at ({col}, {row})")
            # noinspection PyUnresolvedReferences
            QMessageBox.information(self, "Success", f"Destination set to {guild} at ({col}, {row})", QMessageBox.Ok)


        except sqlite3.Error as e:
            logging.error(f"Failed to set destination: {e}")
            QMessageBox.critical(self, "Database Error", "Failed to set destination")

    def closeEvent(self, event) -> None:
        """Close the database connection on dialog close."""
        if self.db_connection:
            try:
                self.db_connection.close()
                logging.debug("Database connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close database: {e}")
        event.accept()

# -----------------------
# Log Viewer
# -----------------------

class LogViewer(QDialog):
    """A dialog window to view and optionally send application logs."""

    def __init__(self, parent: QWidget, log_directory: str):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setWindowIcon(APP_ICON)
        self.resize(900, 600)

        self.log_directory = LOG_DIR
        self.current_log_lines = []

        # Layouts
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # File List
        self.log_list = QListWidget()
        self.log_list.itemClicked.connect(self.load_log)
        left_layout.addWidget(QLabel("Available Logs"))
        left_layout.addWidget(self.log_list)

        # Populate Log Files
        for file in sorted(os.listdir(log_directory), reverse=True):
            if file.endswith(".log"):
                self.log_list.addItem(file)

        # Log Viewer Text Area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # Filter checkboxes
        self.levels = {
            "DEBUG": QCheckBox("DEBUG"),
            "INFO": QCheckBox("INFO"),
            "WARNING": QCheckBox("WARNING"),
            "ERROR": QCheckBox("ERROR"),
            "CRITICAL": QCheckBox("CRITICAL")
        }
        for cb in self.levels.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.apply_filter)

        filter_box = QGroupBox("Log Level Filters")
        filter_layout = QHBoxLayout()
        for cb in self.levels.values():
            filter_layout.addWidget(cb)
        filter_box.setLayout(filter_layout)

        # Buttons
        # Buttons
        delete_button = QPushButton("Delete Log")
        delete_button.clicked.connect(self.delete_log)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)

        # Assemble Right Layout
        right_layout.addWidget(QLabel("Log Contents"))
        right_layout.addWidget(self.log_text)
        right_layout.addWidget(filter_box)
        right_layout.addLayout(button_layout)

        # Final Layout
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 5)

    def load_log(self, item: QListWidgetItem):
        file_path = os.path.join(self.log_directory, item.text())
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_log_lines = f.readlines()
            self.apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def apply_filter(self):
        enabled_levels = [level for level, cb in self.levels.items() if cb.isChecked()]
        filtered = [
            line for line in self.current_log_lines
            if any(level in line for level in enabled_levels)
        ]
        self.log_text.setPlainText("".join(filtered))

    def delete_log(self):
        selected_item = self.log_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No File Selected", "Please select a log file first.")
            return

        filename = selected_item.text()
        file_path = os.path.join(self.log_directory, filename)

        confirm = QMessageBox.warning(
            self, "WARNING!",
            "Are you sure you want to delete this log file?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            os.remove(file_path)
            self.log_list.takeItem(self.log_list.currentRow())
            self.log_text.clear()
            self.current_log_lines = []
            # noinspection PyUnresolvedReferences
            QMessageBox.information(self, "Deleted", f"Successfully deleted: {filename}", QMessageBox.Ok)

        except Exception as delete_error:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.truncate(0)
                self.current_log_lines = []
                self.log_text.clear()
                # noinspection PyUnresolvedReferences
                QMessageBox.information(
                    self, "Cleared Instead",
                    f"Could not delete '{filename}' (in use), so its contents were cleared instead.",QMessageBox.Ok
                )
            except Exception as clear_error:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to delete or clear the log file:\n{delete_error}\n\nAlso failed to clear contents:\n{clear_error}"
                )

    def copy_log_file_to_clipboard(self, file_path: str):
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(file_path)])
        QApplication.clipboard().setMimeData(mime_data)

# -----------------------
# Discord Menu
# -----------------------

class DiscordServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Community Discord Servers")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, invite_link FROM discord_servers")
            servers = cursor.fetchall()

        for name, link in servers:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, url=link: webbrowser.open(url))
            layout.addWidget(btn)

# -----------------------
# Compass Overlay
# -----------------------

class CompassOverlay(QDialog):
    """
    A floating compass window that shows both Direct and Transit routes to a destination,
    sorted by AP cost. Color-coded: Green = Direct, Purple = Transit.
    """

    def __init__(self, direct_route_info, transit_route_info, parent=None):
        """
        Args:
            direct_route_info (tuple): (int ap_cost, str description)
            transit_route_info (tuple): (int ap_cost, str description)
        """
        super().__init__(parent)
        self.setWindowTitle("Compass Routes")
        self.setMinimumWidth(350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.direct_route_info = direct_route_info
        self.transit_route_info = transit_route_info

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Shortest Available Route:")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        self.route_list = QListWidget()
        self.route_list.setFrameShape(QFrame.NoFrame)

        # Track route data
        self.route_mapping = {}

        routes = [
            ("Direct Route", *self.direct_route_info, QColor("green")),
            ("Transit Route", *self.transit_route_info, QColor("purple")),
        ]
        routes.sort(key=lambda r: r[1])  # sort by AP cost

        for label, cost, desc, color in routes:
            item = QListWidgetItem(f"{label} — {cost} AP\n{desc}")
            item.setForeground(color)
            self.route_list.addItem(item)
            self.route_mapping[label] = (cost, desc)

        self.route_list.itemClicked.connect(self.route_selected)  # ✅ Hook click signal
        layout.addWidget(self.route_list)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def refresh(self, direct_route_info, transit_route_info):
        """
        Update the overlay with new route data.
        """
        self.direct_route_info = direct_route_info
        self.transit_route_info = transit_route_info

        self.route_list.clear()

        routes = [
            ("Direct Route", *self.direct_route_info, QColor("green")),
            ("Transit Route", *self.transit_route_info, QColor(170, 0, 170)),
        ]
        routes.sort(key=lambda r: r[1])

        for label, cost, desc, color in routes:
            item = QListWidgetItem(f"{label} — {cost} AP\n{desc}")
            item.setForeground(color)
            self.route_list.addItem(item)
            self.route_mapping = {}  # Store label → (ap, desc)

    def route_selected(self, item):
        label_text = item.text().split("—")[0].strip()
        route_info = self.route_mapping.get(label_text)
        if route_info and self.parent():
            self.parent().set_compass_display_from_overlay(label_text, route_info)

# -----------------------
# Main Entry Point
# -----------------------

def main() -> None:
    """Run the RBC City Map Application."""
    global APP_ICON
    app = QApplication(sys.argv)
    APP_ICON = QIcon('./images/favicon.ico')
    app.setWindowIcon(APP_ICON)

    splash = SplashScreen("images/loading.png")
    splash.show()
    splash.show_message("Starting up...")

    # Delay decorating until instance is created
    main_window = RBCCommunityMap()

    init_methods = [
        '_init_scraper',
        '_init_window_properties',
        '_init_web_profile',
        '_init_ui_state',
        '_init_characters',
        '_init_ui_components',
        '_finalize_setup'
    ]

    for name in init_methods:
        method = getattr(main_window, name)
        setattr(main_window, name, splash_message(splash)(method))

    main_window.splash = splash
    main_window.show()
    splash.finish(main_window)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()