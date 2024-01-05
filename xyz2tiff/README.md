# xyz2tiff.py

This Python script is used to resample GeoTIFF files to a desired resolution and merge them into one file.

## Functionality

The script contains one main function:

1. `resample_geotiff(input_path:str, output_path:str, target_resolution:float, epsg=25832) -> None`:
   This function imports an elevation raster dataset and resamples it to a desired resolution. The resampled files are saved as GeoTIFF.

In the main execution block, the script:

1. Sets the path to the elevation data.
2. Creates a list of .xyz files in the elevation data directory.
3. Extracts only the file name without the whole path.
4. Defines the target resolution.
5. Loops through the file list and resamples each raster file to the desired resolution using the `resample_geotiff` function.
6. Combines the resampled raster files into one.

## Input data
* elevation data as .xyz files

## Output
* individual GeoTiff files
* one merged GeoTiff file

## Usage

To use this script, you need to have gdal, os, and glob libraries installed in your Python environment. You can run the script from the command line as follows:

```bash
python xyz2tiff.py
```
Please note that you may need to adjust the `dem_path` variable to point to the directory containing your elevation data and the `target_resolution` variable to set your desired resolution.

## Dependencies
* gdal
* os
* glob

## Limitations
This script assumes that the elevation data files are in .xyz format and have a specific structure. If your data files have a different format or structure, the script may not work as expected.