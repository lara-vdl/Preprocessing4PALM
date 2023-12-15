from lxml import etree
import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd
from xml.etree import ElementTree

pathToGml = r"<ENTER PATH TO GML HERE>"

def gmlToShapelyPolygon(gml_polygon: str) -> Polygon:
    #print(gml_polygon)
    
    if gml_polygon == "N/A":
        return None
    else:
        # Parse the GML string
        root = ElementTree.fromstring(gml_polygon)

        # Extract coordinates from the GML
        coordinates = []
        pos_list = root.find(".//{http://www.opengis.net/gml}posList")
        if pos_list is not None:
            coords = pos_list.text.split()
            coordinates = [(float(coords[i]), float(coords[i + 1]), float(coords[i + 2])) for i in range(0, len(coords), 3)]

        # Create a Shapely Polygon
        shapely_polygon = Polygon(coordinates)

        return shapely_polygon

def addGmlToGeoDataFrame(gdf: gpd.GeoDataFrame, gmlId: str, height: float, function: str, buildingPart: bool, geometry: str):
    newRow = {"gml_id": gmlId, "height": height, "function": function, "buildingPart": buildingPart, "geometry": gmlToShapelyPolygon(geometry)}
    new_gdf = gpd.GeoDataFrame([newRow], geometry='geometry', crs=gdf.crs)
    return gpd.GeoDataFrame(pd.concat([gdf, new_gdf], ignore_index=True), crs=gdf.crs)

def extract_building_parts_with_geometry(citygml_file):
    data = gpd.GeoDataFrame(
        columns = [
            "gml_id",
            "height",
            "function",
            "buildingPart"
        ],
        geometry= [],
        crs="EPSG:25832"
    )
    
    tree = etree.parse(citygml_file)
    root = tree.getroot()

    # Extract namespaces from the root element
    nsmap = root.nsmap

    # Define namespaces for XPath queries
    ns = {
        'core': nsmap.get('core', ''),
        'gml': nsmap.get('gml', ''),
        'bldg': nsmap.get('bldg', ''),
    }

    # Find all Building elements
    building_elements = root.findall('.//bldg:Building', namespaces=ns)

    for building_element in building_elements:
        gml_id = building_element.get('{http://www.opengis.net/gml}id')

        # Check if measuredHeight element exists
        measured_height_element = building_element.find('./bldg:measuredHeight', namespaces=ns)
        measured_height = measured_height_element.text if measured_height_element is not None else "N/A"

        function_element = building_element.find('./bldg:function', namespaces=ns)
        function = function_element.text if function_element is not None else "N/A"

        # Extract 2D geometry
        geometry_element = building_element.find('.//gml:Polygon', namespaces=ns)
        if geometry_element is not None:
            geometry_text = etree.tostring(geometry_element, pretty_print=True).decode()
        else:
            geometry_text = "N/A"

        data = addGmlToGeoDataFrame(data, gml_id, measured_height, function, False, geometry_text)

        # Find all BuildingPart elements within the current Building
        building_part_elements = building_element.findall('.//bldg:BuildingPart', namespaces=ns)

        for building_part_element in building_part_elements:
            part_gml_id = building_part_element.get('{http://www.opengis.net/gml}id')

            part_measured_height_element = building_part_element.find('./bldg:measuredHeight', namespaces=ns)
            part_measured_height = part_measured_height_element.text if part_measured_height_element is not None else "N/A"

            part_function_element = building_part_element.find('./bldg:function', namespaces=ns)
            part_function = part_function_element.text if part_function_element is not None else "N/A"

            # Extract 2D geometry for BuildingPart
            part_geometry_element = building_part_element.find('.//gml:Polygon', namespaces=ns)
            if part_geometry_element is not None:
                part_geometry_text = etree.tostring(part_geometry_element, pretty_print=True).decode()
            else:
                part_geometry_text = "N/A"

            data = addGmlToGeoDataFrame(data, gml_id, part_measured_height, part_function, True, part_geometry_text)

    return data

if __name__ == "__main__":
    citygml_file_path = pathToGml
    data = extract_building_parts_with_geometry(citygml_file_path)
    print(data)
