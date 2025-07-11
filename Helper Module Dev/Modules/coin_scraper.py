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
class CoinScraper:
    def __init__(self, character_name, character_id, web_profile):
        """
        Initialize the CoinScraper with the given character name, character ID, and web profile.

        Args:
            character_name (str): The name of the character for whom to scrape the coin count.
            character_id (int): The unique ID of the character for database updates.
            web_profile (QWebEngineProfile): The web profile to use for maintaining session data.
        """
        logging.debug("Initializing CoinScraper.")
        self.character_name = character_name
        self.character_id = character_id
        self.web_profile = web_profile
        self.website_frame = QWebEngineView(self.web_profile)

        # Start scraping process with periodic checks
        self.check_coin_count()

    def check_coin_count(self):
        """
        Periodically scrape the page for the coin count by loading the relevant page.
        """
        coin_url = "https://quiz.ravenblack.net/blood.pl?action=viewvamp"
        self.website_frame.setUrl(QUrl(coin_url))
        self.website_frame.loadFinished.connect(self.on_page_loaded)

    def on_page_loaded(self):
        """
        Handle page load completion and trigger HTML processing.
        """
        logging.debug("Page loaded. Processing HTML for coin count.")
        self.website_frame.page().toHtml(self.extract_coins_from_html)

    def extract_coins_from_html(self, html):
        """
        Extract bank coins, pocket coins, and handle coin-related actions from the HTML content.
        Updates both bank and pocket coins in the database for the current character.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Search for the bank balance line
            bank_match = re.search(r"Welcome to Omnibank. Your account has (\d+) coins in it.", html)
            if bank_match:
                bank_coins = int(bank_match.group(1))
                logging.info(f"Bank coins found: {bank_coins}")
                cursor.execute('''
                    UPDATE coins
                    SET bank = ?
                    WHERE character_id = ?
                ''', (bank_coins, self.character_id))

            # Search for pocket coin amounts
            pocket_match = re.search(r"Money: (one|\d+) coins|You have (one|\d+) coins", html, re.IGNORECASE)
            if pocket_match:
                pocket_coins_text = pocket_match.group(1) or pocket_match.group(2)
                pocket_coins = 1 if pocket_coins_text.lower() == "one" else int(pocket_coins_text)
                logging.info(f"Pocket coins found: {pocket_coins}")
                cursor.execute('''
                    UPDATE coins
                    SET pocket = ?
                    WHERE character_id = ?
                ''', (pocket_coins, self.character_id))

            # Define actions for additional coin changes
            actions = {
                'deposit': r"You deposit (\d+) coins.",
                'withdraw': r"You withdraw (\d+) coins.",
                'transit': r"It costs 5 coins to ride. You have (\d+).",
                'hunter': r"You drink the hunter\'s blood.*You also found (\d+) coins",
                'paladin': r"You drink the paladin\'s blood.*You also found (\d+) coins",
                'human': r"You drink the human\'s blood.*You also found (\d+) coins",
                'bag_of_coins': r'The bag contained (\d+) coins',
                'robbing': r'You stole (\d+) coins from (\w+)',
                'silver_suitcase': r'The suitcase contained (\d+) coins',
                'given_coins': r'(\w+) gave you (\d+) coins',
                'getting_robbed': r'(\w+) stole (\d+) coins from you'
            }

            # Process each action pattern and update coins as needed
            for action, pattern in actions.items():
                match = re.search(pattern, html)
                if match:
                    coin_count = int(match.group(1))

                    if action == 'deposit':
                        # Deposit reduces pocket coins
                        cursor.execute('''
                            UPDATE coins
                            SET pocket = pocket - ?
                            WHERE character_id = ?
                        ''', (coin_count, self.character_id))
                        logging.info(f"Deposit action: -{coin_count} coins to pocket.")

                    elif action == 'withdraw':
                        # Withdraw increases pocket coins
                        cursor.execute('''
                            UPDATE coins
                            SET pocket = pocket + ?
                            WHERE character_id = ?
                        ''', (coin_count, self.character_id))
                        logging.info(f"Withdraw action: +{coin_count} coins to pocket.")

                    elif action == 'transit':
                        # Set pocket coins after transit
                        coins_in_pocket = int(match.group(1))
                        cursor.execute('''
                            UPDATE coins
                            SET pocket = ?
                            WHERE character_id = ?
                        ''', (coins_in_pocket, self.character_id))
                        logging.info(f"Transit action: Pocket coins set to {coins_in_pocket}.")

                    elif action == 'getting_robbed':
                        # Losing coins when robbed
                        cursor.execute('''
                            UPDATE coins
                            SET pocket = pocket - ?
                            WHERE character_id = ?
                        ''', (coin_count, self.character_id))
                        logging.info(f"Getting robbed: -{coin_count} coins from pocket.")

                    else:
                        # Gaining coins (from hunting, robbing, receiving, etc.)
                        cursor.execute('''
                            UPDATE coins
                            SET pocket = pocket + ?
                            WHERE character_id = ?
                        ''', (coin_count, self.character_id))
                        logging.info(f"Gained {coin_count} coins from action: {action}.")
                    break  # Exit loop after first match to avoid multiple updates from one HTML pass

            connection.commit()
            logging.info(f"Updated coins for character ID {self.character_id}.")

        except Exception as e:
            logging.error(f"Failed to update coins from HTML: {e}")

        finally:
            connection.close()
