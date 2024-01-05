# buildings2PALM.py
This Python script is used to process building data and translate Zensus data to the PALM building types.

## Functionality

The script contains three main functions:

1. `translateZensus(clip_file:str, grid_file:str, zensus_file:str, key_file:str, layername= "de_grid_laea_100m", epsg=25832) -> gpd.GeoDataFrame`:
   This function translates the Zensus data to the PALM building types. It reads and clips data, reads Zensus data and reduces it to building age, reads a translation table, merges geodataframe and pandas dataframe, and returns a geodataframe.

2. `combine_shapefiles(directory:str, clip_file:str) -> gpd.GeoDataFrame`:
   This function combines all shapefiles in a directory into one geodataframe and creates a unique ID for each GML ID. The data is clipped to the domain extend.

3. `rasteriseBuildings(gdf:gpd.GeoDataFrame,column:str,resolution:float,dtype:str,nodata:float,out_path:str) -> None`:
   This function rasterizes the buildings to a given resolution and saves it as a GeoTiff.

In the main execution block, the script:

1. Sets data paths.
2. Calls the `translateZensus` and `combine_shapefiles` functions with appropriate arguments.
3. Spatially joins the dataframes.
4. Drops unnecessary columns.
5. Fills NaN values in building_type column with 5.
6. Saves the dataframe as a shapefile.
7. Calls the `rasteriseBuildings` function to rasterize the buildings.

## Input data
* shapefiles with building geometries 
* grid shapefile for Zensus data (100 m grid)
* Zensus building data
* translation table as CSV file to translate Zensus building age to PALM building type

## Output
* shapefile with building geometries, IDs, height and building type
* three raster files for building ID, height and type

## Usage

To use this script, you need to have GeoPandas, pandas, os, and rasterio libraries installed in your Python environment. You can run the script from the command line as follows:

```bash
python buildings2PALM.py
```

Please note that you may need to adjust the data paths and function arguments to match your data.

## Dependencies
* GeoPandas
* pandas
* os
* rasterio

## Limitations
This script assumes that the data files have a specific structure and contain certain elements. If your data files have a different structure or do not contain these elements, the script may not work as expected.

