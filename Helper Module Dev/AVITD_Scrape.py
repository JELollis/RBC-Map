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
import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QTextEdit
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

class AVITDScraper:
    def __init__(self):
        self.url = "https://aviewinthedark.net/"

    def scrape_guilds_and_shops(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        guilds = self.scrape_section(soup, "the guilds")
        shops = self.scrape_section(soup, "the shops")
        guilds_next_update = self.extract_next_update_time(soup, 'Guilds')
        shops_next_update = self.extract_next_update_time(soup, 'Shops')

        return guilds, shops, guilds_next_update, shops_next_update

    def scrape_section(self, soup, section_image_alt):
        data = []

        section_image = soup.find('img', alt=section_image_alt)
        if not section_image:
            print(f"No data found for {section_image_alt}.")
            return data

        table = section_image.find_next('table')
        rows = table.find_all('tr', class_=['odd', 'even'])

        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 2:
                continue

            name = columns[0].text.strip()
            location = columns[1].text.strip()

            location = location.replace("SE of ", "").strip()

            try:
                column, row = location.split(" and ")
                data.append((name, column, row))
            except ValueError:
                print(f"Location format unexpected for {name}: {location}")

        return data

    def extract_next_update_time(self, soup, section_name):
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
                    return next_update.strftime('%Y-%m-%d %H:%M:%S')
        return 'NA'

class ScraperApp(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('AVITD Scraper')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.log_widget = QTextEdit(self)
        self.log_widget.setReadOnly(True)
        self.layout.addWidget(self.log_widget)

        self.scrape_button = QPushButton('Scrape AVITD Data', self)
        self.scrape_button.clicked.connect(self.scrape_data)
        self.layout.addWidget(self.scrape_button)

        self.setLayout(self.layout)

        self.scraper = AVITDScraper()

    def scrape_data(self):
        guilds, shops, guilds_next_update, shops_next_update = self.scraper.scrape_guilds_and_shops()

        self.log_widget.append(f"Guilds Next Update: {guilds_next_update}")
        self.log_widget.append(f"Shops Next Update: {shops_next_update}")

        results = "\nGuilds Data:\n"
        for guild in guilds:
            results += f"Name: {guild[0]}, Column: {guild[1]}, Row: {guild[2]}\n"

        results += "\nShops Data:\n"
        for shop in shops:
            results += f"Name: {shop[0]}, Column: {shop[1]}, Row: {shop[2]}\n"

        self.log_widget.append(results)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = ScraperApp()
    dialog.show()
    sys.exit(app.exec())
