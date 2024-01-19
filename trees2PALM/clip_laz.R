# tree detection with lidR
library(lidR)
library(raster)
library(sf)
library(data.table)
library(terra)

setwd("your working directory")

# create a filelist of all las files
lasfiles <- list.files("laz", pattern = ".laz$", full.names = F)

# create a filelist of all dem files
demfiles <- list.files("dem", pattern = ".tif$", full.names = F)

# create a filelist of all mask files
maskfiles <- list.files("mask", pattern = ".shp$", full.names = F)

# create a loop through all las files
for (i in 1:length(lasfiles)) {
  print(paste("start loop",i,"of",length(lasfiles)))
  
  # read las file
  las <- readLAS(paste0("laz/", lasfiles[i]), select = "xyzr", filter = "-drop_single -keep_class 1 2 20")
  
  # read dem file
  dem <- raster(paste0("dem/", demfiles[i]))
  
  # read tree mask
  build <- st_read(paste0("mask/", maskfiles[i]), quiet=T)
  
  # clip las file with tree mask
  starttime <- Sys.time()
  print(paste("clip started at", starttime))
  
  las_clip <- clip_roi(las, build)
  
  endtime <- Sys.time()
  print(paste("clip finished after:",difftime(endtime, starttime, units = "mins")))
  
  # classify noise
  las_clip <- classify_noise(las_clip, sor(k=20,m=1))
  
  # normalise las
  nlas <- las_clip - dem
  
  writeLAS(nlas, paste0("clipped_laz/clipped_", lasfiles[i]))
}
