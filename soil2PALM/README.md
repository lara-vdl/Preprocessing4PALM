# soil2PALM.py

This Python script is used to process soil data from NRW (BK50) and translate it to PALM classes.

## Functionality

The script contains two main functions:

1. `rasteriseSoil(gdf:gpd.GeoDataFrame,column:str,resolution:float) -> None`:
   This function rasterizes the processed soil dataset with a desired resolution and converts the values to integer.

2. `translateSoil(clip_file:str, soil_file:str, key_file:str,epsg=25832) -> gpd.GeoDataFrame`:
   This function translates the soil data from NRW (BK50) to PALM classes. It reads and clips data, reads a translation table, merges geodataframe and pandas dataframe, and returns a geodataframe.

In the main execution block, the script:

1. Sets data paths.
2. Calls the `translateSoil` function to translate the soil data.
3. Keeps only relevant columns.
4. Saves the dataframe as a shapefile.
5. Calls the `rasteriseSoil` function to rasterize the soil data.

## Input data
* soil dataset NRW (.shp)
* translation table as csv file

## Output
* raster file with soil type

## Usage

To use this script, you need to have GeoPandas, pandas, os, and rasterio libraries installed in your Python environment. You can run the script from the command line as follows:

~~~bash
python soil2PALM.py
~~~

Please note that you may need to adjust the data paths and function arguments to match your data.

## Dependencies
* GeoPandas
* pandas
* os
* rasterio

## Limitations
This script assumes that the soil data files are in a specific format and contain certain elements. If your data files have a different format or do not contain these elements, the script may not work as expected.

