import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Polygon

# set data paths
build_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/buildings/shp"
outpath = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/trees/mask"

def create_tree_mask(directory:str, outpath:str) -> gpd.GeoDataFrame:
    '''
    Function to create a tree mask from a directory of building shapefiles.
    Building geometries are simplified, buffered and dissolved by ID
    '''
    # Get a list of all building shapefiles in the directory
    shapefile_list = [file for file in os.listdir(directory) if file.endswith(".shp")]

    # Iterate over each shapefile and read it into a GeoDataFrame
    for shapefile in shapefile_list:
        # Read the shapefile into a GeoDataFrame
        gdf = gpd.read_file(os.path.join(directory, shapefile))

        # create unique ID for each GML ID
        gdf["ID"] = gdf.groupby("gml_id").ngroup()

        # Get the extent of the buildings
        minx, miny, maxx, maxy = gdf.geometry.total_bounds

        # Create a polygon from the extent
        polygon = Polygon([(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])

        # Create a new GeoDataFrame
        build_extend = gpd.GeoDataFrame([1], geometry=[polygon], crs=gdf.crs)

        # simplify, buffer and dissolve building geometries
        gdf.geometry = gdf.geometry.simplify(1)
        gdf.geometry = gdf.geometry.buffer(1)
        gdf = gdf.dissolve(by='ID')

        # create tree mask from difference of building extent and buildings
        tree_mask = gpd.overlay(build_extend, gdf, how='difference')

        # transform tree mask to geoseries
        tree_mask_geom = tree_mask.geometry

        # save tree mask
        tree_mask_geom.to_file(os.path.join(outpath, shapefile.replace("LoD2","tree_mask")))

create_tree_mask(build_path, outpath)