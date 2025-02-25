### Changelog for RBC City Map Application

#### Version 0.1.0
- **Initial Release**: Basic implementation of the RBC City Map Application.
  - Display a minimap with zooming capability.
  - Integration with a web view to extract coordinates from a webpage.
  - Display nearest locations like pubs, banks, and transits.
  - Option to set and save destination.

#### Version 0.2.0
- **Data Loading**: Connect to a MySQL database to fetch city map data.
  - Load columns, rows, banks, taverns, transits, and user buildings from the database.

#### Version 0.3.0
- **Minimap Enhancements**: Improved the minimap display.
  - Added color coding for different types of locations.
  - Display labels at intersections of named streets.
  - Implemented mouse click navigation on the minimap.

#### Version 0.4.0
- **Web Integration**: Enhanced web view integration.
  - Improved extraction of coordinates from the web page.
  - Added support for refreshing the web view content.
  - Better handling of edge cases and errors during coordinate extraction.

#### Version 0.4.1
- **Zoom and Destination Features**: Enhanced zooming and destination setting functionality.
  - Refined zoom in and zoom out capabilities.
  - Improved the set destination feature with better handling and visual feedback.

#### Version 0.4.2
- **User Interface Improvements**: Enhanced the user interface.
  - Added character list and management buttons.
  - Improved the layout of control buttons for better usability.
  - Updated styles for better visual clarity.

#### Version 0.4.3
- **Minor Fixes and Updates**: Bug fixes and minor improvements.
  - Fixed issues with coordinate extraction and display.
  - Improved error handling and user feedback.

#### Version 0.5.0
- **Database Enhancements**: Improved data loading and integration.
  - Added support for loading shops and guilds data from the database.
  - Implemented initial scraping of guilds and shops data from "A View in the Dark".

#### Version 0.5.1
- **Location Tracking and Display**: Enhanced location tracking on the minimap.
  - Added features to draw lines to nearest locations like taverns, banks, and transits.
  - Improved display of special locations on the minimap.

#### Version 0.5.2
- **Data Scraping and Updating**: Implemented scraping and updating of guilds and shops data.
  - Functions to scrape data from "A View in the Dark" and update the database.
  - Extract next update times and calculate timestamps.
  - Update individual guild and shop entries in the database.

#### Version 0.5.3
- **Coordinate Handling**: Improved coordinate handling for precise location tracking.
  - Enhanced methods to extract and process coordinates from the web page.
  - Better handling of intersections and precise coordinates.

#### Version 0.5.4
- **Automated Updates**: Automated scraping and updating of guilds and shops.
  - Retrieve and update next update times for guilds and shops.
  - Conditional scraping based on the current time and next update times.
  - Improved data synchronization with the database.

#### Version 0.6.0
- **User Interface and Data Visualization**: Major UI and data visualization improvements.
  - Added information frame to display closest locations and AP costs.
  - Visual enhancements for better readability and user interaction.
  - Additional buttons and controls for improved navigation and usability.
  - Updated labels and display for nearest locations and set destination.

#### Version 0.6.1
- **Character Management**: Added character management features.
  - Implemented the ability to add, modify, and delete characters.
  - Integrated character data loading and saving using pickle files.
  - Enhanced the user interface to support character management.
- **Additional Data Integration**: Added places of interest to the map.
  - Integrated places of interest data into the minimap and database.
  - Updated minimap drawing function to include places of interest.
- **Distance Calculation**: Improved AP cost calculation using Chebyshev distance.
  - Enhanced distance calculations for more accurate AP costs.
  - Updated information frame to display AP costs for nearest locations and destinations.

#### Version 0.6.2
- **Improved Import Handling**: Added better handling for module imports with an automated installation option for missing dependencies.
- **Database Connection**: Enhanced the logic for connecting to both local and remote MySQL databases with fallback mechanisms.
- **Error Handling**: Implemented more robust error handling during the initialization phase.

#### Version 0.6.3
- **Character Management**: Added features to manage characters, including adding, modifying, and deleting characters. The character data is now stored using `pickle`.
- **UI Enhancements**: Updated the UI to include a character list and management buttons, with a new feature to select characters from a list and log in automatically.
- **Website Button**: Added a button for future website integration, with a "Coming Soon" popup for now.

#### Version 0.7.0
- **Theme Customization**: Introduced a new feature for customizing the application theme, including saving and loading theme settings.
- **Database Viewer**: Added a database viewer utility for viewing and managing data tables directly within the application.
- **Enhanced Logging**: Implemented a more comprehensive logging setup, including log files for debugging and tracking usage.

#### Version 0.7.1
- **Credits and About Dialogs**: Added detailed "About" and "Credits" dialogs with scrolling animations and detailed acknowledgments.
- **Menu Actions**: Expanded the menu with new actions for opening Discord, the RBC website, and viewing application details.
- **Edge Case Handling**: Improved handling of edge cases on the map, such as interactions at the very edges of the grid.

#### Version 0.7.2
- **Intersection Naming**: Updated the intersection naming logic to handle cases where locations are at the edge of the map, ensuring consistent and accurate labels.
- **SQLite Cookie Storage**: Implemented an SQLite-based cookie storage system for managing session cookies within the application.
- **User Interface Updates**: Enhanced various UI components, including a more dynamic and responsive map view, improved character management, and additional customization options.

#### Version 0.7.3
- **Scraping and Data Updates**: Added automated scraping and data updates for guilds and shops when the "Update Data" button is clicked.
  - The scraping process now runs before updating comboboxes with the latest data.
  - Improved logic to handle missing or outdated data during the scraping process.
- **Bug Fixes**: Addressed various bugs related to data handling and UI updates.
- **Performance Improvements**: Optimized data loading and scraping processes for faster updates.

#### Version 0.8.0
- **Major New Features**:
  - **Enhanced Data Loading and Management**: Comprehensive loading from MySQL, including coordinates for `banks`, `taverns`, `transits`, `user_buildings`, `shops`, `guilds`, and `places_of_interest`.
  - **Coin Management and Cookie Persistence**: Introduced SQLite databases for cookies (`cookies.db`) and coins (`coins.db`), with coin tracking for bank balances, deposits, withdrawals, and in-game actions.
  - **Web Scraping Enhancements**: Expanded `AVITDScraper` to fetch guild and shop update timestamps, supporting automatic updates.
  - **UI and Minimap Enhancements**: Improved minimap rendering with dynamic scaling, zoom controls, and lines to nearest locations.
  - **Theme Customization**: Added `ThemeCustomizationDialog` for custom UI and minimap color settings.
  - **Character Management and Persistence**: Enhanced character list with persistent last active character and auto-login.
  - **Improved Console Logging**: Added JavaScript console logging injection for webview debugging.
- **Known Issues**:
  - Occasional map display overlap when zoomed out.
  - Delays in loading data with remote database connections.

#### Version 0.8.1
- **General Enhancements**: Expanded functionality with advanced error handling and structured logging.
- **Database & Session Management**: Centralized data in `sessions/rbc_map_data.db` for characters, coins, destinations, cookies, and themes.
- **Map & Minimap Features**: Added dynamic minimap labels, destination management with AP costs, and transit route info.
- **User Interface & Theme Customization**: Enhanced theming system with persistent settings and improved UI layout.
- **Coin and Resource Tracking**: Integrated coin parsing from HTML with persistent storage.
- **Error Logging and Debugging**: Detailed logging for all major operations and JavaScript console messages.
- **File Structure and Code Organization**: Modularized code with directory setup for logs, sessions, and images.

#### Version 0.8.2
- **Database Transition**: Fully transitioned from MySQL and separate SQLite databases (`cookies.db`, `coins.db`) to a unified SQLite database (`rbc_map_data.db`).
  - Updated all data loading and storage to use the single SQLite database.
  - Removed pickle-based character storage in favor of SQLite tables.
- **Shopping List Tool**: Introduced `ShoppingListTool` for generating item lists with cost calculations.
  - Supports shop selection, charisma-based pricing, and quantity management.
  - Integrates with character coin data from the database.
- **UI Improvements**: Added browser navigation buttons (back, forward, refresh) above the webview.
- **Bug Fixes**: Resolved issues with minimap rendering at extreme zoom levels.

#### Version 0.9.0
- **Major Features**:
  - **Damage Calculator**: Added `DamageCalculator` dialog for calculating weapon needs based on target BP.
    - Supports charisma-based pricing and displays total cost.
  - **Powers Reference Tool**: Introduced `PowersDialog` for viewing power details and setting guild destinations.
    - Displays power name, guild, cost, quest info, and skill info, with nearest guild location support.
  - **CSS Customization**: Added `CSSCustomizationDialog` for webview styling with color and image options.
    - Saves customizations to SQLite and applies them dynamically.
- **Minimap Enhancements**: Improved rendering with grid lines, better edge case handling, and dynamic text scaling.
- **Menu Bar Expansion**: Added tools menu with options for database viewer, shopping list, damage calculator, and powers reference.
- **Character Login**: Enhanced auto-login with JavaScript form submission and last active character persistence.
- **Known Issues**: Minor delays in CSS application on webview reload.

#### Version 0.9.1
- **Performance Optimizations**: Optimized database queries and minimap updates for faster performance.
- **Recent Destinations**: Added support for saving and displaying up to 10 recent destinations per character.
- **UI Refinements**: Improved info frame styling with consistent colors and word wrapping.
- **Bug Fixes**: Fixed coin tracking inaccuracies and improved error handling in `AVITDScraper`.

#### Version 0.10.0
- **General Enhancements**:
  - **Version Display**: Updated `show_about_dialog` to display `version_number` (0.10.0) for better version tracking.
  - **Documentation**: Refactored docstring with detailed class and function descriptions for open-source clarity.
- **Minimap Features**:
  - Enhanced `draw_minimap` with grid-based rendering and refined location offsets (e.g., +1,+1 for banks).
  - Added support for clicking the minimap to recenter on any location.
- **Tools Integration**: Fully integrated shopping list, damage calculator, and powers reference into the workflow.
  - Shopping list now displays pocket and bank coins alongside the total cost.
  - Damage calculator uses static pricing from Discount Magic with charisma adjustments.
- **Database Enhancements**: Added tables for `shop_items`, `powers`, and `recent_destinations` with initial data.
- **Webview Improvements**: Improved `extract_coins_from_html` to handle additional in-game actions (e.g., robbing, receiving coins).
- **Theme Customization**: Extended to include minimap-specific colors (e.g., set_destination, transit routes).
- **Bug Fixes**:
  - Fixed overlap issues in minimap labels at high zoom levels.
  - Resolved rare crashes during character switching.
- **Known Issues**:
  - Occasional lag when scraping large datasets from "A View in the Dark".
  - CSS customization may not apply instantly on some webview reloads.

---