# mme
 Morrowind Map Explorer (interactive web service)

 ## Usage
 Just launch the web application ("app.py")
 > [!IMPORTANT]
 > To use the full functionality, download and unzip "[Morrowind Reference.zip](https://www.nexusmods.com/morrowind/mods/53726/)" archive into the "Morrowind Reference" directory (to be on the same level as "mme") before the first startup. It comes separately, as it is built and updated separately via the [fallout_quests](https://github.com/mr-js/fallout_quests) project and takes up a lot of space.

 ## Examples
 ![mme](/images/mme.jpeg)

 Full game map with main locations, scrollable and zoomable. You can click on locations, mark them as unopened (default), explored, planned or special - automatically remembered and marked on the map with different colors, as well as leave arbitrary comments for each individual location. When you click on a location point, a detailed description from the Fandom Encyclopedia is downloaded and displayed under the location, including diagrams and pictures (works offline from the offline guide).

 ## Remarks
 All location data is stored separately in an open format (base map data, custom map data, settings), so everything can be easily transferred. There is also a built-in mechanism for patching existing map data, including adding new locations. Database support for English and Russian localizations of the game.
 > [!NOTE]
 > By default the map for Russian localization of the game is displayed. But in the "source.zip" there is also a map "map.json.eng" with original names for English localization of the game. To switch localization it is enough to replace the file "map.json" in the root and delete all other files ("custom.json" and "settings.json") there as well.
