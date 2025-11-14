# import libraries
import geopandas as gpd
import pandas as pd
import os
import numpy as np
import xarray as xr
import rioxarray as rio
from geocube.vector import vectorize
import shapely
import json
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
import fiona
from shapely.geometry import shape

# set data paths
data_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use"
alkis_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use/ALKIS/bo_nutzung"
keys_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use/translation_tables"
outpath = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use/processed"

# define gloabl variables
with open(os.path.join(data_path,"alkis_dict.json")) as jsonFile:
    layers = json.load(jsonFile)

# define functions
def readClipper(file:str) -> gpd.GeoDataFrame:
    '''
    Reads the clipper (shapefile) as a Geodataframe
    '''
    filepath = os.path.join(data_path,file)
    return gpd.read_file(filepath)

def readAndClipLayers(filename:str, layername:str, clipper:gpd.GeoDataFrame, epsg = 25832) -> gpd.GeoDataFrame:
    '''
    Reads the ALKIS layer (xml file) into a Geodataframe and clips to desired extent with a clipper Geodataframe
    '''
    # Open the file with Fiona
    with fiona.open(os.path.join(alkis_path,filename), driver="GML", layer=layername) as src:
        # Create a new GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features([feature for feature in src if shape(feature['geometry']).is_valid])

    # Set the CRS
    gdf = gdf.set_crs(epsg)

    # Clip the GeoDataFrame
    clipped = gdf.clip(clipper, keep_geom_type=True)
    return clipped

def readKeyTable(file:str) -> pd.DataFrame:
    '''
    Reads the translation tables (csv file) as pandas dataframe
    '''
    return pd.read_csv(os.path.join(keys_path,file))


def replaceNA(config:str, layer:gpd.GeoDataFrame, value:float, columnToOverwrite:str) -> gpd.GeoDataFrame:
    '''
    Function to replace NAN values in a Geodataframe based on a configuration \n
    When ALKIS layers are mapped to PALM classes based on an attribute, not all features may receive a PALM class. \n
    Those features receive a value for either the vegetation or pavement column based on the ALKIS layer from which they originate. 
    ''' 
    if config == "veg":
        layer.loc[(layer["vegetation"].isna()),columnToOverwrite] = value
        return layer

    if config == "pav":
        layer.loc[(layer["pavement"].isna()),columnToOverwrite] = value
        return layer

    if config == "vegAndPav":
        layer.loc[(layer["pavement"].isna() & layer["vegetation"].isna()),columnToOverwrite] = value
        return layer

def vectoriseImperviousness(rasterDs:str, clipper:gpd.GeoDataFrame, class_breaks:list) -> tuple[gpd.GeoDataFrame,gpd.GeoDataFrame]:
    '''
    Reads the imperviousness raster and reclassifies the degrees of imperviousness into three classes \n
    - 0 to 25%
    - 26 to 50%
    - more than 50% \n
    The raster is then vectorised and two Geodataframes with low imperviousness less than 25% and high imperviousness more than 50% are returned
    '''
    ## read imperviousness data and simplify
    imperv = rio.open_rasterio(os.path.join(data_path,rasterDs), masked=True).squeeze()

    # reproject to 25832
    imperv = imperv.rio.reproject(clipper.crs)

    # clip
    imperv_clip = imperv.rio.clip(clipper.geometry.values, clipper.crs)

    # reclassify raster
    classes = class_breaks
    imperv_class = xr.apply_ufunc(np.digitize, imperv_clip, classes)

    # polygonise with geocube and keep only imperviousness class 1
    imperv_class.name = "impervi"
    imperv_shape = vectorize(imperv_class.astype("int32"))

    imperv_low = imperv_shape[imperv_shape.impervi==1]
    imperv_high = imperv_shape[imperv_shape.impervi==3]

    return imperv_low, imperv_high


def identifyGreen(imperv_low:gpd.GeoDataFrame, alkis_edit:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    This function identifies green areas within areas currently defined as a PALM pavement (artificial) type 3.\n
    It intersects the Geodataframe with low imperviousness with the ALKIS Geodataframe and changes to columns accordingly.\n
    The intersected layer is then merged again with the ALKIS layer where the attributes are edited and the Geodataframe is returned.
    '''
    ## combine imperviousness and ALKIS
    # subset ALKIS with pavement type 3
    alkis_pave = alkis_edit[alkis_edit["pavement"] == 3.0]

    # intersect with imperviousness
    intersect = alkis_pave.overlay(imperv_low, how="intersection")

    # change column values, pavement to nan, vegetation to 8
    intersect["vegetation"] = 8.0
    intersect["pavement"] = np.nan

    # check if geometries are valid
    print(intersect.geometry.is_valid.all())
    print(alkis_edit.geometry.is_valid.all())

    alkis_palm1 = alkis_edit.overlay(intersect, how = "union")

    # change column values
    if "vegetation_2" in alkis_palm1:
        alkis_palm1.loc[alkis_palm1["vegetation_2"]==8.0,"pavement_1"]=np.nan
        alkis_palm1.loc[alkis_palm1["vegetation_2"]==8.0,"vegetation_1"]=8.0
        alkis_palm1.rename(columns={"funktion_1":"funktion","bezeichnung_1":"bezeichnung","pavement_1":"pavement","vegetation_1":"vegetation","water_1":"water"}, inplace=True)
    else:
        alkis_palm1.loc[alkis_palm1["vegetation"]==8.0,"pavement_1"]=np.nan
        alkis_palm1.rename(columns={"funktion_1":"funktion","bezeichnung_1":"bezeichnung","pavement_1":"pavement"}, inplace=True)

    return alkis_palm1

def identifySealed(imperv_high:gpd.GeoDataFrame, alkis_edit:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    This function identifies sealed areas within areas currently defined as a PALM vegetation type.\n
    It intersects the Geodataframe with low imperviousness with the ALKIS Geodataframe and changes to columns accordingly.\n
    The intersected layer is then merged again with the ALKIS layer where the attributes are edited and the Geodataframe is returned.
    '''
    ## combine imperviousness and ALKIS
    # subset ALKIS where pavement nan
    alkis_veg = alkis_edit[alkis_edit["pavement"].isna()]

    # intersect with imperviousness
    intersect = alkis_veg.overlay(imperv_high, how="intersection")

    # change column values, vegetation to nan, pavement to 3
    intersect["vegetation"] = np.nan
    intersect["pavement"] = 3.0

    # combine ALKIS with intersected df with union
    # set precision of coordinates (known geopandas bug)
    alkis_edit["geometry"] = shapely.set_precision(alkis_edit.geometry.values, 1e-6)
    intersect["geometry"] = shapely.set_precision(intersect.geometry.values, 1e-6)

    alkis_palm1 = alkis_edit.overlay(intersect, how = "union")

    # change column values
    alkis_palm1.loc[alkis_palm1["pavement_2"]==3.0,"pavement_1"]=3.0
    alkis_palm1.loc[alkis_palm1["pavement_2"]==3.0,"vegetation_1"]=np.nan
    alkis_palm1.rename(columns={"funktion_1":"funktion","bezeichnung_1":"bezeichnung","pavement_1":"pavement","vegetation_1":"vegetation","water_1":"water"}, inplace=True)

    return alkis_palm1

def overlayRail(city:str) -> None:
    '''
    Overlays the ALKIS rail layer with other layers defined in the dictionary to exclude subways 
    '''
    overlayed = None
    rail = None

    for layer in layers[city]:
        if layer["layername"] == "AX_Bahnverkehr": 
            rail = layer["clippedLayer"]
        if layer["overlayRail"]:
            overlayed = pd.concat([overlayed,layer["clippedLayer"]], ignore_index=True)

    rail = rail.overlay(overlayed, how="difference")

    for layer in layers[city]:
        if layer["layername"] == "AX_Bahnverkehr":
            layer["clippedLayer"] =  rail

def rasteriseSurface(gdf:gpd.GeoDataFrame,column:str,resolution:float) -> None:
    '''
    Rasterises the processed ALKIS dataset with a desired resolution and converts to values to integer
    '''
    output_raster_path = os.path.join(outpath,f"alkis_palm_{column}.tif")

    # Set the desired raster resolution and bounding box
    pixel_size = resolution  # Adjust this according to your needs
    minx, miny, maxx, maxy = gdf.total_bounds
    width = int((maxx - minx) / pixel_size)
    height = int((maxy - miny) / pixel_size)

    # Define the raster transform
    transform = from_origin(minx, maxy, pixel_size, pixel_size)

    # Define the CRS
    crs = gdf.crs

    # Create a new raster file
    with rasterio.open(output_raster_path, 'w', driver='GTiff', count=1, dtype='int16', width=width, height=height, transform=transform, crs=crs, nodata=-9999) as dst:
        # Handle NaN values and round to integers
        shapes = [
            (geom, int(round(value)) if not np.isnan(value) else -9999)
            for geom, value in zip(gdf.geometry, gdf[column])
        ]
        # Rasterize the GeoDataFrame into the new raster
        raster = rasterize(shapes, out_shape=(height, width), transform=transform)
        
        # Write the raster data to the output raster
        dst.write(raster, 1)

## translate ALKIS to PALM surface types
# step 1 read clipper and vectorise imperviousness
clipper = readClipper("clip.shp")

imperv_low, imperv_high = vectoriseImperviousness(
    rasterDs="Imperviousness/DATA/IMD_2018_010m_E41N31_03035_v020.tif",
    clipper = clipper
)

# read and clip the ALKIS layer before the loop
alkis = gpd.read_file(f"{alkis_path}/alkis.gpkg", layer="nutzung")

alkis = alkis.clip(clipper, keep_geom_type=True)

# Fill missing values with a placeholder (e.g., 0)
alkis["veg"] = alkis["veg"].fillna(0).astype(int)


# step 2 loop through dictionary which defines translation and further operations
for layer in layers["Berlin"]:
    print(layer["layername"])
    layer["editedLayer"] = alkis[alkis["bezeich"]==layer["layername"]]

    # translate to PALM classes either with translation table or as a whole layer
    if layer["mapOnAttribute"]:
        keyTable = readKeyTable(layer["keyTable"])
        if layer["mergeKeyOnFunction"]:
            layer["editedLayer"] = layer["editedLayer"].merge(keyTable, how="left", left_on="fkt", right_on="funktion")
        else:
            layer["editedLayer"] = layer["editedLayer"].merge(keyTable, how="left", left_on="veg", right_on="vegetationsmerkmal")
        
        # replace NAN values due to missing attributes in ALKIS layer
        layer["editedLayer"] = replaceNA(
            config = layer["replaceNA"]["config"],
            layer = layer["editedLayer"],
            value = layer["replaceNA"]["value"],
            columnToOverwrite = layer["replaceNA"]["column"]
        )
    else:
        layer["editedLayer"][layer["palmMapping"]["palmSurfaceType"]] = layer["palmMapping"]["palmValue"]

    # identify green areas in sealed classes and change to vegetation
    if layer["identifyGreen"]:
        # check if layer["clippedLayer"] is empty
        if layer["editedLayer"].empty:
            continue
        else:
            layer["editedLayer"]=identifyGreen(imperv_low,layer["editedLayer"])

    # identify sealed areas in sports and leisure facilities and change to pavement
    if layer["identifySealed"]:
        if layer["editedLayer"].empty:
            continue
        else:
            layer["editedLayer"]=identifySealed(imperv_high,layer["editedLayer"])

# create empty geodataframe for combined ALKIS layers
alkis_palm_all= gpd.GeoDataFrame()

# combine all ALKIS layers translated to PALM
for layer in layers["Berlin"]:
    alkis_palm_all = pd.concat([alkis_palm_all, layer["editedLayer"]])

# keep only necessary columns
alkis_palm_all = alkis_palm_all[["pavement","vegetation","water","geometry"]]

# combine with named PALM class table for visualisation purposes
class_names = pd.read_csv(os.path.join(data_path,"PALM_classes.csv"))

alkis_palm_named = alkis_palm_all.merge(class_names, on=["pavement","vegetation","water"], how="left")

# create land_use column from combination of vegetation and water for later use in GEO4PALM
alkis_palm_named["land_use"] = alkis_palm_named["vegetation"]
alkis_palm_named["land_use"] = np.where(alkis_palm_named["water"].notna(), alkis_palm_named["water"] + 20, alkis_palm_named["land_use"])

# save shapefile
alkis_palm_named.to_file(os.path.join(outpath,"alkis_palm_test.shp"))

# rasterise both layers
rasteriseSurface(alkis_palm_named,"pavement",2.0)
rasteriseSurface(alkis_palm_named,"land_use",2.0)