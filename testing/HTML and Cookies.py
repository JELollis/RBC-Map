import os
import pickle
import logging
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineCookieStore
from PySide6.QtCore import QUrl

# Path to cookies file
COOKIE_FILE_PATH = 'cookies.pkl'

class CookieTestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cookie Test")
        self.setGeometry(100, 100, 1024, 768)

        # Create a QWebEngineProfile for handling cookies
        self.web_profile = QWebEngineProfile.defaultProfile()

        # Enable persistent cookies and set the storage path
        self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        # Load cookies if available
        self.load_cookies()

        # Set up the webview
        self.webview = QWebEngineView(self)
        self.webview.setUrl(QUrl("https://quiz.ravenblack.net/blood.pl"))
        self.webview.loadFinished.connect(self.on_load_finished)
        self.setCentralWidget(self.webview)

        # Connect the cookie added signal to save the cookie
        cookie_store = self.web_profile.cookieStore()
        cookie_store.cookieAdded.connect(self.on_cookie_added)

    def load_cookies(self):
        """
        Load cookies from a file if available.
        """
        if os.path.exists(COOKIE_FILE_PATH):
            try:
                with open(COOKIE_FILE_PATH, 'rb') as f:
                    cookies_data = pickle.load(f)
                    cookie_store = self.web_profile.cookieStore()
                    for cookie_data in cookies_data:
                        cookie = self.deserialize_cookie(cookie_data)
                        cookie_store.setCookie(cookie, QUrl("https://quiz.ravenblack.net"))
                    logging.info("Cookies loaded from file.")
            except (EOFError, pickle.UnpicklingError):
                logging.warning("Failed to load cookies - file might be empty or corrupt.")
        else:
            logging.info("No cookies file found. Creating a new one.")

    def on_cookie_added(self, cookie):
        """
        Handle the event when a new cookie is added.
        """
        logging.debug(f"Cookie added: {cookie.name().data().decode('utf-8')} = {cookie.value().data().decode('utf-8')}")
        self.save_cookie_to_file(cookie)

    def save_cookie_to_file(self, cookie):
        """
        Save the cookies to a file.
        """
        cookies = []
        if os.path.exists(COOKIE_FILE_PATH):
            try:
                with open(COOKIE_FILE_PATH, 'rb') as f:
                    cookies = pickle.load(f)
            except (EOFError, pickle.UnpicklingError):
                logging.warning("Failed to load existing cookies - creating a new list.")

        cookies.append(self.serialize_cookie(cookie))
        with open(COOKIE_FILE_PATH, 'wb') as f:
            pickle.dump(cookies, f)
            logging.debug("Cookies saved to file.")

    def serialize_cookie(self, cookie):
        """
        Convert a QNetworkCookie to a serializable dictionary.

        Args:
            cookie (QNetworkCookie): The cookie to serialize.

        Returns:
            dict: The serialized cookie data.
        """
        return {
            'name': cookie.name().data().decode('utf-8'),
            'value': cookie.value().data().decode('utf-8'),
            'domain': cookie.domain(),
            'path': cookie.path(),
            'expiry': cookie.expirationDate().toString() if cookie.isSessionCookie() is False else None,
            'secure': cookie.isSecure(),
            'httponly': cookie.isHttpOnly(),
        }

    def deserialize_cookie(self, cookie_data):
        """
        Convert a serialized dictionary back to a QNetworkCookie.

        Args:
            cookie_data (dict): The serialized cookie data.

        Returns:
            QNetworkCookie: The deserialized cookie.
        """
        from PySide6.QtNetwork import QNetworkCookie
        from PySide6.QtCore import QDateTime

        cookie = QNetworkCookie(
            name=cookie_data['name'].encode('utf-8'),
            value=cookie_data['value'].encode('utf-8')
        )
        cookie.setDomain(cookie_data['domain'])
        cookie.setPath(cookie_data['path'])
        if cookie_data['expiry']:
            cookie.setExpirationDate(QDateTime.fromString(cookie_data['expiry']))
        cookie.setSecure(cookie_data['secure'])
        cookie.setHttpOnly(cookie_data['httponly'])

        return cookie

    def on_load_finished(self):
        """
        Handle the webview load finished event.
        """
        logging.info("Webview finished loading.")
        logging.debug("Processing HTML of the loaded page.")
        self.webview.page().toHtml(lambda html: logging.debug("Loaded page content processed."))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting the Cookie Test Application")

    app = QApplication([])
    window = CookieTestApp()
    window.show()
    app.exec()
