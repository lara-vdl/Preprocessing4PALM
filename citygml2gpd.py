import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd
import glob
import os

def parseGml(filePath: str) -> ET.ElementTree:
    """Reads GML File and returns it as an Element Tree."""
    eTree = ET.parse(filePath)
    rootNode = eTree.getroot()
    return rootNode

def findAllInETree(eTree: ET.ElementTree, query: str) -> list:
    """Finds all Nodes based on a query string and returns a list of all finds."""
    finds = eTree.findall(query)
    return finds

def posListToShapelyPolygon(posList: str) -> Polygon:
    """Converts PosList string into shapely Polygon."""
    if posList is not None:
        coords = posList.split()
        coordinates = [(float(coords[i]), float(coords[i + 1]), float(coords[i + 2])) for i in range(0, len(coords), 3)]

    # Create a Shapely Polygon
    shapely_polygon = Polygon(coordinates)

    return shapely_polygon

def addRowToGeoDataFrame(geoDataFrame: gpd.GeoDataFrame, newRow: dict) -> gpd.GeoDataFrame:
    """Adds a new row to an existing GeoDataFrame."""
    if geoDataFrame.empty:
        geoDataFrame = gpd.GeoDataFrame([newRow], geometry='geometry', crs=geoDataFrame.crs)
    else:
        new_gdf = gpd.GeoDataFrame([newRow], geometry='geometry', crs=geoDataFrame.crs)
        geoDataFrame = gpd.GeoDataFrame(pd.concat([geoDataFrame, new_gdf], ignore_index=True), crs=geoDataFrame.crs)
    return geoDataFrame

def extractHeightsAndGeometryFromGML(eTree: ET.ElementTree, geoDataFrame: gpd.GeoDataFrame, gmlID: str, function: str, buildingPart: bool) -> gpd.GeoDataFrame:
    """Extracts the height and Geometry from a building / roof surface."""
    
    heights = findAllInETree(eTree, ".//{http://www.opengis.net/citygml/building/1.0}measuredHeight")
    if len(heights) == 0: print(f"no height for {gmlID}")
    elif len(heights) > 1: print(f"height on {gmlID} might be lost...") 
    else: height = float(heights[0].text)

    roofSurfaces = findAllInETree(eTree, ".//{http://www.opengis.net/citygml/building/1.0}RoofSurface")
    if len(roofSurfaces) == 0: 
        print(f"no roofSurfaces for {gmlID}")
    else: 
        for rs in roofSurfaces:
            posLists = findAllInETree(rs, ".//{http://www.opengis.net/gml}posList")
            if len(posLists) == 0:
                print(f"no geometry for {gmlID}")
            elif len(posLists) == 1:
                geoDataFrame = addRowToGeoDataFrame(geoDataFrame, newRow = {
                    "gml_id": gmlID, 
                    "height": height, 
                    "function": function, 
                    "buildingPart": buildingPart,
                    "geometry": posListToShapelyPolygon(posLists[0].text)
                })
            else:
                for pl in posLists:
                    geoDataFrame = addRowToGeoDataFrame(geoDataFrame, newRow = {
                        "gml_id": gmlID, 
                        "height": height, 
                        "function": function, 
                        "buildingPart": buildingPart,
                        "geometry": posListToShapelyPolygon(pl.text)
                    })
    
    return geoDataFrame

def saveGeoDataFrameAsShape(filePath: str, geoDataFrame: gpd.GeoDataFrame): 
    geoDataFrame.to_file(filePath)   

if __name__ == "__main__":
    build_path = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/buildings/LOD2"
    filePathList = glob.glob(os.path.join(build_path,'*.gml'))

    #filePath = "/media/lara/2TB SSD/sciebo/Promotion/01_PALM_Evaluation/dev_geodata/buildings/LOD2/LoD2_32_376_5706_1_NW.gml"
    for filePath in filePathList:
        rootNodeGml = parseGml(filePath)

        data = gpd.GeoDataFrame(
            columns=["gml_id", "height", "function", "buildingPart"],
            geometry=[],
            crs="EPSG:25832",
        )

        buildings = findAllInETree(rootNodeGml, ".//{http://www.opengis.net/citygml/building/1.0}Building")

        for building in buildings:

            gmlID = building.attrib['{http://www.opengis.net/gml}id']
            function = None
            height = None
            buildingPart = None
            geometry = None

            buildingParts = findAllInETree(building, ".//{http://www.opengis.net/citygml/building/1.0}BuildingPart")

            functions = findAllInETree(building, ".//{http://www.opengis.net/citygml/building/1.0}function")
            
            if len(functions) == 0: print(f"no function for {gmlID}")
            elif len(functions) > 1: print(f"function on {gmlID} might be lost...") 
            else: function = functions[0].text

            if len(buildingParts) == 0:
                data = extractHeightsAndGeometryFromGML(building, data, gmlID, function, False)
            else:
                for bp in buildingParts:
                    data = extractHeightsAndGeometryFromGML(bp, data, gmlID, function, True)

        saveGeoDataFrameAsShape(os.path.join(build_path,filePath.replace(".gml", ".shp")), data)