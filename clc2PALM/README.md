# clc2PALM.py

This Python script is used to process Corine Land Cover (CLC) data and translate it to PALM classes.

## Functionality

The script contains two main functions:

1. `rasteriseSurface(gdf:gpd.GeoDataFrame,column:str,resolution:float) -> None`:
   This function rasterizes the processed CLC dataset with a desired resolution and converts the values to integer.

2. `translateCLC(clip_file:str, clc_file:str, key_file:str, layername= "U2018_CLC2018_V2020_20u1",epsg=25832) -> tuple[gpd.GeoDataFrame,gpd.GeoDataFrame]`:
   This function translates the CLC data to PALM classes. It reads and clips data, reads a translation table, merges geodataframe and pandas dataframe, and returns a tuple of geodataframes.

In the main execution block, the script:

1. Sets data paths.
2. Calls the `translateCLC` function to translate the CLC data.
3. Keeps only relevant columns.
4. Combines with named PALM class table for visualisation purposes.
5. Saves the dataframe as a shapefile.
6. Calls the `rasteriseSurface` function to rasterize the CLC data.

## Input data
* CORINE Land Cover dataset (.gpkg)
* translation table as csv file
* csv file with names of PALM classes for visualisation purposes
* Shapefile with region of interest for clipping

## Output
* Shapefile with PALM surface types
* two raster files with pavement and land use 

## Usage

To use this script, you need to have GeoPandas, pandas, os, numpy, rasterio, geocube, xarray, rioxarray, and shapely libraries installed in your Python environment. You can run the script from the command line as follows:

~~~bash
python clc2PALM.py
~~~

Please note that you may need to adjust the data paths and function arguments to match your data.

## Dependencies
* GeoPandas
* pandas
* os
* numpy
* rasterio
* geocube
* xarray
* rioxarray
* shapely

## Limitations
This script assumes that the CLC data files are in a specific format and contain certain elements. If your data files have a different format or do not contain these elements, the script may not work as expected.