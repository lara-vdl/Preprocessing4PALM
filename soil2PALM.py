import geopandas as gpd
import pandas as pd
import os
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize

# set data paths
data_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/soil/ISBK50"
keys_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/soil"
outpath = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/soil/processed"

# define functions
def rasteriseSoil(gdf:gpd.GeoDataFrame,column:str,resolution:float) -> None:
    '''
    Rasterises the processed ALKIS dataset with a desired resolution and converts to values to integer
    '''
    output_raster_path = os.path.join(outpath,f"soil_palm_{column}.tif")

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

def translateSoil(clip_file:str, soil_file:str, key_file:str,epsg=25832) -> gpd.GeoDataFrame:
    # read and clip data
    clipper = gpd.read_file(os.path.join(data_path,clip_file))
    soil = gpd.read_file(os.path.join(data_path, soil_file), mask = clipper)
    soil = soil.clip(clipper)

    # read translation table
    keys = pd.read_csv(os.path.join(keys_path,key_file))

    # merge geodataframe and pandas dataframe
    soil_palm = soil.merge(keys, how="left", on="ART")

    # return geodataframe
    return soil_palm

# read and translate soil
soil_palm = translateSoil("clip_clc.shp","BK50.shp","BK50_PALM.csv")

# keep only relevant columns
soil_palm = soil_palm[["ART","Text","soil_type","PALM_text","geometry"]]

# save shapefile
soil_palm.to_file(os.path.join(outpath,"soil_palm.shp"))
print("saved shapefile")

# rasterise 
rasteriseSoil(soil_palm,"soil_type",32.0)