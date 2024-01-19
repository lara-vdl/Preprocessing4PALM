import geopandas as gpd
import pandas as pd
import os
import rasterio
from rasterstats import zonal_stats
import rioxarray as rio
import numpy as np
from rasterio.features import geometry_mask

## data paths
dem_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/dem"
tree_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/trees/processed"
lai_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/trees/lai"
dsm_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/trees/dsm"
chm_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/test_area/trees/chm"

def combine_tree_files(directory:str) -> gpd.GeoDataFrame:
    """
    Combines all tree files in a directory to a single GeoDataFrame.
    :param directory: path to directory containing tree files
    :return: GeoDataFrame containing all trees
    """
    tree_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".shp")]
    trees = gpd.GeoDataFrame()
    for file in tree_files:
        trees = pd.concat([trees, gpd.read_file(file)], ignore_index=True)
    return trees

def prepare_lai_raster(rasterDs:str, epsg=25832):
    """
    Prepares the raster file for zonal statistics.
    Reads and reprojects the raster file."""
    lai_rast = rio.open_rasterio(os.path.join(lai_path,rasterDs), masked=True).squeeze()

    # reproject to epsg 25832
    lai_rast = lai_rast.rio.reproject(epsg)

    # get lai as array and affine of raster
    lai = lai_rast.values * 0.0008
    lai_affine = lai_rast.rio.transform()

    return lai, lai_affine

def create_chm(demDS:str,dsmDS:str,clipper:gpd.GeoDataFrame):
    # Open the raster datasets
    with rasterio.open(os.path.join(dem_path, demDS)) as src1, rasterio.open(os.path.join(dsm_path, dsmDS)) as src2:
        # Read the datasets into arrays
        dem = src1.read(1)
        dsm = src2.read(1)

    # Subtract the datasets
    chm = dsm - dem

    # Create a mask from the GeoDataFrame
    mask = geometry_mask(clipper.geometry, transform=src1.transform, out_shape=src1.shape, invert=True)

    # Apply the mask to the difference raster
    clipped_chm = np.where(mask, chm, np.nan)

    # Save the result as a new raster file
    with rasterio.open(os.path.join(chm_path, "chm_city.tif"), 'w', driver='GTiff', height=clipped_chm.shape[0],
                    width=clipped_chm.shape[1], count=1, dtype=str(clipped_chm.dtype),
                    crs=src1.crs, transform=src1.transform) as dst:
        dst.write(clipped_chm, 1)

trees = combine_tree_files(tree_path)

# get lai raster files
lai, lai_affine = prepare_lai_raster("VI_20200805T104031_S2A_T32ULC-010m_V101_LAI.tiff")

# calculate zonal statistics
stats = zonal_stats(trees, lai, affine=lai_affine, stats=["mean","median","max"], nodata=-32768, geojson_out=True)

# create geodataframe from stats
lai_stats = gpd.GeoDataFrame.from_features(stats)
lai_stats.crs = "EPSG:25832"

# drop all rows where mean is nan
lai_stats = lai_stats.dropna(subset=["mean"])

# drop all rows where mean is smaller than 0.6
lai_stats = lai_stats[lai_stats["mean"] > 0.6]

# summarize lai stats by mean and max
lai_stats_means = lai_stats.agg({"mean":"mean","median":"mean","max":"mean"})
lai_stats_max = lai_stats.agg({"mean":"max","median":"max","max":"max"})

# combine stats and save
lai_stats_summary = pd.concat([lai_stats_means,lai_stats_max], axis=1).T
lai_stats_summary.to_csv(os.path.join(tree_path,"lai_stats_summary.csv"))

create_chm("tif/dem_city.tif","processed/dom_city.tif",lai_stats)