import sys
import sqlite3
import datetime
import logging
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtNetwork import QNetworkCookie

# ------------- CONFIG ----------------
CHARACTER_NAME = "Map Thrall 5"
DB_PATH = "../testing/sessions/rbc_map_data.db"
URL = "https://quiz.ravenblack.net/blood.pl"
TARGET_SPAN_TEXT = "Scrollworks"

# ------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ------------- COOKIE UTILITY ----------------
def load_character_cookie(character_name: str) -> str | None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT k.value 
                FROM characters c
                JOIN cookies k ON c.active_cookie = k.id
                WHERE c.name = ?
            """, (character_name,))
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        logging.error(f"Error loading cookie: {e}")
        return None

# ------------- MAIN WINDOW ----------------
class ShopMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shop Monitor")
        self.setGeometry(100, 100, 900, 600)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_shop_status)

        self.init_ui()
        self.load_cookie_and_website()

    def init_ui(self):
        # Left browser view
        self.web_view = QWebEngineView()
        self.web_view.setMinimumWidth(500)
        self.web_view.loadFinished.connect(self.on_page_loaded)

        # Right status layout
        self.status_label = QLabel("Status: Waiting for login...")
        self.current_time_label = QLabel("Current Time:")
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_monitoring)

        status_layout = QVBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.current_time_label)
        status_layout.addWidget(self.result_box)
        status_layout.addWidget(self.start_button)

        # Combine layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.web_view)
        right_panel = QWidget()
        right_panel.setLayout(status_layout)
        main_layout.addWidget(right_panel)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_cookie_and_website(self):
        cookie = load_character_cookie(CHARACTER_NAME)
        if cookie:
            cookie_store = self.web_view.page().profile().cookieStore()
            qt_cookie = QNetworkCookie(b"ip", cookie.encode('utf-8'))
            qt_cookie.setDomain("quiz.ravenblack.net")
            qt_cookie.setPath("/")
            cookie_store.setCookie(qt_cookie, QUrl(URL))
            logging.info("Cookie applied to WebView")
        else:
            self.status_label.setText("Status: Cookie not found.")

        self.web_view.setUrl(QUrl(URL))

    def on_page_loaded(self, success: bool):
        if not success:
            self.status_label.setText("Status: Failed to load page.")
            return

        def evaluate_html(html: str):
            if "name='passwd'" in html or "verify you are not a bot" in html.lower():
                self.status_label.setText("Status: Please complete login manually.")
            else:
                self.status_label.setText("Status: Login complete. Ready to monitor.")
                self.start_button.setEnabled(True)

        self.web_view.page().toHtml(evaluate_html)

    def start_monitoring(self):
        self.status_label.setText("Status: Monitoring started...")
        self.start_button.setEnabled(False)
        self.align_to_next_five_minutes()

    def align_to_next_five_minutes(self):
        now = datetime.datetime.now()
        minute = (now.minute // 5 + 1) * 5
        next_check = now.replace(minute=0 if minute == 60 else minute, second=0, microsecond=0)
        if minute == 60:
            next_check += datetime.timedelta(hours=1)

        delay_ms = int((next_check - now).total_seconds() * 1000)
        QTimer.singleShot(delay_ms, self.check_shop_status)
        logging.info(f"Next check in {delay_ms / 1000:.1f} seconds (at {next_check.strftime('%H:%M:%S')})")


    def check_shop_status(self):
        now = datetime.datetime.now(ZoneInfo("America/New_York"))
        current_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")
        self.current_time_label.setText(f"Current Time: {current_time}")
        logging.info(f"[{current_time}] Refreshing web page...")

        def process_html(html: str):
            soup = BeautifulSoup(html, "html.parser")
            shop_span = soup.find("span", class_="shop")
            if shop_span and shop_span.text.strip().lower() == TARGET_SPAN_TEXT.lower():
                self.status_label.setText("Status: Shop still present.")
                self.result_box.append(f"[{current_time}] ✅ Shop still present.")
                logging.info("Shop still present. Next check scheduled.")
                self.align_to_next_five_minutes()

            else:
                self.status_label.setText("Status: Shop moved!")
                self.result_box.append(f"[{current_time}] ❌ Shop moved!")
                logging.info("Shop moved — stopping timer and writing file.")
                with open("../testing/shop_move_timestamp.txt", "w") as f:
                    f.write(current_time)
                self.timer.stop()

        self.web_view.reload()
        self.web_view.page().toHtml(self.process_html)

# ------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShopMonitorApp()
    window.show()
    sys.exit(app.exec())