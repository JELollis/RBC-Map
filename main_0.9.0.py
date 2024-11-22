#!/usr/bin/env python3
# Filename: main_0.9.0

"""
=========================
RBC City Map Application
=========================
This application provides a comprehensive graphical interface for viewing and navigating
the city map of RavenBlack City. It includes features such as zooming in and out, setting
and saving destinations, viewing the closest points of interest, managing user characters,
customizing the application theme, and dynamically interacting with map data. The map data
is stored and managed using an SQLite database, with support for refreshing data scraped
from the 'A View in the Dark' website.

Modules:
- sys: Provides access to system-specific parameters and functions.
- os: Used for interacting with the operating system (e.g., file and directory management).
- pickle: Facilitates the serialization and deserialization of Python objects.
- requests: Allows sending HTTP requests to interact with external websites.
- re: Provides regular expression matching operations.
- datetime: Supplies classes for manipulating dates and times.
- bs4 (BeautifulSoup): Used for parsing HTML and XML documents.
- PySide6: Provides a set of Python bindings for the Qt application framework.
- sqlite3: Interface for SQLite database management.
- webbrowser: Enables the opening of URLs in the default web browser.
- math: Provides mathematical functions used in damage calculations.
- logging: Used for logging debug, information, warning, and error messages.

Classes:
- RBCCommunityMap: The main application class that initializes and manages the user interface,
  character management, web scraping, shopping list generation, minimap functionalities, and theme customization.
- DatabaseViewer: A utility class that displays the contents of database tables in a tabbed view.
- CharacterDialog: A dialog class for adding or modifying user characters.
- ThemeCustomizationDialog: A dialog class for customizing the application theme.
- SetDestinationDialog: A dialog class for setting a destination on the map.
- AVITDScraper: A scraper class that fetches data from 'A View in the Dark' to update guilds
  and shops data in the database.
- ShoppingListTool: A tool for generating shopping lists, including calculating total costs
  based on selected items and character conditions.
- CoinScraper: A class responsible for scraping the current coin count from the character's
  webpage and updating the database with the available coins.
- DamageCalculator: A class for calculating damage dealt to characters based on their blood points (BP).
- DamageCalculatorUI: A user interface for the DamageCalculator, allowing users to calculate
  and analyze damage and optionally add required items to the shopping list.

Functions:
- initialize_database: Sets up the SQLite database for storing map data, character data, settings, and cookies.
- save_cookie_to_db: Saves individual cookies to the SQLite database.
- load_cookies_from_db: Loads cookies from the SQLite database into the web engine.
- clear_cookie_db: Clears all cookies from the SQLite database.
- fetch_table_data: Retrieves and returns the column names and data from a specified database table.
- extract_coordinates_from_html: Extracts map coordinates from the loaded HTML content.
- process_html: Updates map-related data such as character coordinates and coins using extracted HTML data.
- find_nearest_location: Finds the nearest point of interest based on a given set of coordinates.
- calculate_ap_cost: Calculates the Action Point (AP) cost between two map coordinates.
- update_guilds: Updates the guilds data in the SQLite database using scraped data.
- update_shops: Updates the shops data in the SQLite database using scraped data.
- get_next_update_times: Retrieves the next update times for guilds and shops from the SQLite database.
- inject_console_logging: Injects JavaScript into the web page to capture and log console messages.
- apply_theme: Applies the currently selected theme to the application UI.
- save_theme_settings: Saves the customized theme settings to the SQLite database.
- load_theme_settings: Loads the saved theme settings from the SQLite database.
- save_zoom_level_to_database: Saves the minimap zoom level to the SQLite database.
- load_zoom_level_from_database: Loads the minimap zoom level from the SQLite database during application start.
- show_about_dialog: Displays the 'About' dialog with information about the application.
- show_credits_dialog: Displays the 'Credits' dialog with information about contributors.

Key Features:
- Dynamic minimap with zoom functionality, edge-case handling, and grid-based rendering.
- Database-backed storage for settings, themes, character data, and cookies using SQLite.
- Integration with 'A View in the Dark' for data scraping and updating in-game information.
- Support for customizing themes and dynamically updating the application's appearance.
- Ability to calculate damage dealt to characters and generate shopping lists based on in-game needs.

To install all required modules, run the following command:
 pip install requests bs4 PySide6 PySide6-WebEngine
"""

import importlib.util
import math
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
    QMessageBox, QFileDialog, QColorDialog, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QInputDialog,
    QTextEdit
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction, QIntValidator, QMouseEvent
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

def initialize_database(DB_PATH):
    """Initialize the SQLite database with the required schema and data."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Begin transaction
    cursor.executescript("""BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `banks` (
`ID` int NOT NULL ,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
`Name` TEXT DEFAULT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT
                );
CREATE TABLE IF NOT EXISTS coins (
                    character_id INTEGER,
                    pocket INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                );
CREATE TABLE IF NOT EXISTS `color_mappings` (
`id` int NOT NULL ,
`type` TEXT NOT NULL,
`color` TEXT NOT NULL,
PRIMARY KEY (`id`)
);
CREATE TABLE IF NOT EXISTS `columns` (
`ID` int NOT NULL ,
`Name` TEXT NOT NULL,
`Coordinate` int NOT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS cookies (
                    name TEXT,
                    domain TEXT,
                    path TEXT,
                    value TEXT,
                    expiration INTEGER,
                    UNIQUE(name, domain, path)
                );
CREATE TABLE IF NOT EXISTS destinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    col INTEGER,
                    row INTEGER,
                    timestamp TEXT,
                    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
                );
CREATE TABLE IF NOT EXISTS `guilds` (
`ID` int NOT NULL ,
`Name` TEXT NOT NULL,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
`next_update` timestamp NULL DEFAULT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS last_active_character (
                    character_id INTEGER,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                );
CREATE TABLE IF NOT EXISTS `placesofinterest` (
`ID` int NOT NULL ,
`Name` TEXT NOT NULL,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `powers` (
`power_id` int NOT NULL ,
`name` TEXT NOT NULL,
`guild` TEXT NOT NULL,
`cost` int DEFAULT NULL,
`quest_info` text,
`skill_info` text,
PRIMARY KEY (`power_id`)
);
CREATE TABLE IF NOT EXISTS recent_destinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    col INTEGER,
                    row INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
                );
CREATE TABLE IF NOT EXISTS `rows` (
`ID` int NOT NULL ,
`Name` TEXT NOT NULL,
`Coordinate` int NOT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value BLOB
                );
CREATE TABLE IF NOT EXISTS `shop_items` (
`id` int NOT NULL ,
`shop_name` TEXT DEFAULT NULL,
`item_name` TEXT DEFAULT NULL,
`base_price` int DEFAULT NULL,
`charisma_level_1` int DEFAULT NULL,
`charisma_level_2` int DEFAULT NULL,
`charisma_level_3` int DEFAULT NULL,
PRIMARY KEY (`id`)
);
CREATE TABLE IF NOT EXISTS `shops` (
`ID` int NOT NULL ,
`Name` TEXT NOT NULL,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
`next_update` timestamp NULL DEFAULT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `taverns` (
`ID` int NOT NULL ,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
`Name` TEXT NOT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `transits` (
`ID` int NOT NULL ,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
`Name` TEXT NOT NULL,
PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `userbuildings` (
`ID` int NOT NULL ,
`Name` TEXT NOT NULL,
`Column` TEXT NOT NULL,
`Row` TEXT NOT NULL,
PRIMARY KEY (`ID`)
);
INSERT OR IGNORE INTO `banks` ("ID","Column","Row","Name") VALUES (1,'Aardvark','82nd','OmniBank'),
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
 (200,'Zinc','74th','OmniBank');
INSERT OR IGNORE INTO "color_mappings" ("id","type","color") VALUES (1,'bank','blue'),
 (2,'tavern','orange'),
 (3,'transit','red'),
 (4,'user_building','purple'),
 (5,'alley','grey'),
 (6,'default','black'),
 (7,'border','white'),
 (9,'edge','blue'),
 (10,'shop','green'),
 (11,'guild','yellow'),
 (12,'placesofinterest','purple'),
 (13,'background','#d4d4d4'),
 (14,'text_color','#000000'),
 (15,'button_color','#b1b1b1'),
 (30,'set_destination','#1a7f7a'),
 (31,'set_destination_transit','#046380');
INSERT OR IGNORE INTO  "columns" ("ID","Name","Coordinate") VALUES 
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
('102', 'Zestless', '200');
INSERT OR IGNORE INTO  "guilds" ("ID","Name","Column","Row","next_update") VALUES (1,'Allurists Guild 1','Pessimism','66th','2024-11-22 19:00:02'),
 (2,'Allurists Guild 2','Ruby','29th','2024-11-22 19:00:02'),
 (3,'Allurists Guild 3','Jackal','47th','2024-11-22 19:00:02'),
 (4,'Empaths Guild 1','Buzzard','23rd','2024-11-22 19:00:02'),
 (5,'Empaths Guild 2','Buzzard','49th','2024-11-22 19:00:02'),
 (6,'Empaths Guild 3','Squid','37th','2024-11-22 19:00:02'),
 (7,'Immolators Guild 1','Quince','72nd','2024-11-22 19:00:02'),
 (8,'Immolators Guild 2','Diamond','69th','2024-11-22 19:00:02'),
 (9,'Immolators Guild 3','Lonely','65th','2024-11-22 19:00:02'),
 (10,'Thieves Guild 1','Ruby','37th','2024-11-22 19:00:02'),
 (11,'Thieves Guild 2','Olive','40th','2024-11-22 19:00:02'),
 (12,'Thieves Guild 3','Ferret','33rd','2024-11-22 19:00:02'),
 (13,'Travellers Guild 1','Unctuous','73rd','2024-11-22 19:00:02'),
 (14,'Travellers Guild 2','Malachite','63rd','2024-11-22 19:00:02'),
 (15,'Travellers Guild 3','Steel','16th','2024-11-22 19:00:02'),
 (16,'Peacekkeepers Mission 1','Emerald','67th','2024-11-22 19:00:02'),
 (17,'Peacekkeepers Mission 2','Unicorn','33rd','2024-11-22 19:00:02'),
 (18,'Peacekkeepers Mission 3','Emerald','33rd','2024-11-22 19:00:02');
INSERT OR IGNORE INTO  "placesofinterest" ("ID","Name","Column","Row") VALUES (1,'Battle Arena','Zelkova','52nd'),
 (2,'Hall of Binding','Vervain','40th'),
 (3,'Hall of Severance','Walrus','40th'),
 (4,'The Graveyard','Larch','50th'),
 (5,'Cloister of Secrets','Gloom','1st'),
 (6,'Eternal Aubade of Mystical Treasures','Zelkova','47th'),
 (7,'Kindred Hospital','Woe','13th');
INSERT OR IGNORE INTO  "powers" ("power_id","name","guild","cost","quest_info","skill_info") VALUES (1,'Battle Cloak','Any Peacekeeper''s Mission',2000,'None','Buying a cloak from one of the peace missions will prevent you from attacking or being attacked by non-cloaked vampires. The cloak enforces a resting rule which limits you to bite only humans after being zeroed until you reach 250 BP. Vampires cannot bite or attack you during this time. You may still bite and rob non-cloaked vampires, as they can do the same to you. Cloaked vampires appear blue, and if zeroed, they turn pink.'),
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
 (16,'Second Sight','Donation Required',NULL,'Visit donation page for $5 or find a sponsor.','Grants a bonus power of choice from a list, including Celerity-1, Stamina-1, Thievery-1, Shadows-1, Telepathy-1, Charisma-1, or Locate-1.'),
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
 (34,'Thrift 3','Allurists Guild 3',10000,'Buy 1 Perfect Red Rose from 6 specified shops.','15% chance to keep a used item/scroll instead of it burning up.');
INSERT OR IGNORE INTO  "rows" ("ID","Name","Coordinate") VALUES
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
('102', '100th', '200');
INSERT OR IGNORE INTO  "shop_items" ("id","shop_name","item_name","base_price","charisma_level_1","charisma_level_2","charisma_level_3") VALUES (1,'Discount Magic','Perfect Dandelion',35,33,32,31),
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
 (241,'The White House','Pewter Tankard',15000,15000,15000,15000);
INSERT OR IGNORE INTO  "shops" ("ID","Name","Column","Row","next_update") VALUES (1,'Ace Porn','NA','NA','2024-11-22 10:40:02'),
 (2,'Checkers Porn Shop','NA','NA','2024-11-22 10:40:02'),
 (3,'Dark Desires','NA','NA','2024-11-22 10:40:02'),
 (4,'Discount Magic','NA','NA','2024-11-22 10:40:02'),
 (5,'Discount Potions','NA','NA','2024-11-22 10:40:02'),
 (6,'Discount Scrolls','NA','NA','2024-11-22 10:40:02'),
 (7,'Herman''s Scrolls','NA','NA','2024-11-22 10:40:02'),
 (8,'Interesting Times','NA','NA','2024-11-22 10:40:02'),
 (9,'McPotions','NA','NA','2024-11-22 10:40:02'),
 (10,'Paper and Scrolls','NA','NA','2024-11-22 10:40:02'),
 (11,'Potable Potions','NA','NA','2024-11-22 10:40:02'),
 (12,'Potion Distillery','NA','NA','2024-11-22 10:40:02'),
 (13,'Potionworks','NA','NA','2024-11-22 10:40:02'),
 (14,'Reversi Porn','NA','NA','2024-11-22 10:40:02'),
 (15,'Scrollmania','NA','NA','2024-11-22 10:40:02'),
 (16,'Scrolls ''n'' Stuff','NA','NA','2024-11-22 10:40:02'),
 (17,'Scrolls R Us','NA','NA','2024-11-22 10:40:02'),
 (18,'Scrollworks','NA','NA','2024-11-22 10:40:02'),
 (19,'Silver Apothecary','NA','NA','2024-11-22 10:40:02'),
 (20,'Sparks','NA','NA','2024-11-22 10:40:02'),
 (21,'Spinners Porn','NA','NA','2024-11-22 10:40:02'),
 (22,'The Magic Box','NA','NA','2024-11-22 10:40:02'),
 (23,'The Potion Shoppe','NA','NA','2024-11-22 10:40:02'),
 (24,'White Light','NA','NA','2024-11-22 10:40:02'),
 (25,'Ye Olde Scrolles','NA','NA','2024-11-22 10:40:02');
INSERT OR IGNORE INTO  "taverns" ("ID","Column","Row","Name") VALUES (1,'Gum','33rd','Abbot''s Tavern'),
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
 (95,'Pyrites','70th','Ye Olde Gallows Ale House');
INSERT OR IGNORE INTO  "transits" ("ID","Column","Row","Name") VALUES (1,'Mongoose','25th','Calliope'),
 (2,'Zelkova','25th','Clio'),
 (3,'Malachite','25th','Erato'),
 (4,'Mongoose','50th','Euterpe'),
 (5,'Zelkova','50th','Melpomene'),
 (6,'Malachite','50th','Polyhymnia'),
 (7,'Mongoose','75th','Terpsichore'),
 (8,'Zelkova','75th','Thalia'),
 (9,'Malachite','75th','Urania');
INSERT OR IGNORE INTO  "userbuildings" ("ID","Name","Column","Row") VALUES (1,'Ace''s House of Dumont','Cedar','99th'),
 (2,'Alatáriël Maenor','Diamond','50th'),
 (3,'Alpha Dragon''s and Lyric''s House of Dragon and Flame','Amethyst','90th'),
 (4,'AmadisdeGaula''s Stellaburgi','Wulfenite','38th'),
 (5,'Andre''s Crypt','Ferret','10th'),
 (6,'Annabelle''s Paradise','Emerald','85th'),
 (7,'Anthony''s Castle Pacherontis','Walrus','39th'),
 (8,'Anthony''s Gero Claw','Vulture','39th'),
 (9,'Anthony''s Training Grounds','Vulture','35th'),
 (10,'Aphaythean Vineyards','Willow','13th'),
 (11,'Archangel''s Castle','Beech','4th'),
 (12,'Avant''s Garden','Amethyst','68th'),
 (13,'BaShalor''s Rose Garden','Cobalt','41st'),
 (14,'Bitercat''s mews','Lion','42nd'),
 (15,'Black dragonet''s mansion','Oppression','80th'),
 (16,'Blutengel''s Temple of Blood','Fear','13th'),
 (17,'Café Damari','Zelkova','68th'),
 (18,'Cair Paravel','Lion','27th'),
 (19,'Capadocian Castle','Larch','49th'),
 (20,'Carnal Desires','Ivy','66th'),
 (21,'Castle of Shadows','Turquoise','86th'),
 (22,'Castle RavenesQue','Raven','NCL'),
 (23,'ChaosRaven''s Dimensional Tower','Killjoy','23rd'),
 (24,'CHASS''s forever-blues hall','Torment','75th'),
 (25,'CrimsonClover''s Hideaway','Diamond','85th'),
 (26,'CrowsSong''s Blackbird Towers','Wulfenite','3rd'),
 (27,'D''dary Manor','Aardvark','1st'),
 (28,'Daphne''s Dungeons','Malachite','64th'),
 (29,'DarkestDesire''s Chambers','Despair','56th'),
 (30,'Darkwolf''s and liquid-vamp''s Country Cottage','Wulfenite','69th'),
 (31,'Deaths embrace''s Shadow Keep','Holly','81st'),
 (32,'Devil Miyu''s Abeir-Toril','Fear','2nd'),
 (33,'Devil Miyu''s Edge of Reason','Fear','NCL'),
 (34,'Devil Miyu''s Lair','Fear','1st'),
 (35,'Dreamcatcher Haven','Torment','2nd'),
 (36,'Elijah''s Hall of the Lost','Zinc','99th'),
 (37,'ElishaDraken''s Sanguine Ankh','Nightingale','59th'),
 (38,'Epineux Manoir','Olive','70th'),
 (39,'Espy''s Jaded Sorrows','Jaded','69th'),
 (40,'Freedom Trade Alliance','Amethyst','46th'),
 (41,'Gypsychild''s Caravan','Torment','69th'),
 (42,'Halls of Shadow Court','Horror','99th'),
 (43,'Hells Gate''s Castle of Destruction','Lonely','45th'),
 (44,'Hesu''s Place','Raven','24th'),
 (45,'Hexenkessel','Jackal','83rd'),
 (46,'High Council','Obsidian','49th'),
 (47,'Ildiko''s and Brom''s Insanity','Killjoy','53rd'),
 (48,'Jacomo Varis'' Shadow Manor','Raven','96th'),
 (49,'Jaxi''s and Speedy''s Cave','Raven','23rd'),
 (50,'Julia''s Villa','Gloom','76th'),
 (51,'King Lestat''s Le Paradis Caché','Cobalt','90th'),
 (52,'La Cucina','Diamond','28th'),
 (53,'Lady Ophy''s and WhiteLighter Abode','Malaise','94th'),
 (54,'LadyFae''s and nitenurse''s Solas Gealaí Caisleán','Raven','76th'),
 (55,'Lasc Talon''s Estate','Willow','42nd'),
 (56,'Lass'' Lair','Vervain','1st'),
 (57,'Liski''s Shadow Phial','Gloom','99th'),
 (58,'Lord Galamushi''s Enchanted Mansion','Anguish','52nd'),
 (59,'Louvain''s Sanctuary','Gibbon','21st'),
 (60,'Majica''s Playground','Willow','50th'),
 (61,'Mandruleanu Manor','Diamond','86th'),
 (62,'Mansion of Malice','Horror','69th'),
 (63,'Marlena''s Wishing Well','Fear','56th'),
 (64,'Moirai''s Gate to the Church of Blood','Horror','13th'),
 (65,'Moondreamer''s Darkest Desire''s Lighthouse','Fear','9th'),
 (66,'Moonlight Gardens','Turquoise','87th'),
 (67,'Ms Delgado''s Manor','Sorrow','69th'),
 (68,'MyMotherInLaw''s Home for Wayward Ghouls','Amethyst','69th'),
 (69,'Narcisssa''s Vineyard','Aardvark','60th'),
 (70,'Nemesis'' Asyl','Zinc','85th'),
 (71,'NightWatch Headquarters','Larch','51st'),
 (72,'Obsidian''s Arboretum','Obsidian','88th'),
 (73,'Obsidian''s Castle of Warwick','Obsidian','NCL'),
 (74,'Obsidian''s Château de la Lumière','Obsidian','66th'),
 (75,'Obsidian''s château noir','Obsidian','99th'),
 (76,'Obsidian''s Hall of Shifting Realms','Obsidian','15th'),
 (77,'Obsidian''s Penthouse','Obsidian','29th'),
 (78,'Obsidian''s Silver Towers','Obsidian','51st'),
 (79,'Obsidian''s Tranquility','Obsidian','80th'),
 (80,'Obsidian''s, Phoenixxe''s and Em''s Heaven''s Gate','Obsidian','45th'),
 (81,'Occamrazor''s House of Ears','Yew','30th'),
 (82,'Ordo Dracul Sanctum','Nightingale','77th'),
 (83,'Pace Family Ranch','Fir','69th'),
 (84,'Palazzo Lucius','Zebra','27th'),
 (85,'Pandrora and CBK''s Chamber of Horrors','Torment','95th'),
 (86,'RemipunX''s Sacred Yew','Cobalt','42nd'),
 (87,'Renovate''s grove','Umbrella','71st'),
 (88,'Saki''s Fondest Wish','Nightingale','17th'),
 (89,'Samantha Dawn''s Salacious Sojourn','Anguish','53rd'),
 (90,'Sanctuary Hotel','Kraken','27th'),
 (91,'Sartori''s Domicile','Elm','1st'),
 (92,'SCORPIOUS1''s Tower of Truth','Yearning','58th'),
 (93,'Setitevampyr''s temple','Raven','50th'),
 (94,'Shaarinya`s Sanguine Sanctuary','Raven','77th'),
 (95,'Shadow bat''s Sanctorium','Cobalt','76th'),
 (96,'SIE Compound','Raven','13th'),
 (97,'Sitrence''s Lab','Ferret','3rd'),
 (98,'Solanea''s Family Home','Ruby','56th'),
 (99,'Soledad''s Cavern of Shadows','Zinc','NCL'),
 (100,'St. John Bathhouse','Sycamore','76th'),
 (101,'Starreagle''s Paradise Lair','Beryl','24th'),
 (102,'Steele Industries','Umbrella','44th'),
 (103,'Stormy jayne''s web','Nickel','99th'),
 (104,'Talon Castle','Willow','35th'),
 (105,'tejas_dragon''s Lair','Zelkova','69th'),
 (106,'The Ailios Asylum','Amethyst','36th'),
 (107,'The Belly of the Whale','Amethyst','2nd'),
 (108,'The Calignite','Eagle','16th'),
 (109,'The COVE','Knotweek','51st'),
 (110,'The Dragons Lair Club','Vervain','39th'),
 (111,'The Eternal Spiral','Anguish','69th'),
 (112,'The goatsucker''s lair','Yak','13th'),
 (113,'The Halls of Heorot','Jaded','75th'),
 (114,'The House of Night','Walrus','38th'),
 (115,'The Inner Circle Manor','Diamond','26th'),
 (116,'The Ivory Tower','Zelkova','76th'),
 (117,'The Ixora Estate','Lead','48th'),
 (118,'The Kyoto Club','Lion','22nd'),
 (119,'The Lokason Myrkrasetur','Wulfenite','40th'),
 (120,'The Path of Enlightenment Castle','Willow','80th'),
 (121,'The RavenBlack Bite','Oppression','40th'),
 (122,'The Reynolds'' Estate','Beryl','23rd'),
 (123,'The River Passage','Yew','33rd'),
 (124,'The Sakura Garden','Nickel','77th'),
 (125,'The Sanctum of Vermathrax-rex and Bellina','Vexation','99th'),
 (126,'The Sanguinarium','Fear','4th'),
 (127,'The Scythe''s Negotiation Offices','Vauxite','88th'),
 (128,'The Sepulchre of Shadows','Ennui','1st'),
 (129,'The Tower of Thorns','Pilchard','70th'),
 (130,'The Towers of the Crossed Swords','Torment','66th'),
 (131,'The White House','Nervous','75th'),
 (132,'University of Vampiric Enlightenment','Yak','80th'),
 (133,'Virgo''s obsidian waygate','Obsidian','2nd'),
 (134,'Vulture''s Pagoda','Vulture','50th'),
 (135,'Wilde Sanctuary','Willow','51st'),
 (136,'Wilde Wolfe Estate','Vervain','50th'),
 (137,'Willhelm''s Warrior House','Horror','53rd'),
 (138,'Willow Lake Manse','Willow','99th'),
 (139,'Willow Woods'' & The Ent Moot','Willow','54th'),
 (140,'Wolfshadow''s and Crazy''s RBC Casino','Lead','72nd'),
 (141,'Wyndcryer''s TygerNight''s and Bambi''s Lair','Unicorn','77th'),
 (142,'Wyvernhall','Ivy','38th'),
 (143,'X','Emerald','NCL');
COMMIT;
""")

    # Commit changes and close connection
    connection.commit()
    connection.close()

# Call database initialization
initialize_database(DB_PATH)

# -----------------------
# Load Data from Database
# -----------------------

def load_data(DB_PATH):
    """
    Load various map-related data from the SQLite database.

    This function establishes a connection to the SQLite database and retrieves data for columns, rows,
    banks, taverns, transits, user buildings, color mappings, shops, guilds, and places of interest.
    The data is stored in dictionaries or lists and returned for use in the application.

    Args:
        DB_PATH (str): Path to the SQLite database file.

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
    connection = sqlite3.connect(DB_PATH)
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

    return (
        columns,
        rows,
        banks_coordinates,
        taverns_coordinates,
        transits_coordinates,
        user_buildings_coordinates,
        color_mappings,
        shops_coordinates,
        guilds_coordinates,
        places_of_interest_coordinates
    )

# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data(DB_PATH)

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
        self.columns, self.rows, self.banks_coordinates, self.taverns_coordinates, self.transits_coordinates, self.user_buildings_coordinates, self.color_mappings, self.shops_coordinates, self.guilds_coordinates, self.places_of_interest_coordinates = load_data(DB_PATH)

        # Set up the UI components
        self.zoom_level = 3
        self.load_zoom_level_from_database()
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
        Load the theme settings from the SQLite database (settings table).
        Each theme setting is stored individually under the `settings` table.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Query all theme-related settings
            cursor.execute("SELECT setting_name, setting_value FROM settings WHERE setting_name LIKE 'theme_%'")
            settings = cursor.fetchall()

            # Populate color mappings, setting defaults for missing items
            defaults = {
                "theme_background": "#d4d4d4",
                "theme_text_color": "#000000",
                "theme_button_color": "#b1b1b1",
                "theme_bank": "blue",
                "theme_tavern": "orange",
                "theme_transit": "red",
                "theme_user_building": "purple",
                "theme_shop": "green",
                "theme_guild": "yellow",
                "theme_placesofinterest": "purple",
            }

            self.color_mappings = {key.replace("theme_", ""): QColor(value) for key, value in settings}

            # Add missing default values
            for key, default in defaults.items():
                if key.replace("theme_", "") not in self.color_mappings:
                    self.color_mappings[key.replace("theme_", "")] = QColor(default)

            logging.info("Theme settings loaded successfully.")

        except sqlite3.Error as e:
            logging.error(f"Error loading theme settings: {e}")
            # Apply default theme if the database fails
            self.color_mappings = {
                "background": QColor("#d4d4d4"),
                "text_color": QColor("#000000"),
                "button_color": QColor("#b1b1b1"),
            }
        finally:
            connection.close()

    def save_theme_settings(self):
        """
        Save each theme setting individually to the `settings` table in SQLite.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the settings table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT
                )
            ''')

            # Save each color mapping individually
            for key, color in self.color_mappings.items():
                cursor.execute('''
                    INSERT INTO settings (setting_name, setting_value)
                    VALUES (?, ?)
                    ON CONFLICT(setting_name) DO UPDATE SET setting_value = excluded.setting_value
                ''', (f"theme_{key}", color.name()))  # QColor to hex string

            connection.commit()
            logging.info("Theme settings saved successfully.")

        except sqlite3.Error as e:
            logging.error(f"Error saving theme settings: {e}")
        finally:
            connection.close()

    def apply_theme(self):
        """
        Apply the current theme settings to the application's stylesheet.
        """
        try:
            # Retrieve individual theme settings
            background_color = self.color_mappings.get("background", QColor("#d4d4d4")).name()
            text_color = self.color_mappings.get("text_color", QColor("#000000")).name()
            button_color = self.color_mappings.get("button_color", QColor("#b1b1b1")).name()

            # Apply styles
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
                """
            )
            logging.info("Theme applied successfully.")
        except Exception as e:
            logging.error(f"Error applying theme: {e}")

    def change_theme(self):
        """
        Open the theme customization dialog and apply the selected theme.

        This method allows the user to customize the application's theme colors and immediately apply the changes.
        """
        dialog = ThemeCustomizationDialog(self, color_mappings=self.color_mappings)
        if dialog.exec():
            # Update local color mappings and persist changes
            self.color_mappings = dialog.color_mappings
            self.apply_theme()
            self.save_theme_settings()
            logging.info("Theme updated and saved.")

    # -----------------------
    # Cookie Handling
    # -----------------------
    def setup_cookie_handling(self):
        """
        Set up cookie handling, including loading and saving cookies from the 'cookies' table in rbc_map_data.db.
        """
        # No need to initialize the cookies table here as it's done during database initialization
        # Ensure that cookies table exists, it's handled by initialize_database()

        # Connect the QWebEngineProfile's cookie store to the application
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)

        # Load previously saved cookies from the database
        self.load_cookies()

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
        forward_button.setIcon(QIcon('images/forward.png'))
        forward_button.setIconSize(QSize(30, 30))
        forward_button.setFixedSize(30, 30)
        forward_button.setStyleSheet("background-color: transparent; border: none;")
        forward_button.clicked.connect(self.website_frame.forward)
        self.browser_controls_layout.addWidget(forward_button)

        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon('images/refresh.png'))
        refresh_button.setIconSize(QSize(30, 30))
        refresh_button.setFixedSize(30, 30)
        refresh_button.setStyleSheet("background-color: transparent; border: none;")
        refresh_button.clicked.connect(lambda: self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl')))
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
        info_frame.setFixedHeight(260)  # Increased height for better spacing
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)  # Space between each label for clarity
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Common style for each info label with padding, border, and smaller font size
        label_style = """
            background-color: {color};
            color: white;
            font-weight: bold;
            padding: 5px;
            border: 2px solid black;
            font-size: 12px;  /* Set smaller font size for readability */
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

        # Damage Calculator Tool
        damage_calculator_action = QAction('Damage Calculator', self)
        damage_calculator_action.triggered.connect(self.open_damage_calculator_tool)
        tools_menu.addAction(damage_calculator_action)

        # Power Reference Tool
        power_reference_action = QAction('Power Reference Tool', self)
        power_reference_action.triggered.connect(self.open_powers_dialog)
        tools_menu.addAction(power_reference_action)

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

        QMessageBox.information(self, "Damage Calculator Shopping List", shopping_list_text)

    def open_powers_dialog(self):
        """
        Opens the Powers Information dialog.
        """
        # Initialize the PowersDialog with the SQLite database connection
        powers_dialog = PowersDialog(DB_PATH)  # Pass the SQLite connection

        # Show the PowersDialog as a modal
        powers_dialog.exec()

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
                logging.debug(f"Selected character set: {self.selected_character}")
                if 'id' not in self.selected_character:
                    logging.error("Loaded character data lacks 'id'. Check database integrity.")
            else:
                logging.warning("No characters found in the database.")
                self.selected_character = None

        except sqlite3.Error as e:
            logging.error(f"Failed to load characters from database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load characters: {e}")
            self.characters = []
            self.selected_character = None
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

        Args:
            item (QListWidgetItem): The selected item in the list.

        Logs the selected character, saves the last active character,
        logs out the current character, and then logs in the selected one.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)

        if selected_character:
            logging.debug(f"Selected character: {character_name}")
            self.selected_character = selected_character

            # Fetch character ID if missing
            if 'id' not in self.selected_character:
                connection = sqlite3.connect(DB_PATH)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT id FROM characters WHERE name = ?", (character_name,))
                    character_row = cursor.fetchone()
                    if character_row:
                        self.selected_character['id'] = character_row[0]
                        logging.debug(f"Character '{character_name}' ID set to {self.selected_character['id']}.")
                    else:
                        logging.error(f"Character '{character_name}' not found in characters table.")
                except sqlite3.Error as e:
                    logging.error(f"Failed to retrieve character_id for '{character_name}': {e}")
                finally:
                    connection.close()

            # Save last active character
            if 'id' in self.selected_character:
                self.save_last_active_character(self.selected_character['id'])
            else:
                logging.error(f"Cannot save last active character: ID missing for '{character_name}'.")

            # Logout current character and login the selected one
            self.logout_current_character()
            QTimer.singleShot(1000, self.login_selected_character)
        else:
            logging.error(f"Character '{character_name}' selection failed.")

    def logout_current_character(self):
        """
        Logout the current character by navigating to the logout URL.
        """
        logging.debug("Logging out current character.")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))
        QTimer.singleShot(1000, self.login_selected_character)

    def login_selected_character(self):
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        logging.debug(
            f"Logging in character: {self.selected_character['name']} with ID: {self.selected_character.get('id')}")
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
            x_value = int(x_input['value'])
            y_value = int(y_input['value'])
            logging.debug(f"Extracted coordinates from input fields: x={x_value}, y={y_value}")
            return x_value, y_value

        current_location_td = soup.find('td', {'class': 'street', 'style': 'border: solid 1px white;'})

        if current_location_td:
            form = current_location_td.find('form')
            if form:
                x_value = int(form.find('input', {'name': 'x'})['value'])
                y_value = int(form.find('input', {'name': 'y'})['value'])
                logging.debug(f"Extracted coordinates from form: x={x_value}, y={y_value}")
                return x_value, y_value

        logging.debug("No coordinates found in the HTML content.")
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

        # Search for the bank balance line (found by "Welcome to Omnibank")
        bank_match = re.search(r"Welcome to Omnibank. Your account has (\d+) coins in it.", html)

        # Search for the pocket balance line (found by "You have \d+ coins")
        pocket_match = re.search(r"You have (\d+) coins", html)

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

        # Handle pocket coin balance update
        if pocket_match:
            pocket_coins = int(pocket_match.group(1))
            logging.info(f"Pocket coins found: {pocket_coins}")

            # Update the pocket coins in the SQLite database
            cursor.execute('''
                UPDATE coins 
                SET pocket = ? 
                WHERE character_id = ?
            ''', (pocket_coins, character_id))

        # Handle deposit action (optional, depending on your needs)
        deposit_match = re.search(r"You deposit (\d+) coins.", html)
        if deposit_match:
            deposit_coins = int(deposit_match.group(1))
            logging.info(f"Deposit found: {deposit_coins} coins")

            # Reduce the pocket coins by the deposited amount
            cursor.execute('''
                UPDATE coins
                SET pocket = pocket - ?
                WHERE character_id = ?
            ''', (deposit_coins, character_id))

        # Handle withdrawal action (optional, depending on your needs)
        withdraw_match = re.search(r"You withdraw (\d+) coins.", html)
        if withdraw_match:
            withdraw_coins = int(withdraw_match.group(1))
            logging.info(f"Withdrawal found: {withdraw_coins} coins")

            # Increase the pocket coins by the withdrawn amount
            cursor.execute('''
                UPDATE coins
                SET pocket = pocket + ?
                WHERE character_id = ?
            ''', (withdraw_coins, character_id))

        # Handle transit coin update (optional, depending on your needs)
        transit_match = re.search(r"It costs 5 coins to ride. You have (\d+).", html)
        if transit_match:
            coins_in_pocket = int(transit_match.group(1))
            logging.info(f"Transit found: Pocket coins updated to {coins_in_pocket}")

            # Explicitly set the pocket coin count after transit
            cursor.execute('''
                UPDATE coins
                SET pocket = ?
                WHERE character_id = ?
            ''', (coins_in_pocket, character_id))

        # Handle other coin-related actions (e.g., hunting, robbing, etc.)
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

        # Handle other coin-related actions (e.g., hunting, robbing, etc.)
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

        logging.debug(f"Drawing minimap with column_start={self.column_start}, row_start={self.row_start}, "
                      f"zoom_level={self.zoom_level}, block_size={block_size}")

        def draw_location(column_index, row_index, color, label_text=None):
            """
            Draws a location on the minimap with dynamic scaling and border.

            Args:
                column_index (int): Column index of the location.
                row_index (int): Row index of the location.
                color (QColor): Color to fill the location.
                label_text (str, optional): Label text to draw at the location. Defaults to None.
            """
            logging.debug(f"Location '{label_text}' Initial column_index={column_index}, row_index={row_index}")
            # Adjust offsets specifically for edge cases
            adjusted_column_index = column_index - 1 if column_index == 1 else column_index
            adjusted_row_index = row_index - 1 if row_index == 1 else row_index

            # Calculate cell position on the minimap grid
            x0 = (adjusted_column_index - self.column_start) * block_size
            y0 = (adjusted_row_index - self.row_start) * block_size

            # Edge cases: Ensure edge locations draw correctly at the map edges
            if column_index == 1:
                adjusted_column_index = column_index
                x0 = (column_index - self.column_start) * block_size
            if row_index == 1:
                adjusted_row_index = row_index
                y0 = (row_index - self.row_start) * block_size

            # Ensure the adjusted location is within bounds
            if x0 < 0 or y0 < 0 or x0 >= self.minimap_size or y0 >= self.minimap_size:
                logging.debug(
                    f"Skipping drawing location '{label_text}' at column_index={column_index}, row_index={row_index}, "
                    f"x0={x0}, y0={y0} (out of bounds)")
                return

            logging.debug(f"Drawing location '{label_text}' at column_index={column_index}, row_index={row_index}, "
                          f"x0={x0}, y0={y0}, color={color.name()}")

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
                logging.debug(f"Drawing grid cell at column_index={column_index}, row_index={row_index}, "
                              f"x0={x0}, y0={y0}")

                # Draw the cell background
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                # Special location handling
                column_name = next((name for name, coord in self.columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in self.rows.items() if coord == row_index), None)

                # Draw cell background color
                if column_index <= 0 or column_index >= 201 or row_index <= 0 or row_index >= 201:
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
                # Add +1,+1 offset specifically for banks
                adjusted_column_index = column_index + 1
                adjusted_row_index = row_index + 1
                draw_location(adjusted_column_index, adjusted_row_index, self.color_mappings["bank"], "Bank")
            else:
                logging.warning(f"Skipping bank at {col_name} & {row_name} due to missing coordinates")

        # Draw other locations without the offset
        for name, (column_index, row_index) in self.taverns_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["tavern"], name)

        for name, (column_index, row_index) in self.transits_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["transit"], name)

        for name, (column_index, row_index) in self.user_buildings_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["user_building"], name)

        for name, (column_index, row_index) in self.shops_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["shop"], name)

        for name, (column_index, row_index) in self.guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["guild"], name)

        for name, (column_index, row_index) in self.places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
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
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit_coords[0] - self.column_start) * block_size + block_size // 2,
                (nearest_transit_coords[1] - self.row_start) * block_size + block_size // 2
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
            self.save_zoom_level_to_database()  # Save the updated zoom level
            self.website_frame.page().toHtml(self.process_html)

    def zoom_out(self):
        """
        Zoom out the minimap, ensuring the character stays centered.
        """
        if self.zoom_level < 7:  # Adjusted max level to improve readability
            self.zoom_level += 2  # Increase by 2 to keep zoom levels odd-numbered
            self.save_zoom_level_to_database()  # Save the updated zoom level
            self.website_frame.page().toHtml(self.process_html)

    def save_zoom_level_to_database(self):
        """
        Save the current zoom level to the settings table in the database.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            query = """
            INSERT INTO settings (setting_name, setting_value)
            VALUES ('minimap_zoom', ?)
            ON CONFLICT(setting_name) DO UPDATE SET setting_value = ?;
            """
            cursor.execute(query, (self.zoom_level, self.zoom_level))
            connection.commit()
            logging.debug(f"Zoom level saved to database: {self.zoom_level}")
        except sqlite3.Error as e:
            logging.error(f"Failed to save zoom level to database: {e}")
        finally:
            connection.close()

    def load_zoom_level_from_database(self):
        """
        Load the saved zoom level from the settings table in the database.
        If no value is found, set it to the default (3).
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            query = "SELECT setting_value FROM settings WHERE setting_name = 'minimap_zoom';"
            result = cursor.execute(query).fetchone()
            if result:
                self.zoom_level = int(result[0])
                logging.debug(f"Zoom level loaded from database: {self.zoom_level}")
            else:
                self.zoom_level = 3  # Default zoom level
                logging.debug("No saved zoom level found. Defaulting to 3.")
        except sqlite3.Error as e:
            self.zoom_level = 3  # Fallback default zoom level
            logging.error(f"Failed to load zoom level from database: {e}")
        finally:
            connection.close()

    def recenter_minimap(self):
        """
        Recenter the minimap so that the character's location is at the center cell,
        including visible but non-traversable areas beyond the traversable range.
        """
        if not hasattr(self, 'character_x') or not hasattr(self, 'character_y'):
            logging.error("Character position not set. Cannot recenter minimap.")
            return

        # Calculate zoom offset (-1 for 5x5, -2 for 7x7, etc.)
        zoom_offset = (self.zoom_level - 4) // 2

        # Calculate starting positions to center the character
        column_start = self.character_x - zoom_offset
        row_start = self.character_y - zoom_offset

        # Allow visible but non-traversable cells up to 203,203 for 7x7 zoom
        column_start = max(-1, min(column_start, 203 - self.zoom_level))
        row_start = max(-1, min(row_start, 203 - self.zoom_level))

        logging.debug(f"Recentered minimap: character_x={self.character_x}, character_y={self.character_y}, "
                      f"column_start={column_start}, row_start={row_start}, zoom_level={self.zoom_level}")

        # Update minimap start positions
        self.column_start = column_start
        self.row_start = row_start

        # Refresh the minimap
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
        if event.button() == Qt.MouseButton.LeftButton:
            # Map global click position to minimap's local coordinates
            local_position = self.minimap_label.mapFromGlobal(event.globalPosition().toPoint())
            click_x, click_y = local_position.x(), local_position.y()

            # Validate click is within the minimap
            if 0 <= click_x < self.minimap_label.width() and 0 <= click_y < self.minimap_label.height():
                # Calculate relative coordinates and block size
                block_size = self.minimap_size // self.zoom_level
                relative_x = click_x
                relative_y = click_y

                # Determine clicked cell
                clicked_column = self.column_start + (relative_x // block_size)
                clicked_row = self.row_start + (relative_y // block_size)

                # Calculate new center positions
                center_offset = self.zoom_level // 2

                # Allow extended bounds
                min_start = -(self.zoom_level // 2)
                max_start = 201 + (self.zoom_level // 2) - self.zoom_level

                new_column_start = clicked_column - center_offset
                new_row_start = clicked_row - center_offset

                # Clamp to extended valid ranges
                new_column_start = max(min_start, min(new_column_start, max_start))
                new_row_start = max(min_start, min(new_row_start, max_start))

                # Update minimap start positions
                self.column_start = new_column_start
                self.row_start = new_row_start

                # Debug logs
                logging.debug(f"Click at ({click_x}, {click_y}) -> Cell: ({clicked_column}, {clicked_row})")
                logging.debug(f"New minimap start: column={self.column_start}, row={self.row_start}")

                # Update the minimap display
                self.update_minimap()
            else:
                logging.debug(f"Click ({click_x}, {click_y}) is outside the minimap bounds.")

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

    def save_to_recent_destinations(self, destination_coords, character_id):
        """
        Save the current destination to the recent destinations for the specific character,
        keeping only the last 10 entries per character.

        Args:
            destination_coords (tuple): Coordinates of the destination to save.
            character_id (int): ID of the character for which to save the destination.
        """
        if destination_coords is None or character_id is None:
            return

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Insert the new destination with character_id
            cursor.execute("INSERT INTO recent_destinations (character_id, col, row) VALUES (?, ?, ?)",
                           (character_id, *destination_coords))

            # Keep only the 10 most recent destinations per character
            cursor.execute("""
                DELETE FROM recent_destinations 
                WHERE character_id = ? AND id NOT IN (
                    SELECT id FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10
                )
            """, (character_id, character_id))

            connection.commit()
            logging.info(
                f"Destination {destination_coords} saved to recent destinations for character ID {character_id}.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save recent destination: {e}")
        finally:
            connection.close()

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
            bank_coords = nearest_bank[0][1]
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
                (name for name, coords in self.places_of_interest_coordinates.items() if coords == destination_coords),
                None
            )
            destination_label_text = f"Set Destination - {place_name}" if place_name else "Set Destination"
            self.destination_label.setText(
                f"{destination_label_text}\n{destination_intersection} - AP: {destination_ap_cost}")

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

                # Update the transit destination label
                self.transit_destination_label.setText(
                    f"Set Destination - {char_transit_name} to {dest_transit_name}\n"
                    f"{self.get_intersection_name(dest_transit_coords)} - Total AP: {total_ap_via_transit}"
                )
            else:
                self.transit_destination_label.setText("Transit Route Info Unavailable")

        else:
            # Clear labels when no destination is set
            self.destination_label.setText("No Destination Set")
            self.transit_destination_label.setText("No Destination Set")

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
                          "Version 0.9.0\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Development team shown in credits.\n\n\n"
                          "This program is based on the LIAM\u00B2 app by Leprichaun")

    from PySide6.QtCore import QTimer

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
            "Design and Layout: Shuvi, Blair Wilson (Ikunnaprinsess)\n\n\n\n"
            "Special Thanks:\n\n"
            "Cain \"Leprechaun\" McBride for the LIAM\u00B2 program \nthat inspired this program\n\n"
            "Cliff Burton for A View in the Dark which is \nwhere Shops and Guilds data is retrieved\n\n"
            "Everyone who contributes to the \nRavenBlack Wiki and A View in the Dark\n\n"
            "Anders for RBNav and the help along the way\n\n\n\n"
            "Most importantly, thank YOU for using this app. \nWe all hope it serves you well!"
        )

        credits_dialog = QDialog()
        credits_dialog.setWindowTitle('Credits')
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

        # Create and start the scrolling animation
        animation = QPropertyAnimation(credits_label, b"geometry")
        animation.setDuration(35000)  # 30 seconds
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(
            QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        # Close dialog 5 seconds after the animation finishes
        def close_after_delay():
            QTimer.singleShot(2500, credits_dialog.accept)  # Wait 2.5 seconds before closing

        animation.finished.connect(close_after_delay)
        animation.start()

        credits_dialog.exec()

    # -----------------------
    # Database Viewer
    # -----------------------
    def open_database_viewer(self):
        """
        Open the database viewer to browse and inspect data from the RBC City Map database.

        This method connects to the SQLite database, fetches the data from specified tables,
        and displays it in a new DatabaseViewer window.
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
            db_connection: The established SQLite database connection.
        """
        super().__init__()
        self.setWindowTitle('SQLite Database Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Create a QTabWidget to hold the table views
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.db_connection = db_connection
        self.cursor = self.db_connection.cursor()

        # Query to get all table names
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
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
        # Use PRAGMA to get column information and SELECT to fetch data
        self.cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        column_names = [col[1] for col in self.cursor.fetchall()]

        self.cursor.execute(f"SELECT * FROM `{table_name}`")
        data = self.cursor.fetchall()

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
        Update the SQLite database with the scraped data.

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
            cursor.execute(f"UPDATE {table} SET `Column`='NA', `Row`='NA', `next_update`=?", (next_update,))
        except sqlite3.Error as e:
            logging.error(f"Failed to reset {table} entries to 'NA': {e}")
            return

        # Step 2: Update with the correct data from the scraped results
        for name, column, row in data:
            try:
                logging.debug(
                    f"Updating {table} entry: Name={name}, Column={column}, Row={row}, Next Update={next_update}")
                cursor.execute(
                    f"UPDATE {table} SET `Column`=?, `Row`=?, `next_update`=? WHERE `Name`=?",
                    (column, row, next_update, name)
                )
            except sqlite3.Error as e:
                logging.error(f"Failed to update {table} entry '{name}': {e}")

        self.connection.commit()
        cursor.close()
        logging.info(f"Database updated for {table}.")

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
class set_destination_dialog(QDialog):
    """
    A dialog for setting a destination on the map.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Destination")
        self.resize(200, 250)
        self.parent = parent  # Access to parent methods and properties
        logging.info("Initialized set_destination_dialog")

        # Main layout setup
        main_layout = QVBoxLayout(self)

        # Define the style with a border for dropdowns
        dropdown_style = """
            QComboBox {
                border: 2px solid #5F6368;
                padding: 5px;
                border-radius: 4px;
            }
        """

        # Dropdown for recent destinations
        self.recent_destinations_dropdown = QComboBox()
        self.populate_recent_destinations()

        # Dropdowns for selecting destinations
        dropdown_layout = QFormLayout()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()

        # Populate dropdowns with values from the data sources
        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

        logging.info("Populated destination dropdowns.")

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

        # Control buttons
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
        Populate the recent destinations dropdown for the selected character.
        """
        logging.info("Populating recent destinations.")
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem("Select a recent destination")

        character_id = self.parent.selected_character.get('id')

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Fetch recent destinations for the character
            cursor.execute(
                "SELECT col, row FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10",
                (character_id,)
            )
            recent_destinations = cursor.fetchall()
            logging.info(f"Fetched {len(recent_destinations)} recent destinations for character {character_id}.")

            # Process each recent destination
            for col, row in recent_destinations:
                try:
                    # Convert to integers if they aren't already
                    col = int(col)
                    row = int(row)
                except ValueError:
                    logging.error("Non-integer values for col/row: col=%s, row=%s", col, row)
                    continue

                # Round coordinates to the nearest odd number (unless boundary)
                rounded_col = col if col in (0, 200) else (col if col % 2 != 0 else col - 1)
                rounded_row = row if row in (0, 200) else (row if row % 2 != 0 else row - 1)
                logging.debug("Rounded col=%d to %d and row=%d to %d", col, rounded_col, row, rounded_row)

                # Fetch street names
                cursor.execute("SELECT Name FROM `columns` WHERE Coordinate = ?", (rounded_col,))
                col_name = cursor.fetchone()
                col_name = col_name[0] if col_name else f"Column {rounded_col}"

                cursor.execute("SELECT Name FROM `rows` WHERE Coordinate = ?", (rounded_row,))
                row_name = cursor.fetchone()
                row_name = row_name[0] if row_name else f"Row {rounded_row}"

                # Check for a named building at this location across all relevant tables
                building_name = None
                for table in ["banks", "guilds", "placesofinterest", "shops", "taverns", "transits", "userbuildings"]:
                    cursor.execute(
                        f"SELECT Name FROM `{table}` WHERE `Column` = ? AND `Row` = ?",
                        (col_name, row_name)
                    )
                    result = cursor.fetchone()
                    if result:
                        building_name = result[0]
                        break

                # Format display name
                display_name = f"{col_name} & {row_name}"
                if building_name:
                    display_name += f" - {building_name}"

                self.recent_destinations_dropdown.addItem(display_name, (col, row))
                logging.info(f"Added recent destination: {display_name}")
        except sqlite3.Error as e:
            logging.error(f"Error fetching recent destinations: {e}")
        finally:
            connection.close()

    def populate_dropdown(self, dropdown, items):
        logging.info("Populating dropdown with %d items.", len(items))
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems(items)

    def update_comboboxes(self):
        logging.info("Updating comboboxes.")
        self.show_notification("Updating Shop and Guild Data. Please wait...")

        # Run the scraper to update data if available
        if hasattr(self.parent, 'AVITD_scraper') and self.parent.AVITD_scraper:
            self.parent.AVITD_scraper.scrape_guilds_and_shops()

        # Reload data from the SQLite database
        try:
            updated_data = load_data()
            self.parent.columns, self.parent.rows, self.parent.banks_coordinates, \
                self.parent.taverns_coordinates, self.parent.transits_coordinates, \
                self.parent.user_buildings_coordinates, self.parent.color_mappings, \
                self.parent.shops_coordinates, self.parent.guilds_coordinates, \
                self.parent.places_of_interest_coordinates = updated_data

            # Populate dropdowns with updated data
            self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
            self.populate_dropdown(self.bank_dropdown,
                                   [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
            self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
            self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
            self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
            self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
            self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

            # Call update_minimap to redraw the map with the new data
            if hasattr(self.parent, 'update_minimap') and callable(self.parent.update_minimap):
                logging.info("Updating minimap with new data.")
                self.parent.update_minimap()

            logging.info("Comboboxes updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update comboboxes: {e}")

    def show_notification(self, message):
        logging.info("Displaying notification: %s", message)
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
        if not self.parent.selected_character:
            logging.warning("No character selected for clearing destination.")
            return

        character_id = self.parent.selected_character['id']
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        try:
            cursor.execute('DELETE FROM destinations WHERE character_id = ?', (character_id,))
            connection.commit()
            logging.info(f"Cleared destination for character {character_id}")

            self.parent.destination = None
            self.parent.update_minimap()
        except sqlite3.Error as e:
            logging.error(f"Failed to clear destination for character {character_id}: {e}")
        finally:
            connection.close()

        self.accept()

    def set_destination(self):
        logging.info("Attempting to set destination.")

        # Retrieve the selected destination coordinates
        destination_coords = self.get_selected_destination()

        if not destination_coords:
            logging.warning("No valid destination selected.")
            # Show a dialog to the user if no destination is selected
            self.show_error_dialog("No destination selected", "Please select a valid destination from the list.")
            return

        if self.parent.selected_character:
            character_id = self.parent.selected_character['id']
            logging.info(f"Setting destination for character {character_id} to {destination_coords}")

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            try:
                # First, check if the destination already exists in recent destinations
                cursor.execute('''
                    SELECT 1 FROM recent_destinations WHERE character_id = ? AND col = ? AND row = ?
                ''', (character_id, destination_coords[0], destination_coords[1]))
                existing_destination = cursor.fetchone()

                if existing_destination:
                    logging.info("Destination already exists in recent destinations. Not adding again.")
                else:
                    # If not, add it to the recent destinations
                    cursor.execute('''
                        INSERT INTO recent_destinations (character_id, col, row, timestamp)
                        VALUES (?, ?, ?, datetime('now'))
                    ''', (character_id, destination_coords[0], destination_coords[1]))
                    connection.commit()
                    logging.info(f"Added destination to recent destinations: {destination_coords}")

                # Now, update or insert the destination as the current destination
                cursor.execute("SELECT id FROM destinations WHERE character_id = ?", (character_id,))
                existing_destination = cursor.fetchone()

                if existing_destination:
                    cursor.execute('''
                        UPDATE destinations
                        SET col = ?, row = ?, timestamp = datetime('now')
                        WHERE character_id = ?
                    ''', (destination_coords[0], destination_coords[1], character_id))
                else:
                    cursor.execute('''
                        INSERT INTO destinations (character_id, col, row, timestamp)
                        VALUES (?, ?, ?, datetime('now'))
                    ''', (character_id, destination_coords[0], destination_coords[1]))

                connection.commit()
                logging.info(f"Destination set successfully for character {character_id} at {destination_coords}.")

                self.parent.destination = destination_coords
                self.parent.update_minimap()
            except sqlite3.Error as e:
                logging.error(f"Failed to set destination for character {character_id}: {e}")
            finally:
                connection.close()

            self.accept()
        else:
            logging.warning("No character selected. Destination not set.")
            self.show_error_dialog("No character selected", "Please select a character to set the destination.")

    def get_selected_destination(self):
        logging.info("Retrieving selected destination.")

        # Check recent destinations dropdown first
        recent_selection = self.recent_destinations_dropdown.currentText()
        if recent_selection and recent_selection != "Select a recent destination":
            # Fetch the coordinates stored with the dropdown item
            coords = self.recent_destinations_dropdown.currentData()
            logging.info(f"Selected recent destination: {recent_selection} with coordinates {coords}")
            return coords

        # Dropdowns with predefined coordinates
        selected_dropdowns = [
            (self.tavern_dropdown, self.parent.taverns_coordinates),
            (self.transit_dropdown, self.parent.transits_coordinates),
            (self.shop_dropdown, self.parent.shops_coordinates),
            (self.guild_dropdown, self.parent.guilds_coordinates),
            (self.poi_dropdown, self.parent.places_of_interest_coordinates),
            (self.user_building_dropdown, self.parent.user_buildings_coordinates)
        ]

        # Check each dropdown for a valid selection
        for dropdown, data in selected_dropdowns:
            selection = dropdown.currentText()
            if selection and selection != "Select a destination":
                coords = data.get(selection)
                logging.info(f"Selected destination: {selection} with coordinates {coords}")
                return coords

        # Special handling for banks
        bank_selection = self.bank_dropdown.currentText()
        if bank_selection and bank_selection != "Select a destination":
            # Parse the bank's "ABC Street & 123 Street" format
            col_name, row_name = bank_selection.split(" & ")

            # Look up column and row coordinates using parent data (columns and rows tables)
            col_coord = self.parent.columns.get(col_name.strip())
            row_coord = self.parent.rows.get(row_name.strip())

            if col_coord is not None and row_coord is not None:
                # Apply +1 offset for cell directly SE of intersection
                logging.info("Selected bank destination: %s with coordinates (%d, %d)", bank_selection, col_coord + 1,
                             row_coord + 1)
                return col_coord + 1, row_coord + 1

        # Custom location entry
        col = self.parent.columns.get(self.columns_dropdown.currentText())
        row = self.parent.rows.get(self.rows_dropdown.currentText())
        if col is not None and row is not None:
            logging.info("Custom destination selected: Column %s, Row %s", col, row)
            return col, row

        logging.warning("No valid destination selected.")
        return None

    def show_error_dialog(self, title, message):
        # Create a dialog box to display the error message
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle(title)
        error_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        message_label = QLabel(message)
        layout.addWidget(message_label)

        # Adding a button to close the dialog
        close_button = QPushButton("Close")
        close_button.clicked.connect(error_dialog.accept)
        layout.addWidget(close_button)

        error_dialog.setLayout(layout)
        error_dialog.setFixedSize(300, 100)  # Set a fixed size for the dialog
        error_dialog.exec()

# -----------------------
# Shopping list Tools
# -----------------------
class ShoppingListTool(QMainWindow):
    def __init__(self, character_name, DB_PATH):
        """
        Initialize the Shopping List Tool with SQLite database support.

        Args:
            character_name (str): Name of the character using the tool.
            DB_PATH (str): Path to the SQLite database.
        """
        super().__init__()
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)
        self.character_name = character_name
        self.DB_PATH = DB_PATH  # Central SQLite DB path

        # Initialize SQLite connection
        self.sqlite_connection = sqlite3.connect(self.DB_PATH)
        self.sqlite_cursor = self.sqlite_connection.cursor()

        # Initialize shopping list total
        self.list_total = 0

        # Setting up UI
        self.setup_ui()

        # Load data from SQLite (shop info)
        self.populate_shop_dropdown()

    def setup_ui(self):
        # Initialize UI elements
        self.shop_combobox = QComboBox(self)
        self.charisma_combobox = QComboBox(self)
        self.charisma_combobox.currentIndexChanged.connect(self.load_items)
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
            f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}"
        )
        layout.addWidget(self.total_label)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)

        # Load items when shop or charisma level changes
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self.update_shopping_list_prices)

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
            item_price = int(item_price.split(" Coins")[0])

            # Prompt user for the quantity
            quantity, ok = QInputDialog.getInt(self, "Enter Quantity", f"How many {item_name} to add?", 1, 1)
            if ok:
                # Check if the item is already in the shopping list
                for i in range(self.shopping_list.count()):
                    existing_item_text = self.shopping_list.item(i).text()
                    existing_item_name = existing_item_text.split(" - ")[0]
                    if existing_item_name == item_name:
                        # Update the quantity if the item is already present
                        existing_quantity = int(existing_item_text.split(" - ")[2].split("x")[0])
                        self.shopping_list.item(i).setText(
                            f"{item_name} - {item_price} Coins - {existing_quantity + quantity}x"
                        )
                        self.update_total()
                        return

                # If the item is not in the list, add it with the entered quantity
                self.shopping_list.addItem(f"{item_name} - {item_price} Coins - {quantity}x")
                self.update_total()

    def remove_item(self):
        """
        Prompt for quantity to remove from the selected item in the shopping list.
        """
        selected_item = self.shopping_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            item_name, item_price, item_quantity = item_text.split(" - ")
            item_price = int(item_price.split(" Coins")[0])
            item_quantity = int(item_quantity.split("x")[0])

            # Prompt the user for the quantity to remove
            quantity_to_remove, ok = QInputDialog.getInt(self, "Enter Quantity", f"How many {item_name} to remove?", 1, 1, item_quantity)
            if ok:
                new_quantity = item_quantity - quantity_to_remove
                if new_quantity > 0:
                    # Update the item's quantity in the list without re-adding "Coins"
                    self.shopping_list.currentItem().setText(f"{item_name} - {item_price} Coins - {new_quantity}x")
                else:
                    # Remove the item if the quantity reaches zero
                    self.shopping_list.takeItem(self.shopping_list.row(selected_item))

                self.update_total()

    def populate_shop_dropdown(self):
        """
        Populate the shop dropdown with available shops from the MySQL database.
        """
        try:
            self.sqlite_cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
            shops = self.sqlite_cursor.fetchall()
            for shop in shops:
                self.shop_combobox.addItem(shop[0])
        except pymysql.MySQLError as err:
            print(f"Error fetching shop names: {err}")

    def load_items(self):
        """
        Load items from the selected shop and charisma level into the available items list.
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
        WHERE shop_name = ?
        """
        self.sqlite_cursor.execute(query, (shop_name,))
        items = self.sqlite_cursor.fetchall()

        for item in items:
            item_name = item[0]
            price = item[1]
            self.available_items_list.addItem(f"{item_name} - {price} Coins")

    def update_shopping_list_prices(self):
        """
        Update the prices in the shopping list based on the selected charisma level.
        """
        shop_name = self.shop_combobox.currentText()
        charisma_level = self.charisma_combobox.currentText()

        # Determine the price column based on charisma level
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(charisma_level, "base_price")

        # Update prices for each item in the shopping list
        for i in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(i).text()
            item_name = item_text.split(" - ")[0]
            quantity = int(item_text.split(" - ")[2].split("x")[0])

            # Query for the updated price from MySQL
            query = f"""
            SELECT {price_column}
            FROM shop_items
            WHERE item_name = ? AND shop_name = ?
            """
            self.sqlite_cursor.execute(query, (item_name, shop_name))
            result = self.sqlite_cursor.fetchone()

            if result:
                updated_price = result[0]
                self.shopping_list.item(i).setText(f"{item_name} - {updated_price} Coins - {quantity}x")

        self.update_total()

    def update_total(self):
        """
        Update the total cost of the shopping list and display it.
        """
        self.list_total = 0
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            item_price = int(item_text.split(" - ")[1].split(" Coins")[0])
            item_quantity = int(item_text.split(" - ")[2].split("x")[0])
            self.list_total += item_price * item_quantity

        # Update the label with the correct total, considering the coins in pocket and bank
        self.total_label.setText(
            f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}"
        )

    def coins_in_pocket(self):
        """
        Retrieve the number of coins in the pocket for the given character from the SQLite DB.
        """
        cursor = self.sqlite_connection.cursor()
        cursor.execute("SELECT id FROM characters WHERE name = ?", (self.character_name,))
        character_id = cursor.fetchone()

        if character_id:
            cursor.execute("SELECT pocket FROM coins WHERE character_id = ?", (character_id[0],))
            result = cursor.fetchone()
            return result[0] if result else 0
        return 0

    def coins_in_bank(self):
        """
        Retrieve the number of coins in the bank for the given character from the SQLite DB.
        """
        cursor = self.sqlite_connection.cursor()
        cursor.execute("SELECT id FROM characters WHERE name = ?", (self.character_name,))
        character_id = cursor.fetchone()

        if character_id:
            cursor.execute("SELECT bank FROM coins WHERE character_id = ?", (character_id[0],))
            result = cursor.fetchone()
            return result[0] if result else 0
        return 0

# -----------------------
# Damage Calculator Tool
# -----------------------
class DamageCalculator(QDialog):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.charisma_level = 0  # Default charisma level
        self.setWindowTitle("Damage Calculator")
        self.setMinimumWidth(400)

        # Main layout for the dialog
        main_layout = QVBoxLayout()

        # Target BP input
        bp_layout = QHBoxLayout()
        bp_label = QLabel("Target BP:")
        self.bp_input = QLineEdit()
        self.bp_input.setValidator(QIntValidator(0, 100000000))  # Allow only integer input
        bp_layout.addWidget(bp_label)
        bp_layout.addWidget(self.bp_input)
        main_layout.addLayout(bp_layout)

        # Charisma level selection
        charisma_layout = QHBoxLayout()
        charisma_label = QLabel("Charisma Level:")
        self.charisma_dropdown = QComboBox()
        self.charisma_dropdown.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        self.charisma_dropdown.currentIndexChanged.connect(self.update_charisma_level)
        charisma_layout.addWidget(charisma_label)
        charisma_layout.addWidget(self.charisma_dropdown)
        main_layout.addLayout(charisma_layout)

        # Weapons needed display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("Weapons needed will be displayed here.")
        main_layout.addWidget(self.result_display)

        # Total cost display
        self.total_cost_label = QLabel("Total Cost: 0 Coins")
        main_layout.addWidget(self.total_cost_label)

        # Calculate button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_damage)
        main_layout.addWidget(self.calculate_button)

        # Set the layout for the dialog
        self.setLayout(main_layout)

        # Static prices for Discount Magic at different charisma levels
        self.discount_magic_prices = {
            "Vial of Holy Water": [1400, 1357, 1302, 1260],
            "Garlic Spray": [700, 678, 651, 630],
            "Wooden Stake": [2800, 2715, 2604, 2520],
        }

    def update_charisma_level(self):
        # Update charisma level from dropdown selection
        self.charisma_level = self.charisma_dropdown.currentIndex()

    def calculate_damage(self):
        # Clear previous results
        self.result_display.clear()

        try:
            # Get target BP from input
            target_bp = int(self.bp_input.text())
        except ValueError:
            self.result_display.setText("Please enter a valid BP value.")
            return

        if target_bp <= 0:
            self.result_display.setText("BP must be greater than 0.")
            return

        results = []
        total_cost = 0
        remaining_bp = target_bp
        total_hits = 0

        # Load prices for weapons based on charisma level
        vial_cost = self.discount_magic_prices["Vial of Holy Water"][self.charisma_level]
        spray_cost = self.discount_magic_prices["Garlic Spray"][self.charisma_level]
        stake_cost = self.discount_magic_prices["Wooden Stake"][self.charisma_level]

        # Step 1: Calculate the number of Vial of Holy Water hits needed to reduce BP to <= 1350
        vial_hits = 0
        while remaining_bp > 1350:
            damage = math.floor(remaining_bp * 0.6)  # Vial of Holy Water does BP * 0.6 damage
            remaining_bp -= damage
            vial_hits += 1
            total_cost += vial_cost
            total_hits += 1

        if vial_hits > 0:
            results.append(
                f"Discount Magic - Vial of Holy Water - Qty: {vial_hits} - Total Cost: {vial_hits * vial_cost:,} coins")

        # Step 2: Calculate the number of Garlic Spray hits needed to reduce BP to <= 200
        spray_hits = 0
        while remaining_bp > 200:
            remaining_bp -= 75  # Garlic Spray does a fixed average of 75 damage
            spray_hits += 1
            total_cost += spray_cost
            total_hits += 1

        if spray_hits > 0:
            results.append(
                f"Discount Magic - Garlic Spray - Qty: {spray_hits} - Total Cost: {spray_hits * spray_cost:,} coins")

        # Step 3: Use one Wooden Stake if BP <= 200
        if remaining_bp <= 200 and remaining_bp > 0:
            remaining_bp = 0  # Wooden Stake brings BP to 0
            total_cost += stake_cost
            total_hits += 1
            results.append(f"Discount Magic - Wooden Stake - Qty: 1 - Total Cost: {stake_cost:,} coins")

        # Final output for total cost and total hits
        results.append(f"Totals: Hits: {total_hits} Coins: {total_cost:,}")
        self.result_display.setText("\n".join(results))
        self.total_cost_label.setText(f"Total Cost: {total_cost:,} Coins")

# -----------------------
# Powers Reference Tool
# -----------------------
class PowersDialog(QDialog):
    def __init__(self,DB_PATH):
        """
        Initialize the PowersDialog with an SQLite connection using the global DB_PATH.
        """
        super().__init__()
        self.setWindowTitle("Powers Information")
        self.setMinimumSize(600, 400)

        # Establish SQLite connection using the global DB_PATH
        self.db_connection = sqlite3.connect(DB_PATH)

        # Layout setup
        main_layout = QHBoxLayout(self)

        # Left panel: List of powers
        self.powers_list = QListWidget()
        self.powers_list.itemClicked.connect(self.load_power_info)
        main_layout.addWidget(self.powers_list)

        # Right panel: Power details
        self.details_panel = QVBoxLayout()

        # Power name
        self.power_name_label = QLabel("<b>Power:</b>")
        self.details_panel.addWidget(self.power_name_label)

        # Guild
        self.guild_label = QLabel("<b>Guild:</b>")
        self.details_panel.addWidget(self.guild_label)

        # Cost
        self.cost_label = QLabel("<b>Cost:</b>")
        self.details_panel.addWidget(self.cost_label)

        # Quest information
        self.quest_info_text = QTextEdit()
        self.quest_info_text.setReadOnly(True)
        self.details_panel.addWidget(QLabel("<b>Quest Info:</b>"))
        self.details_panel.addWidget(self.quest_info_text)

        # Skill information
        self.skill_info_text = QTextEdit()
        self.skill_info_text.setReadOnly(True)
        self.details_panel.addWidget(QLabel("<b>Skill Info:</b>"))
        self.details_panel.addWidget(self.skill_info_text)

        main_layout.addLayout(self.details_panel)

        # Load all powers into the list
        self.load_powers()

    def load_powers(self):
        """
        Load all powers from the SQLite database and populate the list widget.
        """
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT power_id, name FROM powers ORDER BY name ASC")
            powers = cursor.fetchall()
            cursor.close()

            # Populate the powers list
            for power_id, name in powers:
                self.powers_list.addItem(name)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load powers from the database:\n{e}")

    def load_power_info(self, item):
        """
        Load detailed information for the selected power and display it.

        Args:
            item: The selected QListWidgetItem containing the power's name.
        """
        try:
            power_name = item.text()
            cursor = self.db_connection.cursor()

            # Query for the power's details
            cursor.execute(
                """
                SELECT name, guild, cost, quest_info, skill_info
                FROM powers
                WHERE name = ?
                """, (power_name,)
            )
            power_details = cursor.fetchone()
            cursor.close()

            # Update the UI with the fetched details
            if power_details:
                name, guild, cost, quest_info, skill_info = power_details
                self.power_name_label.setText(f"<b>Power:</b> {name}")
                self.guild_label.setText(f"<b>Guild:</b> {guild}")
                self.cost_label.setText(f"<b>Cost:</b> {cost} coins" if cost else "<b>Cost:</b> Unknown")
                self.quest_info_text.setPlainText(quest_info if quest_info else "None")
                self.skill_info_text.setPlainText(skill_info if skill_info else "None")
            else:
                QMessageBox.warning(self, "Not Found", f"No details found for '{power_name}'.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load power details:\n{e}")

    def closeEvent(self, event):
        """
        Ensure the SQLite database connection is closed when the dialog is closed.
        """
        if self.db_connection:
            self.db_connection.close()
        event.accept()

# -----------------------
# Main Entry Point
# -----------------------
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