import geopandas as gpd
import pandas as pd
import os
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize

# set data paths
build_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/buildings/Geb_BO"
zensus_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/buildings/Zensus"
outpath = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/buildings/processed"
clip_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/buildings"

def translateZensus(clip_file:str, grid_file:str, zensus_file:str, key_file:str, layername= "de_grid_laea_100m", epsg=25832) -> gpd.GeoDataFrame:
    '''
    This function translates the Zensus data to the PALM building types
    '''
    
    # read and clip data
    clipper = gpd.read_file(os.path.join(clip_path,clip_file))
    grid = gpd.read_file(os.path.join(zensus_path, grid_file), layer=layername, mask = clipper)
    grid = grid.clip(clipper)
    grid.to_crs(epsg, inplace=True)

    # read zensus data and reduce to building age
    zensus = pd.read_csv(os.path.join(zensus_path,zensus_file), encoding="latin_1")
    zensus = zensus[zensus["Merkmal"] == "BAUJAHR_MZ"]

    # read translation table
    keys = pd.read_csv(os.path.join(zensus_path,key_file))

    # merge geodataframe and pandas dataframe
    grid_zensus = grid.merge(zensus, how="left", left_on = "id", right_on="Gitter_ID_100m")
    zensus_palm = grid_zensus.merge(keys, how="left", on="Auspraegung_Code")

    zensus_palm = zensus_palm[['id', 'geometry','Gitter_ID_100m','Merkmal_x','Auspraegung_Code','Auspraegung_Text_x', 'building_type']]

    # return geodataframe
    return zensus_palm

def combine_shapefiles(directory:str, clip_file:str) -> gpd.GeoDataFrame:
    '''
    This function combines all shapefiles in a directory to one geodataframe and creates a unique ID for each GML ID
    The data is clipped to the domain extend
    '''
    # Get a list of all building shapefiles in the directory
    shapefile_list = [file for file in os.listdir(directory) if file.endswith(".shp")]

    # Create an empty GeoDataFrame to store the combined data
    buildings = gpd.GeoDataFrame()

    # Iterate over each shapefile and read it into a GeoDataFrame
    for shapefile in shapefile_list:
        # Read the shapefile into a GeoDataFrame
        gdf = gpd.read_file(os.path.join(directory, shapefile))
            
        # Concatenate the GeoDataFrame to the combined GeoDataFrame
        buildings = pd.concat([buildings, gdf], ignore_index=True)

    # create unique ID for each GML ID
    buildings["ID"] = buildings.groupby("gml_id").ngroup()

    # clip data
    clipper = gpd.read_file(os.path.join(clip_path,clip_file))
    buildings.geometry = buildings.geometry.buffer(0)
    buildings = buildings.clip(clipper)

    # drop all where function is 53001_1800, 53001_1806, 53001_1807, 53001_1808, 53001_1830
    buildings = buildings[~buildings["function"].isin(["53001_1800", "53001_1806", "53001_1807", "53001_1808", "53001_1830"])]
    
    return buildings

def rasteriseBuildings(gdf:gpd.GeoDataFrame,column:str,resolution:float,dtype:str,nodata:float,out_path:str) -> None:
    '''
    This function rasterizes the buildings to a given resolution and saves it as a GeoTiff
    '''
    # Set the desired raster resolution and bounding box
    pixel_size = resolution  
    minx, miny, maxx, maxy = gdf.total_bounds
    width = int((maxx - minx) / pixel_size)
    height = int((maxy - miny) / pixel_size)

    # Define the raster transform
    transform = from_origin(minx, maxy, pixel_size, pixel_size)

    # Create a new raster object with the specified parameters
    with rasterio.open(f"{out_path}/build_{column}.tif", 'w', driver='GTiff', height=height, width=width, count=1, dtype=dtype, crs=gdf.crs, transform=transform, nodata=nodata) as dst:
        # Rasterize the GeoDataFrame
        raster = rasterize(
            [(geom, float(value)) for geom, value in zip(gdf.geometry, gdf[column])],
            out_shape=(height, width),
            transform=transform,
            fill=nodata,
            all_touched=True,
            dtype=dtype
        )
        dst.write(raster, 1)

# translate Zensus data and read buildings
zensus_palm = translateZensus(clip_file="clip_3035.shp",grid_file="DE_Grid_ETRS89-LAEA_100m.gpkg",zensus_file="Geb100m.csv",key_file="keys_Zensus.csv")
buildings = combine_shapefiles(build_path,"clip.shp")

# Spatially join the dataframes
joined_df = gpd.sjoin(buildings, zensus_palm, how="left", predicate="intersects")

# Drop unnecessary columns
joined_df = joined_df.drop(columns=["index_right"])

# Fill NaN values in building_type column with 5
joined_df["building_type"].fillna(5, inplace=True)

# save as shapefile
joined_df.to_file(os.path.join(outpath,"buildings.shp"))

# rasterise buildings
rasteriseBuildings(joined_df,"building_type",5,"int16",-9999,outpath)
rasteriseBuildings(joined_df,"ID",5,"int32",-9999,outpath)
rasteriseBuildings(joined_df,"height",5,"float32",-9999,outpath)