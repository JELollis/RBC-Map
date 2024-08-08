#!/usr/bin/python3
#Filename main 0.3.3.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pickle
import os

from variables import *

class CityMapApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        # Initialize minimap parameters
        self.zoom_level = 3  # Default zoom level
        self.minimap_size = 280  # Size of the minimap
        self.column_start = 0
        self.row_start = 0

        # Create the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left side layout
        left_layout = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Box)
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left_layout)

        # Create the minimap area
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        minimap_frame.setLayout(minimap_layout)

        # Add minimap
        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Combo boxes and Go button layout
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_columns.addItems(columns.keys())  # Populate with column names

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_rows.addItems(rows.keys())  # Populate with row names

        go_button = QPushButton('Go')
        go_button.setFixedSize(50, 30)
        go_button.clicked.connect(self.go_to_location)  # Connect to go_to_location method

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        # Zoom and set destination buttons
        zoom_layout = QHBoxLayout()
        button_size = (self.minimap_size - 10) // 3  # Adjusted size to fit in the row with padding

        zoom_in_button = QPushButton('Zoom in')
        zoom_in_button.setFixedSize(button_size, 40)
        zoom_in_button.clicked.connect(self.zoom_in)  # Connect to zoom_in method
        zoom_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton('Zoom out')
        zoom_out_button.setFixedSize(button_size, 40)
        zoom_out_button.clicked.connect(self.zoom_out)  # Connect to zoom_out method
        zoom_layout.addWidget(zoom_out_button)

        set_destination_button = QPushButton('Set Destination')
        set_destination_button.setFixedSize(button_size, 40)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        # Closest locations buttons
        closest_buttons_layout = QHBoxLayout()

        btn1 = QPushButton('1st Closest\nLocations')
        btn1.setFixedSize(button_size, 40)
        btn1.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn1)

        btn2 = QPushButton('2nd Closest\nLocations')
        btn2.setFixedSize(button_size, 40)
        btn2.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn2)

        btn3 = QPushButton('3rd Closest\nLocations')
        btn3.setFixedSize(button_size, 40)
        btn3.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn3)

        left_layout.addLayout(closest_buttons_layout)

        # Refresh, Discord, and Website buttons
        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 40)
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 40)
        action_layout.addWidget(discord_button)

        website_button = QPushButton('Website')
        website_button.setFixedSize(button_size, 40)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        # Character list frame
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        # Placeholder for character list and buttons
        character_list = QLabel()
        character_layout.addWidget(character_list)

        character_buttons_layout = QHBoxLayout()
        new_button = QPushButton('New')
        modify_button = QPushButton('Modify')
        delete_button = QPushButton('Delete')
        character_buttons_layout.addWidget(new_button)
        character_buttons_layout.addWidget(modify_button)
        character_buttons_layout.addWidget(delete_button)
        character_layout.addLayout(character_buttons_layout)

        left_layout.addWidget(character_frame)

        main_layout.addWidget(left_frame)

        # Add the website frame on the right
        self.website_frame = QWebEngineView()
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        main_layout.addWidget(self.website_frame)

        self.show()

        # Initial minimap update
        self.update_minimap()

    def draw_minimap(self):
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

        def determine_color(column_index, row_index):
            if column_index < min(columns.values()) or column_index > max(columns.values()) or row_index < min(
                    rows.values()) or row_index > max(rows.values()):
                return color_map["edge"]
            elif (column_index % 2 == 1) or (row_index % 2 == 1):
                return color_map["alley"]
            else:
                if (column_index, row_index) in banks_coordinates:
                    return color_map["bank"]
                elif (column_index, row_index) in pubs_coordinates:
                    return color_map["pub"]
                elif (column_index, row_index) in transits_coordinates:
                    return color_map["transit"]
                elif (column_index, row_index) in user_buildings_coordinates.values():
                    return QColor("purple")
                return color_map["default"]

        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                x0, y0 = j * block_size, i * block_size

                column_index = self.column_start + j
                row_index = self.row_start + i

                # Draw border around each cell
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                color = determine_color(column_index, row_index)

                painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                 block_size - 2 * border_size, color)

                # Draw labels only at intersections of named streets or for user buildings
                column_name = next((name for name, coord in columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in rows.items() if coord == row_index), None)
                if column_name and row_name:
                    location = (column_index, row_index)
                    if location in user_buildings_coordinates.values():
                        label_text = next(
                            name for name, coord in user_buildings_coordinates.items() if coord == location)
                    else:
                        label_text = f"{column_name} & {row_name}"

                    text_rect = font_metrics.boundingRect(label_text)
                    text_x = x0 + (block_size - text_rect.width()) // 2
                    text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()

                    painter.setPen(QColor('white'))
                    painter.drawText(text_x, text_y, label_text)

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        self.draw_minimap()

    def zoom_in(self):
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_minimap()

    def zoom_out(self):
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.update_minimap()

    def go_to_location(self):
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()
        if column_name in columns:
            self.column_start = columns[column_name]
        if row_name in rows:
            self.row_start = rows[row_name]
        self.update_minimap()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()

        if x < self.minimap_size and y < self.minimap_size:
            block_size = self.minimap_size // self.zoom_level
            col_clicked = x // block_size
            row_clicked = y // block_size

            new_column_start = self.column_start + col_clicked - self.zoom_level // 2
            new_row_start = self.row_start + row_clicked - self.zoom_level // 2

            # Ensure the new start positions are within the valid range
            if -1 <= new_column_start <= 201 - self.zoom_level + 1:
                self.column_start = new_column_start
            if -1 <= new_row_start <= 201 - self.zoom_level + 1:
                self.row_start = new_row_start

            self.update_minimap()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec_())
