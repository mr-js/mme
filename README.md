# mme
 Morrowind Map Explorer (interactive web service)

 ## What's new
 1. Native multi language support (now fully English language and Russian language)
 2. Hot cycle switching of localizations in the application just by pressing key "Select next language": simultaneous work with several localizations.
 3. One single map data file for each localization (locations, descriptions, images), but different custom data for each.
 4. Button "Patch" in the application (you can create your own patches and make changes to current map data).
 5. Updated the patch mechanism and resolved collisions between names in the game and encyclopedia (for RU in manual mode for ENG via AI).
 6. Now you can use the load objects details (LOD) setting to optimize the appearance of the map (5-leveled LOD).
 7. New User Interface (UI) via modern bootstrap.

 ## Usage
 Just launch the web application ("app.py")

 > [!WARNING]
 > Your primary data (notes and markers) are stored in /profiles/{language}/custom.json. If you are actively using it, don't forget to make backups.

 ## Examples
 ![mme](/images/mme_1.png)

 Full game map with main locations, scrollable and zoomable. You can click on locations, mark them as unopened (default), explored, planned or special - automatically remembered and marked on the map with different colors, as well as leave arbitrary comments for each individual location. When you click on a location point, a detailed description from the Fandom Encyclopedia is displayed under the location, including diagrams and pictures (works offline from local database).

 ![mme](/images/mme_2.png)

 ![mme](/images/mme_3.png)

 ![mme](/images/mme_4.png)

 ## Remarks
 All location data is stored separately in an open format (base map data, custom map data and user map settings), so everything can be easily transferred. There is also a built-in mechanism for patching existing map data, including adding new locations. Database support for different localizations of the game.
 > [!NOTE]
 > If you notice an inaccuracy, you can create and add your own patch, then post it here.
