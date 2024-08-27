This is an attempt to create an interactive map coded in Python for use with Vampires, The Dark Alleyway located at https://quiz.ravenblack.net/blood.pl
Goals:
1) Minimap 
      a. Tracks current location from the game (right frame)
     
      b. Tracks nearest pub, bank, and transit.

        i. Red line drawn to the nearest transit

        ii. Blue line drawn to the nearest bank.

        iii. Orange line drawn to the nearest pub

        iiii. Closest, second closest, or third closest location will be available on request by clicking the appropriate "closest" level button.

      c. Indicate user building on grid

      d. Track and indicate moving buildings.

      e. Can zoom in or out to display 3x3 (default), 5x5, 7x7 or 9x9 grid aroudn player position.

      f. Can be manually centered in one of two methods:

        i. Clicking on a square in the minimap grid will place it in the center of the minimap

        ii. Selecting a location using the dropdowns below the map and clicking "Go" will center the minimap on that location. 

      g. Can track a destination.

        i. Manually center the map on a destination.

        ii. Click "Set Destination" to mark the destination on the map

        iii. Map paints a green line on the map to the destination.

     
2)Have a website which will allow users to do several things:
  
   a. Add new buildings to the map

   b. Track moving buildings (Guilds)

   c. Track targets (ex. hunters)
  
3) Store login credentials to quickly and easily switch between characters.
  
   a. User data will be stored in a local binary file generated with python's "pickle" module.

   b. User data will not be stored on the server at any time for any reason. 
  
4) App data stored in MySQL backend.

Currently, there are multiple versions being worked on simultaneously. Feature testing will be located in the "testing" folder. 

Full credit for this idea goes to the player "Leprichaun" who created the program LIAM2 which is the basis of this project. https://liam2.leprichaunproductions.com/

Additional Credits for the team who made this happen:

Windows: Jonathan Lollis, Justin Solivan

Apple OSx Compatibility: Joseph Lemois

Linux Compatibility: Blaskewitts, Fern Lovebond

Design and Layout: Shuvi, Blair Wilson


### New Features in Recent Versions

#### Character Management
- Added features to manage multiple characters within the application, including adding, modifying, and deleting characters. Character data is stored securely using the `pickle` module.

#### Theme Customization
- Introduced theme customization options allowing users to personalize the application's appearance. Users can save and load their theme settings, offering a more personalized experience.

#### Database Viewer
- A new database viewer utility has been added for advanced users. This feature allows direct interaction with the underlying data tables, providing detailed views and management options.