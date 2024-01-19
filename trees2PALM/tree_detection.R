# tree detection with lidR
library(lidR)
library(raster)
library(sf)
library(data.table)
library(terra)

setwd("your working directory")

# create a filelist of all las files
lasfiles <- list.files("clipped_laz", pattern = ".laz$", full.names = F)

# specify domain resolution
res = 2.5
tile_size = res**2

# create a loop through all las files
for (i in 1:length(lasfiles)) {
  print(paste("start loop",i,"of",length(lasfiles)))
  
  # read las file
  nlas <- readLAS(paste0("clipped_laz/", lasfiles[i]), select = "xyzr")
  
  # set negative values to zero
  nlas@data[["Z"]][nlas@data[["Z"]]<0] <- 0
  
  # new chm
  chm <- rasterize_canopy(nlas, 1, dsmtin(max_edge = 8))
  
  # filter objects smaller than 3 m
  nlas <- filter_poi(nlas, Z >= 3)
  
  # detect trees
  f <- function(x) {x * 0.2 + 3}
  heights <- seq(0,40,5)
  ws <- f(heights)
  ttops <- locate_trees(nlas, lmf(f))
  
  # tree segmentation
  algo <- dalponte2016(chm, ttops)
  nlas_seg <- segment_trees(nlas, algo)
  trees <- filter_poi(nlas_seg, !is.na(treeID))
  crowns <- crown_metrics(nlas_seg, func = .stdtreemetrics, geom = "convex")
  crowns <- crowns[crowns$convhull_area >= tile_size,]
  st_write(crowns, paste0("processed/trees", i, ".shp"))
}