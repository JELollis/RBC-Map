# RBC City Map Application

This project is an attempt to create an interactive map coded in Python for use with **Vampires, The Dark Alleyway** located at [RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## Goals

### 1) Minimap Features
   - **Track Current Location**: Automatically track the current location based on the game’s right frame.
   - **Nearest Points of Interest**:
     - **Red Line**: Drawn to the nearest transit station.
     - **Blue Line**: Drawn to the nearest bank.
     - **Orange Line**: Drawn to the nearest pub.
     - **Closest Locations**: Easily find the closest, second closest, or third closest locations by clicking the appropriate "closest" level button.
   - **User Buildings**: Indicate user-specific buildings on the grid.
   - **Moving Buildings**: Track and indicate moving buildings.
   - **Zoom Levels**: The map can zoom in or out to display a 3x3 (default), 5x5, 7x7, or 9x9 grid around the player’s position.
   - **Manual Centering**:
     - **Click to Center**: Click on a square in the minimap grid to center it.
     - **Dropdown Selection**: Select a location using the dropdowns below the map and click "Go" to center the minimap on that location.
   - **Destination Tracking**:
     - **Manual Centering**: Manually center the map on a destination.
     - **Set Destination**: Click "Set Destination" to mark the destination on the map.
     - **Green Line**: Paints a green line on the map to the destination.

### 2) Website Features
   - **Add New Buildings**: Allow users to add new buildings to the map.
   - **Track Moving Buildings**: Track the movement of buildings such as guilds.
   - **Target Tracking**: Track specific targets like hunters.

### 3) Character Management
   - **Quick Switch**: Store login credentials to quickly and easily switch between characters.
   - **Local Data Storage**:
     - User data is stored in a local binary file generated using Python's `pickle` module.
     - No user data is stored on the server at any time for any reason.

### 4) Backend Storage
   - **MySQL Database**: All app data is stored in a MySQL backend.

---

## Development

Currently, multiple versions are being worked on simultaneously. Feature testing is located in the "testing" folder.

### Credits

This project is based on the original idea from the player "Leprichaun," who created the program LIAM2. Full credit goes to them for inspiring this project. Visit [LIAM2](https://liam2.leprichaunproductions.com/) for more information.

### Contributors
- **Windows Compatibility**: Jonathan Lollis, Justin Solivan
- **Apple OSx Compatibility**: Joseph Lemois
- **Linux Compatibility**: Blaskewitts, Fern Lovebond
- **Design and Layout**: Shuvi, Blair Wilson

---

## New Features in Recent Versions

### Character Management
- Added features to manage multiple characters within the application, including adding, modifying, and deleting characters. Character data is stored securely using the `pickle` module.

### Theme Customization
- Introduced theme customization options allowing users to personalize the application's appearance. Users can save and load their theme settings, offering a more personalized experience.

### Database Viewer
- A new database viewer utility has been added for advanced users. This feature allows direct interaction with the underlying data tables, providing detailed views and management options.

### Scraping and Data Updates (v0.7.3)
- Automated scraping and data updates for guilds and shops when the "Update Data" button is clicked. The scraping process now runs before updating comboboxes with the latest data.

---

This README provides a comprehensive overview of the RBC City Map Application, its goals, features, and recent updates. For any further development, refer to the "testing" folder for feature testing and exploration.
