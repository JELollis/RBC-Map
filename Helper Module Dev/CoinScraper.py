# -----------------------
# Imports Handling
# -----------------------
import importlib.util
import sys

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
        print(f"pip install {' '.join(missing_modules)}")
        return False
    return True

# Check for required modules
if not check_required_modules(required_modules):
    sys.exit("Missing required modules. Please install them and try again.")

# Proceed with the rest of the imports and program setup
import logging
import pickle
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import QUrl, Qt, QTimer, QDateTime
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtNetwork import QNetworkCookie
import sqlite3

# Constants
COOKIE_DB_PATH = './sessions/cookies.db'
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


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
            logging.warning(f"Module {module} is missing.")

    if missing_modules:
        logging.error("Some required modules are missing.")
        print("The following modules are missing:")
        for mod in missing_modules:
            print(f"- {mod}")
        print("\nYou can install them with:")
        print(f"pip install {' '.join(missing_modules)}")
        return False

    logging.info("All required modules are present.")
    return True


# List of required modules
required_modules = [
    'pickle', 'pymysql', 'requests', 're', 'time', 'sqlite3',
    'webbrowser', 'datetime', 'bs4', 'PySide6.QtWidgets',
    'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtNetwork'
]

# Check for required modules
if not check_required_modules(required_modules):
    sys.exit("Missing required modules. Please install them and try again.")

class CoinScraper(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Initializing ScraperApp.")
        self.setWindowTitle("Vampire Coin Scraper")
        self.setGeometry(100, 100, 800, 600)

        self.selected_character = None
        self.characters = []
        self.is_signal_connected = False

        self.web_profile = QWebEngineProfile.defaultProfile()
        self.initUI()
        self.setup_cookie_handling()

    def initUI(self):
        logging.debug("Setting up UI.")
        self.label = QLabel("Initializing...", self)
        self.label.setStyleSheet("font-size: 16px;")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.website_frame = QWebEngineView()
        layout.addWidget(self.website_frame)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Start the scraping process after UI setup
        logging.debug("UI setup complete. Starting the scraping process.")
        QTimer.singleShot(1000, self.load_characters)

    # -----------------------
    # SQLite Cookie Storage Setup
    # -----------------------

    COOKIE_DB_PATH = './testing/sessions/cookies.db'  # Path to the SQLite database for storing cookies

    def initialize_cookie_db(self):
        """
        Initialize the SQLite database for storing cookies.

        This function creates a table named 'cookies' in the SQLite database if it doesn't already exist.
        The table is used to store cookie details such as name, value, domain, path, expiry, secure, and httponly flags.
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

    def save_cookie_to_db(self, cookie):
        """
        Save a single cookie to the SQLite database.

        Args:
            cookie (QNetworkCookie): The QNetworkCookie object representing the cookie to save.

        This function inserts the cookie's details into the 'cookies' table in the SQLite database.
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

    def load_cookies_from_db(self):
        """
        Load all cookies from the SQLite database.

        Returns:
            list: A list of QNetworkCookie objects representing the cookies stored in the database.

        This function retrieves all cookies from the 'cookies' table in the SQLite database
        and converts them into QNetworkCookie objects.
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

    def clear_cookie_db(self):
        """
        Clear all cookies from the SQLite database.

        This function deletes all records from the 'cookies' table, effectively clearing all stored cookies.
        """
        connection = sqlite3.connect(COOKIE_DB_PATH)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM cookies')
        connection.commit()
        connection.close()

    # -----------------------
    # Cookie Handling
    # -----------------------

    def setup_cookie_handling(self):
        """
        Set up cookie handling, including loading and saving cookies.

        This method initializes the SQLite database for cookies, connects the QWebEngineProfile's cookie store
        to the application, and loads previously saved cookies from the database.
        """
        self.initialize_cookie_db()
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        self.load_cookies()

    def load_cookies(self):
        """
        Load cookies from the SQLite database.

        This method retrieves cookies from the SQLite database and injects them into the web engine's cookie store.
        """
        cookies = self.load_cookies_from_db()
        for cookie in cookies:
            self.cookie_store.setCookie(cookie, QUrl("https://quiz.ravenblack.net"))
        logging.info("Cookies loaded from SQLite database.")

    def on_cookie_added(self, cookie):
        """
        Handle the event when a new cookie is added, ensuring no duplicates are stored.

        Args:
            cookie (QNetworkCookie): The newly added cookie.

        This method checks if the cookie already exists in the database and saves it if it's new.
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
            self.save_cookie_to_db(cookie)
            logging.debug(
                f"Cookie added: {cookie.name().data().decode('utf-8')} = {cookie.value().data().decode('utf-8')}")
        else:
            logging.debug(
                f"Duplicate cookie ignored: {cookie.name().data().decode('utf-8')} = {cookie.value().data().decode('utf-8')}")

        connection.close()

    # -----------------------
    # Character Management
    # -----------------------

    def load_characters(self):
        """
        Load characters from a pickle file in the 'sessions' directory.
        """
        logging.debug("Loading characters from sessions/characters.pkl.")
        try:
            with open('./sessions/characters.pkl', 'rb') as f:
                self.characters = pickle.load(f)
                if self.characters:
                    self.selected_character = self.characters[0]  # Use the first character for this test
                    self.label.setText(f"Character {self.selected_character['name']} selected.")
                    logging.debug(f"Character {self.selected_character['name']} selected.")
                    QTimer.singleShot(1000, self.logout_current_character)
                else:
                    self.label.setText("No characters found.")
                    logging.warning("No characters found in the characters.pkl file.")
        except FileNotFoundError:
            self.label.setText("Characters file not found.")
            logging.error("characters.pkl file not found.")
        except Exception as e:
            self.label.setText(f"Error loading characters: {e}")
            logging.error(f"Error loading characters: {e}")

    def logout_current_character(self):
        """
        Logout the current character by navigating to the logout URL.
        """
        logging.debug("Logging out current character.")
        self.label.setText("Logging out current character...")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))

        # Delay login to allow logout to complete
        QTimer.singleShot(1000, self.login_selected_character)

    def login_selected_character(self):
        """
        Log in the selected character after logging out the current one.
        """
        if not self.selected_character:
            self.label.setText("No character selected for login.")
            logging.warning("No character selected for login.")
            return

        self.label.setText(f"Logging in character: {self.selected_character['name']}")
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

        if not self.is_signal_connected:
            logging.debug("Connecting loadFinished signal to on_login_finished.")
            self.website_frame.loadFinished.connect(self.on_login_finished)
            self.is_signal_connected = True

        logging.debug("Executing login JavaScript.")
        self.website_frame.page().runJavaScript(login_script)

    def on_login_finished(self):
        """
        Triggered when the login process is finished. Navigate to the scrape page.
        """
        logging.debug("Login finished. Navigating to coin page.")
        self.label.setText("Navigating to coin page...")
        coin_url = "https://quiz.ravenblack.net/blood.pl?action=viewvamp"
        self.website_frame.setUrl(QUrl(coin_url))

        # Ensure that the loadFinished signal is connected only once
        if self.is_signal_connected:
            self.website_frame.loadFinished.disconnect(self.on_login_finished)
            self.website_frame.loadFinished.connect(self.scrape_coin_count)
            self.is_signal_connected = False

    def scrape_coin_count(self):
        """
        Scrape the page for the coin count.
        """
        logging.debug("Scraping the page for coin count.")
        self.label.setText("Scraping for coins...")
        self.website_frame.page().toHtml(self.process_html)

    def process_html(self, html):
        """
        Process the HTML content of the page to find the coin count.
        """
        logging.debug("Processing HTML content for coin count.")
        soup = BeautifulSoup(html, 'html.parser')
        money_line = soup.find(string=lambda text: text and "Money:" in text)

        if money_line:
            coins = money_line.split("Money: ")[1].split(" ")[0]
            self.label.setText(f"You have {coins} coins.")
            logging.debug(f"Found coin count: {coins}")
            # Disconnect the loadFinished signal to prevent further loading
            self.website_frame.loadFinished.disconnect(self.scrape_coin_count)
        else:
            self.label.setText("Could not find the coins information.")
            logging.warning("Could not find the coins information in the HTML.")


if __name__ == "__main__":
    logging.debug("Starting ScraperApp.")
    app = QApplication(sys.argv)
    scraper = CoinScraper()
    scraper.show()
    sys.exit(app.exec())
