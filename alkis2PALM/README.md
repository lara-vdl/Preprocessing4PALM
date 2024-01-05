# alkis2PALM.py
This script is used to translate ALKIS geospatial data to PALM surface types.

ALKIS consists of several individual layers describing the current use of an area. Some of those layers can directly be translated into a PALM surface type. Other layers are translated to PALM surface types based on the attribute "funktion" (function) or "vegetationsmerkmal" (vegetation characteristic). The translation for those layers is conducted with translation tables. As some features have NAN values in their attributes, a PALM surface type is assigned based on the ALKIS layer from which they originate.

As each ALKIS layer has to be handled differently, a dictionary is defined with the file name, layer name within the xml file, whether to translate to whole layer or with a translation table, how NAN values are replaced and refinements to be made. An example dictionary is provided and currently contains the city of Bochum.

## Functionality

The script contains nine main functions:

1. `readClipper(file:str) -> gpd.GeoDataFrame:` This function reads a shapefile (clipper) as a GeoDataFrame. It takes a string argument representing the file name and returns a GeoDataFrame.

2. `readAndClipLayers(filename:str, layername:str, clipper:gpd.GeoDataFrame, epsg = 25832) -> gpd.GeoDataFrame:` This function reads an ALKIS layer (XML file) into a GeoDataFrame and clips it to the desired extent with a clipper GeoDataFrame. It returns the clipped GeoDataFrame.

3. `readKeyTable(file:str) -> pd.DataFrame:` This function reads a CSV file (translation tables) as a pandas DataFrame. It takes a string argument representing the file name and returns a DataFrame.

4. `replaceNA(config:str, layer:gpd.GeoDataFrame, value:float, columnToOverwrite:str) -> gpd.GeoDataFrame:` This function replaces NaN values in a GeoDataFrame based on a configuration. It returns the updated GeoDataFrame.

5. `vectoriseImperviousness(rasterDs:str, clipper:gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame,gpd.GeoDataFrame]:` This function reads the imperviousness raster, reclassifies the degrees of imperviousness into three classes, vectorizes the raster, and returns two GeoDataFrames with low and high imperviousness.

6. `identifyGreen(imperv_low:gpd.GeoDataFrame, alkis_edit:gpd.GeoDataFrame) -> gpd.GeoDataFrame:` This function identifies green areas within areas currently defined as a PALM pavement (artificial) type 3. It returns the updated GeoDataFrame.

7. `identifySealed(imperv_high:gpd.GeoDataFrame, alkis_edit:gpd.GeoDataFrame) -> gpd.GeoDataFrame:` This function identifies sealed areas within areas currently defined as a PALM vegetation type. It returns the updated GeoDataFrame.

8. `overlayRail(city:str) -> None:` This function overlays the ALKIS rail layer with other layers defined in the dictionary to exclude subways. It doesn't return anything.

9. `rasteriseSurface(gdf:gpd.GeoDataFrame,column:str,resolution:float) -> None:` This function rasterizes the processed ALKIS dataset with a desired resolution and converts the values to integer. It doesn't return anything.

In the main execution block, the script:

1. **Read Clipper and Vectorise Imperviousness**: The script starts by reading a shapefile (clipper) and vectorising the imperviousness raster data. The vectorised data is divided into two categories: low imperviousness and high imperviousness.

2. **Loop Through Dictionary**: The script then loops through a dictionary that defines the translation and further operations for each ALKIS layer. For each layer, the following steps are performed:

    - The layer is read and clipped to the desired extent using the clipper.
    - The layer is translated to PALM classes either with a translation table or as a whole layer.
    - NaN values in the layer are replaced based on a given configuration.
    - If necessary, green areas in sealed classes are identified and changed to vegetation.
    - If necessary, sealed areas in sports and leisure facilities are identified and changed to pavement.

3. **Overlay Rail**: The script overlays the ALKIS rail layer with sealed ALKIS data to exclude subways.

4. **Combine ALKIS Layers**: All ALKIS layers translated to PALM are combined into a single GeoDataFrame. Only necessary columns are kept.

5. **Combine with Named PALM Class Table**: The combined GeoDataFrame is merged with a named PALM class table for visualisation purposes.

6. **Save Shapefile**: The final GeoDataFrame is saved as a shapefile.

7. **Create Land Use Column**: A land use column is created from the combination of vegetation and water for later use in GEO4PALM.

8. **Rasterise Layers**: Finally, the pavement and land use layers are rasterised with a desired resolution.

## Input Data

The script uses the following data:

- ALKIS geospatial data in XML format.
- A shapefile (clipper) to define the area of interest.
- An imperviousness raster data.
- CSV files (translation tables) to map ALKIS attributes to PALM classes.
- A CSV file with named PALM classes for visualisation purposes.
- dictionary file defining the operations for each ALKIS layer for a city (.json file)

## Output

The script produces the following output:

- A shapefile with ALKIS data translated to PALM surface types.
- Two raster files with the pavement and land use data.

## Usage

To use this script, you need to have GeoPandas, pandas, os, and rasterio libraries installed in your Python environment. You can run the script from the command line as follows:

```bash
python alkis2PALM.py
```

Please note that you may need to adjust the data paths and function arguments to match your data.

## Dependencies
* GeoPandas
* pandas
* os
* rasterio
* numpy
* json
* xarray
* rioxarray
* shapely
* geocube

## Limitations
This script assumes that the data files have a specific structure and contain certain elements. If your data files have a different structure or do not contain these elements, the script may not work as expected.
