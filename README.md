# mme
 Morrowind Map Explorer (interactive web service)

 ## What's new
 1. Native multi language support (now fully Russian language is ready, English will be ready a little later)
 2. Hot cycle switching of localizations in the application just by pressing key "Select next language": simultaneous work with several localizations.
 2. One single map data file for each localization (locations, descriptions, images), but different custom data for each.
 > [!WARNING]
 > "[Morrowind Reference.zip](https://www.nexusmods.com/morrowind/mods/53726/)" is no longer required for the full functioning of the program: all inclusive.
 4. Button "Patch" in the application (you can create your own patches and make changes to current map data)

 ## Usage
 Just launch the web application ("app.py")
 > [!NOTE]
 > To switch localization press "Language" (scroll to bottom of page). Editing "settings.json" is no longer required.

 ## Examples
 ![mme](/images/mme.png)

 Full game map with main locations, scrollable and zoomable. You can click on locations, mark them as unopened (default), explored, planned or special - automatically remembered and marked on the map with different colors, as well as leave arbitrary comments for each individual location. When you click on a location point, a detailed description from the Fandom Encyclopedia is downloaded and displayed under the location, including diagrams and pictures (works offline from the offline guide).

 ## Remarks
 All location data is stored separately in an open format (base map data, custom map data and user map settings), so everything can be easily transferred. There is also a built-in mechanism for patching existing map data, including adding new locations. Database support for different localizations of the game.
 > [!NOTE]
 > If you notice an inaccuracy, you can create and add your own patch, then post it here.
