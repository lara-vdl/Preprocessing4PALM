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

## alkis2PALM.py
This python script translate the ALKIS current use data to PALM surface types (pavement, vegetation and water). ALKIS consists of several individual layers describing the current use of an area. Some of those layers can directly be translated into a PALM surface type. Other layers are translated to PALM surface types based on the attribute "funktion" (function) or "vegetationsmerkmal" (vegetation characteristic). The translation for those layers is conducted with translation tables. As some features have NAN values in their attributes, a PALM surface type is assigned based on the ALKIS layer from which they originate.

As garden areas and other green areas within typically urban classes are not separately defined in ALKIS, they are identified using the Copernicus Imperviousness dataset. Similarly, sealed areas within sports facilites are identified. Furthermore, the railway layer contains subway line which should not be visible in a surface classification. These areas are removed by overlaying other ALKIS layers. 

As each ALKIS layer has to be handled differently, a dictionary is defined with the file name, layer name within the xml file, whether to translate to whole layer or with a translation table, how NAN values are replaced and refinements to be made. An example dictionary is provided and currently contains the city of Bochum.

Finally, the resulting shapefile with all ALKIS layers translated to PALM classes is saved. It is also rasterised into a pavement raster and a land use raster (combination of vegetation and water) and saved as GeoTiff.

Required input data:
* ALKIS current use data for a city (.xml file)
* dictionary file defining the operations for each ALKIS layer for a city (.json file)
* translation tables as csv files
* csv file with names of PALM classes for visualisation purposes
* Copernicus imperviousness raster
* Shapefile with region of interest for clipping

Output:
* Shapefile with PALM surface types
* raster file with pavement types
* raster file with land use (combination of vegetation and water types)