### Changelog for RBC City Map Application

## Version 0.1.0

### 💡 Summary
## Version 0.1.0 of the RBCMap app is a functional prototype built with tkinter, focusing on a minimap interface and manual street navigation using dropdowns and zooming. This version is highly procedural and uses no class-based structure.


### 🧩 Key Features in 0.1.0
🗺️ Minimap
Grid-style minimap rendered using a Canvas.

Visualizes intersections of N-S and E-W streets.

Dynamically adjusts based on zoom_level.

Clickable grid allows repositioning the viewport (on_minimap_click).

🧭 Zoom Controls
Buttons for "Zoom In" and "Zoom Out".

Zoom affects how many streets are shown in the viewport (range 3–10).

🏙️ Street Navigation
Dropdowns for selecting a specific N-S and E-W intersection.

“Go” button jumps the map to that location via go_to_location().


📌 Map Refresh & Extra Buttons
Buttons included:

“Refresh Map” – calls update_minimap().

“Discord” – placeholder for community link.

“Modify Buildings” – placeholder for webpage/editor.


### 📦 Placeholder Functions
Functions like open_webpage(), open_discord(), and set_destination() exist but are unimplemented — suggesting planned features like building editing, community integration, and character destination logic.


### 🛠️ Utilities
generate_ew_streets() builds E-W street names from 1st to 100th with ordinal suffixes.

Static N-S street list contains both natural and thematic naming (e.g., “Pine”, “Torment”, “Despair”).


### 🧱 Technical Notes
Hardcoded GUI using absolute grid placements.

Pure procedural code — no object-oriented design.

No data persistence or external file/database integration.

Initial zoom logic and bounds checking are in place for stability.

---

## Version 0.2.0
🚀 Summary
## Version 0.2.0 introduces data-driven enhancements to the map rendering logic and begins to externalize key configuration data, indicating a move toward modularity and semantic enrichment of the map. It remains procedural and GUI-based, using tkinter, but introduces data overlay logic and better street metadata.


📌 Key Enhancements Over 0.1.0
1. Landmark Overlays
Introduced color-coding for specific locations:

blue → Banks

orange → Pubs

red → Transit points

gray → Normal intersections

Determined by checking (ns_street, ew_street) membership in banks, pubs, and transits.

2. Data Externalization
New import: from variables import *

Suggests landmark data (banks, pubs, transits) now reside in a separate variables.py module.

Moves away from hardcoding everything in main, enabling easier expansion/maintenance.

3. Visual Refinement
Changed alley color from blue → black, clearly separating structural roads from data-flagged locations.

Cleaned up layout by switching label order in dropdowns to N-S first, then E-W (likely for readability).


🧠 Architectural Implications
Although still not object-oriented, this update clearly shows domain-aware thinking — streets are now data-bearing, not just labels.

The minimap canvas becomes semantically meaningful beyond layout, taking first steps toward a GIS-style data layer system.

🧭 GUI & Interaction Logic
GUI layout and functionality are largely unchanged from 0.1.0.

Retains the same controls, buttons, and logic for zoom, refresh, and movement.

Placeholder functions (set_destination, open_discord, open_webpage) still do nothing — their implementation remains pending.

---

0.3.0 – Initial Refactor (Tkinter OOP)
**Key **Changes:****

First version to introduce class-based design with CityMapApp.

Clean separation of:

GUI setup (setup_gui)

Logic for zooming, refreshing, and updating maps

Integrated proximity logic: nearest bank/pub/transit display.

Map display using two canvases (map_canvas, minimap_canvas).

Dropdowns for selecting X/Y streets (rows/columns).

Uses rows and columns dicts for grid logic.

> **Assessment:** Experimental OO version, still using tkinter, but paving the way for future Qt refactor.


### 🧱 0.3.1 – Partial Rework + Abstracted Map Logic
**Key **Changes:****

Introduced a Map class encapsulating core minimap data (zoom, center).

Partial backslide to procedural code in UI setup.

Minimap placeholder logic present, but not implemented.

Suggests a transitional stage from 0.3.0 to something Qt-based.

> **Assessment:** Attempt to modularize backend (Map class) before a full GUI transition.


### 💼 0.3.2 – PyQt5 Migration Begins
**Key **Changes:****

Switched GUI toolkit from tkinter to PyQt5.

Replaced Canvas with QLabel + QPixmap for drawing.

Introduced sidebar with:

Minimap

Closest location buttons

Combo boxes for street selection

Zoom/Go/Destination controls

Refresh, Discord, and Website buttons

Basic structure for character list panel added.

Map rendering was still placeholder (load_minimap()), no actual drawing logic.

> **Assessment:** Foundation of the modern UI — PyQt5 layout, modular widgets, and QWebEngine for in-game site.

🧭 0.3.3 – Minimap Rendering Engine Implemented
**Key **Changes:****

Fully functional minimap drawing using QPainter on QPixmap.

Differentiates cell types:

Alleys, street edges, banks, pubs, transits, user buildings

Labels added to:

Named intersections

User buildings

Adds click detection on minimap (mouse events).

Combo box to go to a specific location using street names.

> **Assessment:** This version solidified the interactive PyQt-based minimap engine, replacing prior tkinter logic.


### 🧩 0.3.4 – Enhanced Qt Layout + Post-Load Coordination
**Key **Changes:****

Live HTML parsing from embedded WebView using BeautifulSoup.

Extracts player coordinates (x, y) and recenters minimap dynamically.

Greatly improved integration between map UI and game logic.

Map render logic abstracted to draw_minimap(), coordinates validated, text centered precisely.

> **Assessment:** Fully matured prototype of Qt-based RBCMap — bridging game backend data and GUI map interaction.

---


### 🧱 0.4.0 – Enhanced HTML Integration & Drawing Logic
**Key **Changes:****

Adds extract_coordinates_from_html() using BeautifulSoup.

Pulls player coordinates dynamically from the embedded web view.

Minimap centers based on real in-game location.

Introduced structured minimap drawing via draw_minimap(), with:

Street overlays

Color-coded special locations (banks, pubs, transits, user buildings)

Destination setting stub added (Set Destination button).


✅ Introduced web-integrated positioning and a persistent GUI foundation.

💥 0.4.1 – Nearest-Location Line Drawing (with caveat)
**Key **Additions:****

Draws lines to 1st/2nd/3rd closest banks, pubs, and transits from center.

Implements closest_level logic tied to three new buttons.


☠️ Bug note: Selecting closest levels other than 1 causes stack buffer overflow.


⚠️ Functionally ambitious but structurally unstable. Good idea, flawed execution.


🔧 0.4.2 – Stability Rework, Feature Isolation
**Changes:**

Removed interactive closest-location levels due to instability.

Simplified to show only nearest (1st) bank/pub/transit.

Preserved:

Map rendering

Real-time location pulling from HTML

Zoom and go-to logic

Prepared code for restoring closest_level logic later.


🔁 Rollback and cleanup patch, focusing on reliability and readiness for persistence.


✅ 0.4.3 – Destination Logic & Visual Feedback
Major **Additions:**

Implements:

Persistent destination setting via pickle

Green path to destination drawn on minimap

Restores draw_location() abstraction, applies to all entity types.

Adds find_nearest_*() logic to draw paths to closest pub, bank, transit.

Maintains full parsing/rendering integrity from earlier versions.


🎯 Feature complete version for:

Destination persistence

Full nearest-location visual feedback

Refined GUI controls

--


### 🧱 0.5.0 – 
### 🧩 First Database-Driven Release
**Highlights:**

Introduced connect_to_database() with fallback to remote host.

Loaded columns, rows, banks, taverns, transits, user buildings, and color_mappings from MySQL.

draw_minimap() adjusted to reflect color mappings from DB (color_map).

HTML extraction now pulls from <span class='intersect'>.


✅ First integration of live data from a structured MySQL schema.


### 🛠️ 0.5.1 – 🌈 Qt Color Fix & Code Clarity
**Changes:**

Converts color strings from DB directly into QColor objects in color_map.

Ensures all dynamic visual updates (e.g. edges, alleys, etc.) honor the loaded palette.

Renamed color_map -> self.color_map inside the class for scope clarity.


🧠 Improved visual configuration and reduced hardcoded rendering logic.


🔁 0.5.2 – 🛍️ Shops & Guilds Integrated
**Additions:**

Loads shops and guilds from the database.

Parses their coordinates and next update timestamps.

Includes logic for rendering shop/guild icons on minimap.

Drawn using same draw_location() routine with new categories.


🎯 Adds merchant and faction overlays with live update hooks (timestamp support).


### 📅 0.5.3 – 🔍 Improved HTML Coordinate Extraction
**Enhancements:**

Improved fallback HTML parsing:

Now checks for <input name="x"> and <input name="y"> if <span class='intersect'> is missing.

Alternative fallback: parses <td class='street'> block with embedded <form>.

More robust against A View in the Dark HTML variations.

🛡️ Enhanced HTML fault tolerance in response to inconsistent site markup.


🧠 0.5.4 – 
### 📊 Data Scraper & Next-Update Forecasting
Major New Logic:

Adds scrape_avitd_data():

Scrapes guilds and shops from the A View in the Dark site.

Updates DB rows with next update timestamps.

Adds:

extract_next_update_time()

update_guild(), update_shop()

update_guilds(), update_shops()

get_next_update_times() exposed for use in UI/notifications.


### 🔄 Fully automated sync of key game structures to app backend via web scraping.

---

0.6.0 – 
### 🧬 Modular Cleanup + Persistence Prep
**Changes:**

Cleaned database schema queries, including color_mappings, shops, and guilds with next_update.

Refactored data loading into load_data() with tight dictionary comprehensions.

get_next_update_times() pulls guilds and shops update cycles.

🔗 Reliable DB-backed backend with clean data type safety.


### 🧪 0.6.1 – 
### 📊 Added placesofinterest & Fault-Resilient DB Reads
Improvements:

Integrated placesofinterest table from DB.

Improved resilience on coordinate mapping: filters out entries with None from failed columns.get(...).

Reduced potential for GUI crashes from missing data.

🛡️ Adds soft failure protections in data loading.


### 🧩 0.6.2 – 
### 🛠️ Setup Scripts & AP Cost UI
**Key **Additions:****

Added automatic module installation prompt (pip install) with delay-based relaunch (great for first-time users).

load_characters() tied into dropdown, allowing users to select, add, or remove characters.

Minor GUI tweaks for padding and layout alignment.


### 📦 Packs usability improvements and setup streamlining.


### 🔥 0.6.3 – 
🧠 Intelligent Character Login + Logging System
Major **Upgrades:**

🔑 Character login/logout via in-game site using QWebEngineView JS injection.

Logs out current character → injects name/password → logs back in


## 🧾 Logging system added:

logs/rbc_YYYY-MM-DD.log

Uses logging.debug, info, warning, error


### 🗃 Character list transitioned from QComboBox → QListWidget for better interactivity.


🎨 GUI polish: Highlighted labels (banks, taverns, destination), “Coming Soon” website dialog.


### 📁 Added ensure_directories_exist() to create logs/ and sessions/ if missing.


🧠 Smart automation, session persistence, and robust logging define this release.

---


### 🧱 0.7.0 – 🚀 Migration to PySide6
Key Shifts:

Fully switched from PyQt5 → PySide6.

Introduced:

QWebEngineProfile for persistent cookies

Modularized HTML, database, and logging setup

Introduced persistent character management with fallback if no characters exist.


🧠 This version modernizes the foundation and boosts future-proofing.


🧠 0.7.1 – 
🎨 Theme Customization + Persistent Cookies
**New Features:**

Added load_theme_settings() and apply_theme() for UI color theming.

Implemented persistent QWebEngineProfile with stored cookies in sessions/cookies.

Abstracted cookie handling:

Load/save cookies via pickle

Auto-reapply cookies to quiz.ravenblack.net


🎨 Theming + 🍪 cookies = UX enhancement and session persistency.


### 📦 0.7.2 – 📋 SQLite Cookie Storage & Character Persistence
**Upgrades:**

Replaced pickle-based cookies with SQLite-backed cookie DB (cookies.db).

Introduced:

initialize_cookie_db(), save_cookie_to_db(), load_cookies_from_db()

Character persistence logic now loads last active character automatically.

AVITDScraper integrated into app load to update DB automatically.

💾 First use of SQLite local state. Better for scaling.


🔧 0.7.3 – 
### 🧩 Componentization, Multi-Dialog System, JS Injection
Massive Refactor:

App now includes:

DatabaseViewer for tab-based DB browsing

ThemeCustomizationDialog for visual tuning

SetDestinationDialog and CharacterDialog modularized

JavaScript logging via inject_console_logging()

Supports reading JS console logs from WebView.

Expanded load_data() to include new POIs.


### 🧱 RBCMap becomes a modular, maintainable toolkit, not just a map viewer.

---


### 🧱 0.8.0 – 🗄️ SQLite Conversion & Persistent UX Foundation
**Changes:**

Fully transitioned backend from MySQL to SQLite for offline and portable deployment.

connect_to_database() and load_data() now point to local rbc_map_data.db.

Introduced theme, coin, and cookie persistence tables under a centralized sessions/ directory.

Modularized:

initialize_cookie_db()

initialize_coins_db()

initialize_database() with full schema validation.


### 🔄 Major pivot from cloud-bound to standalone desktop-first architecture.


### 🔐 0.8.1 – 
### 🔐 Secure State, Schema Checking, and Expanded Dialog Logic
**New Features:**

Full schema validation and column-type checking added to initialize_database().

cryptography.Fernet encryption support added for sensitive data (e.g., passwords).

Dialog-based modularity extended:

CharacterDialog

ThemeCustomizationDialog

SetDestinationDialog

Database settings, cookies, and theme colors now stored securely and validated at launch.


### 🧱 Hardened the foundation with encryption + full schema introspection logic.

💥 0.8.2 – ⚔️ Damage Calculator & Extended POI Coverage
Major **Additions:**

New DamageCalculator dialog tool:

Input: Target BP

Calculates hit counts for:

Holy Water

Garlic Spray

Wooden Stake

Computes charisma-discounted prices and total coin cost

Load logic updated to support:

shop_items pricing with charisma scaling

Live coin balance integration per character


🎯 Adds gameplay planning tools, bridging map navigation with action economics.

---


### 🧱 0.9.0 – 
### 🔐 Encrypted Local State & Database Formalization
Key **Enhancements:**

Switched to fully encrypted storage for sensitive data (e.g., character passwords) using cryptography.Fernet.

Finalized SQLite schema:

Adds powers, placesofinterest, shop_items, and recent_destinations.

Adds foreign key constraints and default population for banks, colors, guilds, powers, POIs, etc.

Resilient modular initialization:

initialize_database() builds all tables with INSERT OR IGNORE seeding.

Extensive documentation headers added to all sections.


### 🧱 Formalized DB schema, added encryption, and enhanced modular infrastructure.


🧠 0.9.1 – 📖 Full-Class Registry + Role Documentation
Structural & UX **Enhancements:**

Refined class/module documentation throughout:

RBCCommunityMap, CharacterDialog, DamageCalculatorUI, ShoppingListTool, etc.

Each class/function described by purpose and feature scope.

Bundled all primary features into top-level main.py docstring (great for onboarding devs).

Expanded installer safety: checks module availability at runtime and exits cleanly if missing.


### 📘 Offers full application self-documentation, onboarding ease, and structural transparency.

---


### 🧱 0.10.0 – 
### 💼 Unified Application Structure
**Highlights:**

Refactored RBCCommunityMap into a comprehensive, class-based application core.

Integrated:

Encrypted character handling

Cookie/session persistence

Theme and CSS injection

Full webview interaction via JS + HTML parsing

Created tools:

Damage Calculator

Shopping List Tool

Database Viewer

Powers and Guilds UI


🎯 Sets the gold standard structure for all major features in a centralized GUI shell​
.


### 🧪 0.10.1 – 
### 🧪 Debugging and Display Refinement
**Changes:**

Introduced fine-grained JavaScript console logging hooks via QWebChannel.

Improved load-time handling for coin balances and minimap center recalculations.

Fixed redundant/inactive menu entries (e.g., go back/forward).


🔧 Focused on event hooks, cleanup, and edge-case polish​
.

🔍 0.10.2 – 
### 📊 Metadata Extraction and Info Frame Enhancements
**Enhancements:**

Added update_info_frame() showing:

AP cost estimates

Closest location summaries

Dynamically calculates movement costs using calculate_ap_cost().

Expanded extract_coins_from_html() to support deeper page parsing for accurate balance updates.


🔁 Reinforces app’s value as a real-time tracker and planner​
.


### 🔐 0.10.3 – 
### 🔐 Final Feature Polishing & Schema Finalization
Final **Additions:**

Hardened initialize_database() with:

Over a dozen normalized tables (banks, cookies, shop_items, coins, POIs, guilds, etc.)

INSERT OR IGNORE bootstrap logic for default records

check_required_modules() now validates environment dependencies at launch.

Fully documented top-level application, classes, and methods (self-contained docset).


### 🧱 Locked in a fully seeded local database, supports upgrades without manual user intervention​.

---


### 🧱 0.11.0 – 🧭 Feature Consolidation & Keyboard Navigation
**Additions:**

Introduced WASD keybindings with database-configurable modes.

All major tools — Minimap, Powers, Damage Calculator, Shopping List — consolidated into main UI.

RBCCommunityMap now supports:

move_character(), setup_keybindings(), zoom_in/out

Major module imports refactored into clean sections for readability.

Documentation headers massively improved.


📌 Solidifies RBCMap as a full-featured modular app​
.


### 🧪 0.11.1 – 🪛 Patch for Visuals and Table Coverage
**Enhancements:**

Fixes inconsistencies in theme customization (widget padding, font scaling).

UI consistency polish: spacing and alignment adjusted in dialogs.

Expanded create_tables() to include css_profiles, custom_css, and several migration-safe defaults.


### 🧱 Focused on visual polish and database table consistency​
.


🧠 0.11.2 – 
### 🖥 Splash Screen & Loading Visual Feedback
**New Features:**

Added SplashScreen class using QSplashScreen, visually indicating loading status.

Webview error handling improved — logs load issues more precisely.

Ensured compatibility of web engine initialization on slower machines (fixes some black-screen issues).

First version where startup dependencies are shown as "loading..." at splash.


🎨 First steps toward full UX onboarding flow and startup feedback​
.

🧹 0.11.3 – 🧽 Final Pre-Refactor Polish
**Changes:**

Tightened file structure for modules — preparation for 0.12’s multi-folder modular split.

Logging messages refined, paths shortened to use relative sessions/, logs/, etc.

Final patch before major 0.12.0 directory and architecture shift.

🧼 Focused on cleanup and refactor readiness​.

---


## Version 0.12.0

### 🧱 Monolithic Architecture with Enhanced Modularity

- **Monolithic structure** retained in `main_0.12.0.py` with improved internal modularity for maintainability.
- **`create_tables()` and `insert_initial_data()`** define and seed all SQLite tables, eliminating manual pre-seeding.
- **`check_and_install_modules()`** ensures required Python packages are installed at startup.
- **QSplashScreen** splash screen enhances startup UX with loading feedback.

### 🛠️ Core Features Solidified

- **RBCCommunityMap** unifies key UI components:
  - Minimap rendering with dynamic overlays
  - Zoom and movement logic
  - WASD keyboard navigation
  - Theme application
  - Character persistence
- **Persistent data** for characters, cookies, destinations, coins, and logging settings via SQLite.
- **Expanded dialog system** integrates modular tools:
  - `DamageCalculator`, `ShoppingListTool`, `ThemeCustomizationDialog`, `CSSCustomizationDialog`, `DatabaseViewer`, `PowersDialog`, `SetDestinationDialog`, `CharacterDialog`
  - Each tool operates independently with DB hooks, input validation, and polished UI.

### 💡 New Technical Capabilities

- **Logging** uses `logging.FileHandler` with dynamic log level from DB.
- **Auto-directory setup** creates `logs/`, `sessions/`, and `images/` at launch.
- **Real-time JavaScript logging and CSS injection** for webview interaction.
- **Coordinate mapping and color customization** stored in DB, extensible via `color_mappings` and `css_profiles`.

### 🧬 Schema and Data Foundations

- Over 20 SQLite tables, including `characters`, `coins`, `banks`, `shops`, `guilds`, `taverns`, `placesofinterest`, `color_mappings`, `custom_css`, `rows`, `columns`, `powers`, `discord_servers`.
- Tables seeded with default data using `INSERT OR IGNORE` for first-time installs and upgrade-safe bootstrapping.