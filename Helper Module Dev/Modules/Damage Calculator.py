import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QTextEdit, QMessageBox
# Copyright 2024 RBC Community Map Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class DamageCalculator:
    def __init__(self, initial_bp):
        self.initial_bp = initial_bp

    def calculate_damage(self, bp):
        """
        Calculate the damage dealt by a hit based on current blood points (BP).
        """
        return math.floor(bp ** 0.6)

    def calculate_hits_to_zero(self):
        """
        Calculate the number of hits required to reduce the initial BP to zero.
        The function uses HW when BP is 1275 or higher, and GS when BP is below 1275.
        """
        current_bp = self.initial_bp
        hits = 0
        hw_hits = 0
        gs_hits = 0
        log = []

        while current_bp > 0:
            if current_bp >= 1275:
                damage = self.calculate_damage(current_bp)
                hw_hits += 1
                hit_type = "HW"
            else:
                damage = self.calculate_damage(current_bp)
                gs_hits += 1
                hit_type = "GS"
            current_bp -= damage
            hits += 1

            # Log the hit information
            log.append(f"Hit {hits}: {hit_type} | Damage = {damage}, BP after hit = {current_bp}")

            # Ensure BP doesn't go negative
            if current_bp <= 0 or damage == 0:
                current_bp = 0
                break

        return hits, hw_hits, gs_hits, log

class DamageCalculatorUI(QMainWindow):
    def __init__(self, shopping_list_generator):
        super().__init__()

        self.shopping_list_generator = shopping_list_generator  # Reference to shopping list generator
        self.setWindowTitle("Damage Calculator")
        self.setGeometry(100, 100, 400, 300)

        # Create the input field for initial BP
        self.input_label = QLabel("Enter Initial BP:", self)
        self.input_field = QLineEdit(self)

        # Create the calculate button
        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.clicked.connect(self.calculate_damage)

        # Create the output text area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)

        # Create the send to shopping list button
        self.send_button = QPushButton("Send to Shopping List", self)
        self.send_button.clicked.connect(self.send_to_shopping_list)
        self.send_button.setEnabled(False)  # Disable until calculation is done

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.calculate_button)
        layout.addWidget(self.output_area)
        layout.addWidget(self.send_button)

        # Set the central widget and layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Store HW and GS hits
        self.hw_hits = 0
        self.gs_hits = 0

    def calculate_damage(self):
        # Get the initial BP from the input field
        try:
            initial_bp = int(self.input_field.text())
        except ValueError:
            messagebox = QMessageBox()
            messagebox.critical(self, "Input Error", "Please enter a valid integer for BP.")
            return

        # Initialize the DamageCalculator with the input BP
        calculator = DamageCalculator(initial_bp)
        total_hits, hw_hits, gs_hits, log = calculator.calculate_hits_to_zero()

        # Store HW and GS hits for later use
        self.hw_hits = hw_hits
        self.gs_hits = gs_hits

        # Display the results
        result_text = f"Total hits to bring {initial_bp} BP to zero: {total_hits}\n"
        result_text += f"Holy Water hits: {hw_hits}\n"
        result_text += f"Garlic Spray hits: {gs_hits}\n\n"
        result_text += "Hit Details:\n" + "\n".join(log)

        self.output_area.setText(result_text)

        # Enable the send button
        self.send_button.setEnabled(True)

    def send_to_shopping_list(self):
        """
        Send the HW and GS hits to the shopping list generator.
        """
        if self.hw_hits > 0 or self.gs_hits > 0:
            self.shopping_list_generator.add_items(hw_count=self.hw_hits, gs_count=self.gs_hits)
            QMessageBox.information(self, "Success", "Items added to shopping list.")
        else:
            QMessageBox.warning(self, "Warning", "No hits to send to shopping list.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DamageCalculatorUI()
    window.show()
    sys.exit(app.exec())