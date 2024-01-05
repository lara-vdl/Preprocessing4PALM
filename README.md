
# Preprocessing4PALM

Repository for a collection of scripts to preprocess geodata for the PALM model. 

Input data for the PALM model that is currently considered:
* elevation data
* land cover or use
* soil types
* trees
* buildings

The scripts can be found in the subfolders. Each subfolder contains a README with a description of the workflow and required input data.

## Python packages

Python version used for development: 3.10.12

Required packages:
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
* gdal
* glob
* xml.etree.ElementTree
