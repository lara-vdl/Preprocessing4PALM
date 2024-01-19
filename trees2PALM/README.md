# Tree data preparation

The tree data preparation consists of four subroutines which are described below.

Basically the routine:
1. Creates masks from building geometries which is inverted
2. Clips LIDAR point clouds with the created masks
3. Performs a tree detection on the clipped point clouds
4. Uses the detected tree geometries to derive a statistic of Leaf Area Index and to create a Canopy Height Model

Required input data:
- Shapefiles with building geometries
- LIDAR point clouds as .laz files
- Leaf Area Index Raster dataset, e.g. from Copernicus
- Digital Elevation model as .tif
- Digital Surface model as .tif

<br/>

# Building Tree Mask

This script, `build_tree_mask.py`, is used to create a tree mask from a directory of building shapefiles. The building geometries are simplified, buffered, and dissolved by ID.


## Function

`create_tree_mask(directory:str, outpath:str) -> gpd.GeoDataFrame`

This function creates a tree mask from a directory of building shapefiles. The building geometries are simplified, buffered, and dissolved by ID.

### Parameters

- `directory` (str): The directory where the building shapefiles are located.
- `outpath` (str): The output path where the resulting GeoDataFrame should be saved.

### Returns

- `gpd.GeoDataFrame`: A GeoDataFrame representing the tree mask.


## Usage

~~~bash
python build_tree_mask.py
~~~

## Dependencies

- geopandas
- pandas
- shapely

## Limitations

This script assumes that the building data files are in a specific format and contain certain elements. If your data files have a different format or do not contain these elements, the script may not work as expected.

<br/>

# Clip LIDAR point cloud

This script, `clip_laz.R`, is used to clip LIDAR point clouds. It reads in .laz, .tif, and .shp files, clips the .laz files with a tree mask, classifies noise, and normalizes the .laz files.

## Dependencies

- lidR
- raster
- sf
- data.table
- terra

## Functionality

The script performs the following steps:

1. Reads in .laz files from the "laz" directory.
2. Reads in .tif files from the "dem" directory.
3. Reads in .shp files from the "mask" directory.
4. Loops through all .laz files and performs the following operations for each:
   - Clips the .laz file with the corresponding tree mask.
   - Classifies noise in the .laz file.
   - Normalizes the .laz file using the corresponding .tif file.

## Input Data

The script uses the following data:

- LIDAR point clouds in .laz format
- Digital elevation models as .tif files
- tree masks as .shp files

## Output

The script produces the following output:

- Clipped LIDAR point clouds in .laz format

## Limitations

- The script assumes that the .laz, .tif, and .shp files are all in the correct directories and have matching names. If this is not the case, the script may fail or produce incorrect results.
- The script does not handle any errors or exceptions that might occur during the reading of the files or the processing of the data. If there are issues with the files or the data, the script may fail.
- The script uses hard-coded parameters for the classify_noise function. These parameters may not be appropriate for all datasets.

<br/>

# Tree Detection with lidR

This script, `tree_detection.R`, is used to perform tree detection using lidR. It reads in .laz files, processes them, and outputs shapefiles of detected trees.

## Dependencies

- lidR
- raster
- sf
- data.table
- terra

## Functionality

The script performs the following steps:

1. Reads in .laz files from the "clipped_laz" directory.
2. Loops through all .laz files and performs the following operations for each:
   - Reads the .laz file.
   - Sets negative Z values to zero.
   - Creates a canopy height model (CHM).
   - Filters out objects smaller than 3 m.
   - Detects trees using the variable window filter (VWF) method.
   - Segments the trees.
   - Filters out trees with a crown area smaller than the tile size.
   - Writes the tree crowns to a .shp file in the "processed" directory.

## Input Data

The script uses the following data:

- Clipped LIDAR point clouds in .laz format

## Output

The script produces the following output:

- Detected tree geometries as Shapefiles

## Limitations

- The script assumes that all .laz files are in the "clipped_laz" directory and that this directory exists. If this is not the case, the script may fail.
- The script does not handle any errors or exceptions that might occur during the reading of the .laz files or the processing of the data. If there are issues with the files or the data, the script may fail.
- The script uses hard-coded parameters for the tree detection and segmentation functions. These parameters may not be appropriate for all datasets.
- The script does not check if the output .shp files already exist. If they do, the script will overwrite them.

<br/>

# Processing Tree Data

This script, `process_tree_data.py`, is used to process tree data. It combines tree files, prepares LAI raster files, calculates zonal statistics, creates a canopy height model (CHM), and saves the results.

## Dependencies

- geopandas
- pandas
- rasterio
- numpy
- rasterstats
- os
- rioxarray

## Functionality

The script performs the following steps:

1. Combines all tree files in a directory into a single GeoDataFrame.
2. Prepares the LAI raster file for zonal statistics by reading and reprojecting it.
3. Calculates zonal statistics for the trees using the LAI raster.
4. Creates a GeoDataFrame from the zonal statistics and filters it based on the mean LAI.
5. Aggregates the LAI statistics by mean and max.
6. Saves the aggregated statistics as a .csv file.
7. Calculate a CHM by subtracting the DEM from the DSM and clips it to the filtered tree geometries

The `combine_tree_files` function performs the following steps:

1. Lists all shapefiles in the provided directory.
2. Initializes an empty GeoDataFrame.
3. Loops through each shapefile, reads it into a GeoDataFrame, and concatenates it to the existing GeoDataFrame.
4. Returns the combined GeoDataFrame.

The `prepare_lai_raster` function performs the following steps:

1. Opens the raster file and reads it into a DataArray.
2. Reprojects the DataArray to the specified EPSG code.
3. Multiplies the values in the DataArray by 0.0008 to convert them to the correct units.
4. Returns the values of the DataArray as a numpy array and the affine transformation of the DataArray.

The `create_chm` function performs the following steps:

1. Opens the DEM and DSM raster files and reads them into arrays.
2. Subtracts the DEM from the DSM to create a CHM.
3. Creates a mask from a GeoDataFrame and applies it to the CHM.
4. Saves the masked CHM as a new raster file.

## Input Data

The script uses the following data:

- Detected tree geometries as Shapefiles
- Digital elevation model as .tif file
- Digital surface model as .tif file
- Leaf Area Index Raster dataset

## Output

The script produces the following output:

- Leaf Area Index statistics (csv file)
- Canopy Height Model clipped to building geometries as .tif file

## Usage

~~~bash
python process_tree_data.py
~~~

## Limitations

- The script assumes that all .tif and .shp files are in the correct directories and have matching names. If this is not the case, the script may fail or produce incorrect results.
- The script does not handle any errors or exceptions that might occur during the reading of the files or the processing of the data. If there are issues with the files or the data, the script may fail.
- The script uses hard-coded parameters for the zonal statistics calculation. These parameters may not be appropriate for all datasets.
- The script does not check if the output .csv file already exists. If it does, the script will overwrite it.