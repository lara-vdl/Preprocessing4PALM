import geopandas as gpd
import pandas as pd
import os
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
from geocube.vector import vectorize
import xarray as xr
import rioxarray as rio
import shapely

# set data paths
data_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use/CLC"
keys_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use"
outpath = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/land_use/processed"

# define functions
def rasteriseSurface(gdf:gpd.GeoDataFrame,column:str,resolution:float) -> None:
    '''
    Rasterises the processed ALKIS dataset with a desired resolution and converts to values to integer
    '''
    output_raster_path = os.path.join(outpath,f"clc_palm_{column}.tif")

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

        # 
        #raster = raster.astype('float32')
        
        # Write the raster data to the output raster
        dst.write(raster, 1)

def translateCLC(clip_file:str, clc_file:str, key_file:str, layername= "U2018_CLC2018_V2020_20u1",epsg=25832) -> tuple[gpd.GeoDataFrame,gpd.GeoDataFrame]:
    # read and clip data
    clipper = gpd.read_file(os.path.join(data_path,clip_file))
    clc = gpd.read_file(os.path.join(data_path, clc_file), layer=layername, mask = clipper)
    clc = clc.clip(clipper)
    clc.to_crs(epsg, inplace=True)

    # read translation table
    keys = pd.read_csv(os.path.join(keys_path,key_file))

    # transform clc code_18 column to integer
    clc["Code_18"] = pd.to_numeric(clc["Code_18"])

    # merge geodataframe and pandas dataframe
    clc_palm = clc.merge(keys, how="left", on="Code_18")

    # create land_use column from combination of vegetation and water for later use in GEO4PALM
    clc_palm["land_use"] = clc_palm["vegetation"]
    clc_palm["land_use"] = np.where(clc_palm["water"].notna(), clc_palm["water"] + 20, clc_palm["land_use"])

    # return geodataframe
    return clc_palm, clipper

# read and translate CLC
clc_palm, clipper = translateCLC("clip_clc_3035.shp","U2018_CLC2018_V2020_20u1_gpkg.gpkg","CLC_key.csv")

# keep only relevant columns
clc_palm = clc_palm[["Code_18","CLC_text","pavement","vegetation","water","geometry"]]

# combine with named PALM class table for visualisation purposes
class_names = pd.read_csv(os.path.join(keys_path,"PALM_classes.csv"))

clc_palm_named = clc_palm.merge(class_names, on=["pavement","vegetation","water"], how="left")

# save shapefile
clc_palm_named.to_file(os.path.join(outpath,"clc_palm.shp"))
print("saved shapefile")

# rasterise 
rasteriseSurface(clc_palm,"pavement",32.0)
rasteriseSurface(clc_palm,"land_use",32.0)