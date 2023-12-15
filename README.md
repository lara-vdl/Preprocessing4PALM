# Preprocessing4PALM
## General
Repository for a collection of scripts to preprocess geodata for the PALM model. 

Input data for the PALM model that is currently considered:
* elevation data
* land cover or use
* soil types
* trees

No warranty and no support.

## xyz2tiff.py
This python script edits elevation data from German open data portals. The elevation data is usually provided as .xyz files covering an area of 1 km<sup>2</sup> These files are read and resampled to a desired resolution. The files are then saved as GeoTiff files. Finally the individual GeoTiff files are merged into one file.

Required input data:
* elevation data as .xyz files

Output:
* individual GeoTiff files
* one merged GeoTiff file