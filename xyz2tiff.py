# import libraries
from osgeo import gdal, osr
import os
import glob

# set the path to the elevation data
dem_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/dem"

def resample_geotiff(input_path:str, output_path:str, target_resolution:float, epsg=25832)-> None:
    '''
    Function to import elevation raster dataset and resample it to a desired resolution \n
    Saves the resampled files as GeoTiff
    '''
    # Open the input raster
    input_dataset = gdal.Open(input_path)

    # Get the input geotransform and resolution
    input_geotransform = input_dataset.GetGeoTransform()
    input_resolution = abs(input_geotransform[1])  # assuming square pixels, use abs for safety

    # Calculate the output resolution
    output_resolution = target_resolution

    # Calculate the output size
    output_width = int(input_dataset.RasterXSize * (input_resolution / output_resolution))
    output_height = int(input_dataset.RasterYSize * (input_resolution / output_resolution))

    # Create the output raster
    output_dataset = gdal.GetDriverByName('GTiff').Create(
        output_path, output_width, output_height, input_dataset.RasterCount, gdal.GDT_Float32
    )

    # Set the geotransform and coordinate system of the output raster
    output_dataset.SetGeoTransform((
        input_geotransform[0], output_resolution, 0,
        input_geotransform[3], 0, -output_resolution
    ))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    #output_dataset.SetProjection(input_dataset.GetProjection())
    output_dataset.SetProjection(srs.ExportToWkt())

    # Perform the resampling using gdal.Warp
    gdal.Warp(output_dataset, input_dataset, resampleAlg=gdal.GRA_Bilinear)

    # Close the datasets
    input_dataset = None
    output_dataset = None

    print(f"Resampling complete. Output saved to {output_path}")

# create a list of a .xyz files in the elevation data directory
input_files = glob.glob(os.path.join(dem_path,'*.xyz'))

# extract only the file name without the whole path
xyz_files = [os.path.basename(file) for file in input_files]

# create an empty list for exported tif files
tif_files = []

# define the target resolution
target_resolution = 2.0

# loop through the file list and resample each raster file to the desired resolution
for file in xyz_files:
    input_geotiff = os.path.join(dem_path,file)
    output_geotiff = os.path.join(dem_path,file.replace("dgm1", f"dgm{int(target_resolution)}").replace(".xyz", ".tif"))
    tif_files.append(output_geotiff)
    resample_geotiff(input_geotiff, output_geotiff, target_resolution)

# combine the resampled raster files into one
merged = gdal.Warp(os.path.join(dem_path,'merged_raster.tif'), tif_files, format="GTiff")
merged = None
