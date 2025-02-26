### Changelog for RBC City Map Application

#### Version 0.10.0
- **General Enhancements**:
  - **Version Display**: Updated `show_about_dialog` to display `version_number` (0.10.0) for better version tracking.
  - **Documentation**: Refactored docstrings with detailed class and function descriptions for open-source clarity.
- **Minimap Features**:
  - Enhanced `draw_minimap` with grid-based rendering and refined location offsets (e.g., +1,+1 for banks).
  - Added support for clicking the minimap to recenter on any location.
- **Tools Integration**:
  - Fully integrated shopping list, damage calculator, and powers reference into the workflow.
  - Shopping list now displays pocket and bank coins alongside the total cost.
  - Damage calculator uses static pricing from Discount Magic with charisma adjustments.
- **Database Enhancements**:
  - Transitioned fully to **SQLite**, removing MySQL dependencies.
  - Added tables for `shop_items`, `powers`, and `recent_destinations` with initial data.
- **Webview Improvements**:
  - Improved `extract_coins_from_html` to handle additional in-game actions (e.g., robbing, receiving coins).
- **Theme Customization**:
  - Extended to include minimap-specific colors (e.g., set_destination, transit routes).
- **Bug Fixes**:
  - Fixed overlap issues in minimap labels at high zoom levels.
  - Resolved rare crashes during character switching.

#### Version 0.9.1
- **Bug Fixes & Performance**:
  - Optimized database queries to improve SQLite efficiency.
  - Fixed an issue with minimap display not updating correctly after setting destinations.

#### Version 0.9.0
- **Major UI Enhancements**:
  - Implemented a dynamic minimap with **zoom functionality** and improved edge-case handling.
  - Introduced **theme customization options**, allowing users to personalize the application’s appearance.
- **Database Overhaul**:
  - Began transition from **MySQL to SQLite**, improving local storage capabilities.
- **Tools Additions**:
  - Added **Shopping List Tool** to manage in-game purchases.
  - Introduced **Damage Calculator** for calculating attack strategies.
  - Implemented **Powers Reference Tool** for tracking abilities and guild locations.

#### Version 0.8.1
- **Stability Fixes**:
  - Resolved UI lag issues when switching between different tool windows.
  - Improved integration between shopping list and in-game inventory.

#### Version 0.8.0
- **Database Migration**:
  - Initial implementation of **SQLite-based storage**.
- **Web Scraping**:
  - Improved integration with `A View in the Dark`, enhancing the extraction of in-game data.
- **UI Refinements**:
  - Added a **tabbed interface** for managing different tools.

#### Version 0.7.3
- **Bug Fixes & Minimap Improvements**:
  - Fixed inconsistencies with the coordinate tracking system.
  - Improved rendering speed for large maps.

#### Version 0.7.2
- **Performance Enhancements**:
  - Optimized web scraping methods to reduce redundant requests.
  - Fixed a minor memory leak related to character switching.

#### Version 0.7.1
- **Minor UI Fixes**:
  - Adjusted button placements for better usability.
  - Fixed an issue with color theme application not persisting after restart.

#### Version 0.7.0
- **Major Feature Additions**:
  - Implemented **multi-character management**, allowing users to switch between stored accounts.
  - Added **in-game currency tracking**, displaying pocket and bank balances.
- **Minimap Enhancements**:
  - Improved **grid-based rendering**, adding distinct markers for important locations.

#### Version 0.6.3
- **Database Improvements**:
  - Fixed transaction handling in SQLite to prevent data loss on crash.
  - Minor UI adjustments for database viewer.

#### Version 0.6.2
- **Bug Fixes & UI Enhancements**:
  - Fixed incorrect bank balances displaying in shopping list.
  - Improved responsiveness of damage calculator.

#### Version 0.6.1
- **Feature Tweaks**:
  - Adjusted in-game coordinate tracking for better accuracy.
  - Fixed an issue with some tooltips not displaying correctly.

#### Version 0.6.0
- **Core Functionality Expansion**:
  - Improved handling of **coordinate extraction** from in-game HTML.
  - Introduced **basic guild and shop tracking**.
- **Bug Fixes**:
  - Addressed **UI inconsistencies** in the destination selection menu.

#### Version 0.5.4
- **Patch Release**:
  - Fixed a crashing issue when setting multiple destinations quickly.
  - Improved data persistence between sessions.

#### Version 0.5.0
- **Single-File Transition**:
  - **Removed `variables.py`**, consolidating all constants and settings into `main.py`.
- **First Implementation of Tools**:
  - Basic versions of **shopping list**, **damage calculator**, and **powers reference** introduced.

#### Version 0.4.0
- **Minimap Introduction**:
  - Added **basic minimap functionality** displaying character position and nearby locations.
  - **Color-coded paths** added for banks, taverns, and transit stations.
- **Web Scraping Enhancements**:
  - Improved ability to **fetch and store game data** dynamically.

#### Version 0.3.0
- **PyQt5 Transition**:
  - Migrated UI framework from **Tkinter to PyQt5**, significantly improving design and responsiveness.
- **Basic Data Scraping**:
  - Introduced **BeautifulSoup for extracting character coordinates** from game pages.

#### Version 0.2.0
- **WebView Integration**:
  - Implemented **QtWebEngine** to allow in-game browsing and real-time interactions.
- **Database Expansion**:
  - Added **MySQL support** for storing character and game data.

#### Version 0.1.0
- **Initial Release**:
  - Basic application framework created.
  - Implemented **manual coordinate entry and character tracking**.

