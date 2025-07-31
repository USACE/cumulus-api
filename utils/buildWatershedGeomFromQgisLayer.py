from qgis.core import *
from qgis.utils import iface
import processing
import math

### run in Qgis console with watershed selected as active layer


def get_buffered_rectangular_extents():
    active_layer = iface.activeLayer()

    if not active_layer:
        print("No active layer selected!")
        return None

    print(f"Processing layer: {active_layer.name()}")

    buffer_distance_meters = 2 * 1609.344
    layer_crs = active_layer.crs()

    # Define target CRS for final output (EPSG:5070)
    output_crs = QgsCoordinateReferenceSystem("EPSG:5070")

    # For buffering, use a suitable projected CRS
    if layer_crs.isGeographic():
        buffer_crs = QgsCoordinateReferenceSystem(
            "EPSG:3857"
        )  # Web Mercator for buffering
    else:
        buffer_crs = layer_crs

    # Set buffer distance (always in meters for this workflow)
    buffer_distance = buffer_distance_meters

    try:
        # Step 1: Fix invalid geometries first
        print("Fixing invalid geometries...")
        fixed_result = processing.run(
            "native:fixgeometries",
            {"INPUT": active_layer, "OUTPUT": "TEMPORARY_OUTPUT"},
        )
        fixed_layer = fixed_result["OUTPUT"]
        print("Geometries fixed")

        # Step 2: Get outline using the fixed layer
        outline_result = processing.run(
            "native:convexhull", {"INPUT": fixed_layer, "OUTPUT": "TEMPORARY_OUTPUT"}
        )
        outline_layer = outline_result["OUTPUT"]
        print("Created convex hull outline")

        # Step 3: Reproject to buffering CRS if needed
        if layer_crs.isGeographic():
            reprojected_result = processing.run(
                "native:reprojectlayer",
                {
                    "INPUT": outline_layer,
                    "TARGET_CRS": buffer_crs,
                    "OUTPUT": "TEMPORARY_OUTPUT",
                },
            )
            outline_layer = reprojected_result["OUTPUT"]
            print(f"Reprojected to {buffer_crs.authid()} for buffering")

        # Step 4: Buffer
        buffer_result = processing.run(
            "native:buffer",
            {
                "INPUT": outline_layer,
                "DISTANCE": buffer_distance,
                "SEGMENTS": 10,
                "END_CAP_STYLE": 0,
                "JOIN_STYLE": 0,
                "MITER_LIMIT": 2,
                "DISSOLVE": True,
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )
        buffered_layer = buffer_result["OUTPUT"]
        print(f"Applied 2-mile buffer")

        # Step 5: Get bounding box
        bbox_result = processing.run(
            "native:boundingboxes",
            {"INPUT": buffered_layer, "OUTPUT": "TEMPORARY_OUTPUT"},
        )
        bbox_layer = bbox_result["OUTPUT"]
        print("Created bounding box")

        # Step 6: Reproject to EPSG:5070 for final output
        final_result = processing.run(
            "native:reprojectlayer",
            {
                "INPUT": bbox_layer,
                "TARGET_CRS": output_crs,
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )
        bbox_layer_5070 = final_result["OUTPUT"]
        print(f"Reprojected to {output_crs.authid()}")

        extent = bbox_layer_5070.extent()

        # Round the extents appropriately
        # Round down western and southern extents, round up eastern and northern
        west = int(math.floor(extent.xMinimum()))
        east = int(math.ceil(extent.xMaximum()))
        south = int(math.floor(extent.yMinimum()))
        north = int(math.ceil(extent.yMaximum()))

        # Format as ST_GeomFromText with proper coordinate order
        st_geom_text = f"""ST_GeomFromText('Polygon ((
                        {west} {north},
                        {east} {north},
                        {east} {south},
                        {west} {south},
                        {west} {north}))',
                                5070),"""

        print("\n=== RESULTS ===")
        print(st_geom_text)

        # Also print individual coordinates for reference
        print(f"\nCoordinates (EPSG:5070):")
        print(f"West:  {west}")
        print(f"East:  {east}")
        print(f"South: {south}")
        print(f"North: {north}")
        print(f"Width: {east - west} meters")
        print(f"Height: {north - south} meters")

        # Add to map (optional)
        bbox_layer_5070.setName(f"{active_layer.name()}_2mile_extent_5070")
        QgsProject.instance().addMapLayer(bbox_layer_5070)
        print(f"\nAdded result to map: {bbox_layer_5070.name()}")

        return {
            "st_geom_text": st_geom_text,
            "west": west,
            "east": east,
            "south": south,
            "north": north,
            "extent": extent,
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


# Run the function
result = get_buffered_rectangular_extents()
