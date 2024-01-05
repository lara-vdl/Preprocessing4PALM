
# citygml2gpd.py

This Python script is used to process CityGML LoD2 files and convert them into GeoPandas GeoDataFrames, which are then saved as shapefiles. It filters them to only include roof surfaces.

## Functionality

The script contains several functions:

1. `parseGml(filePath: str) -> ET.ElementTree`:
   This function reads a GML file and returns it as an Element Tree.

2. `findAllInETree(eTree: ET.ElementTree, query: str) -> list`:
   This function finds all nodes based on a query string and returns a list of all finds.

3. `posListToShapelyPolygon(posList: str) -> Polygon`:
   This function converts a PosList string into a Shapely Polygon.

4. `addRowToGeoDataFrame(geoDataFrame: gpd.GeoDataFrame, newRow: dict) -> gpd.GeoDataFrame`:
   This function adds a new row to an existing GeoDataFrame.

5. `extractHeightsAndGeometryFromGML(eTree: ET.ElementTree, geoDataFrame: gpd.GeoDataFrame, gmlID: str, function: str, buildingPart: bool) -> gpd.GeoDataFrame`:
   This function extracts the height and geometry from a building or roof surface.

6. `saveGeoDataFrameAsShape(filePath: str, geoDataFrame: gpd.GeoDataFrame)`:
   This function saves a GeoDataFrame as a shapefile.

In the main execution block, the script:

1. Sets the path to the CityGML files.
2. Loops through each file in the directory.
3. Parses the GML file and extracts the building data.
4. Extracts the height and geometry from each building.
5. Saves the GeoDataFrame as a shapefile.

## Input data

* CityGML LoD2 files

## Output

* shapefiles with building geometries (only roof surfaces) and GML ID, height and function

## Usage

To use this script, you need to have xml.etree.ElementTree, geopandas, shapely, pandas, glob, and os libraries installed in your Python environment. You can run the script from the command line as follows:

~~~bash
python citygml2gpd.py
~~~
Please note that you may need to adjust the `build_path` variable to point to the directory containing your CityGML files.

## Dependencies

* xml.etree.ElementTree
* geopandas
* shapely
* pandas
* glob
* os

## Limitations

This script assumes that the CityGML files are in a specific format and contain certain elements. If your data files have a different format or do not contain these elements, the script may not work as expected.
