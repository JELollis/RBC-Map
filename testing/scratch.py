import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


class MessageEditorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compose Private Message")
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        # Recipient
        self.recipient_input = QLineEdit()
        layout.addWidget(QLabel("Recipient:"))
        layout.addWidget(self.recipient_input)

        # Subject
        self.subject_input = QLineEdit()
        layout.addWidget(QLabel("Subject:"))
        layout.addWidget(self.subject_input)

        # Message Body
        self.body_input = QTextEdit()
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.body_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_send)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Hidden browser for JavaScript injection
        self.web = QWebEngineView(self)
        self.web.hide()
        self.web.load(QUrl("https://lollis-home.ddns.net/messages.php?msg_send=0"))

    def handle_send(self):
        recipient = self.recipient_input.text().strip()
        subject = self.subject_input.text().strip()
        message = self.body_input.toPlainText().strip()

        if not recipient or not subject or not message:
            QMessageBox.warning(self, "Missing Fields", "All fields are required.")
            return

        js = f"""
        (function() {{
            const log = console.log;

            try {{
                log("Injecting recipient...");
                document.querySelector("#msg_send").value = `{recipient}`;

                log("Injecting subject...");
                document.querySelector("input[name='subject']").value = `{subject}`;

                log("Injecting message...");
                document.querySelector("textarea[name='message']").value = `{message}`;

                log("Clicking send...");
                document.querySelector("input[name='send_message']").click();
            }} catch (e) {{
                log("Injection error:", e);
            }}
        }})();
        """

        def inject():
            print("[INFO] Injecting JavaScript into PM form...")
            self.web.page().runJavaScript(js)
            QMessageBox.information(self, "Attempted", "JS injection sent — check if message arrived.")
            self.accept()

        self.web.page().loadFinished.connect(
            lambda ok: inject() if ok else QMessageBox.critical(self, "Error", "Failed to load PM form."))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = MessageEditorDialog()
    dlg.exec()
