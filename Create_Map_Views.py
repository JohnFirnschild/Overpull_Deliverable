"""
Create_Map_Views.py

This script will iterate through a list of layers,
It will Apply Symbolgy appropriatelya and 
and export a map view of each layer.

Not sure is this will work as a python script outside
of ArcGIS Pro.  We may want to consider creating a
custom tool for this using arcpy.GetParameterAsText.


Author: John Firnschild
Written: 2023-10-15
Version: 1.1

"""

import arcpy, os

# Set the workspace
arcpy.env.workspace = r"J:\John_Firnschild\APRX"

active_route = "LUMEN_LH_ROUTE_NA_OMA_DEM_EGNU_QWEST_SPAN_1"
active_mh = "LUMEN_MH_SPLICE_NA_OMA_DEM_EGNU_QWEST_SPAN_1"
active_sites = "LUMEN_SITES_NA_OMA_DEM_EGNU_QWEST_SPAN_1"
output_location = r"J:\ArcMap\Projects\DARK_FIBER_OVERPULL\GOOGLE_Overpull\TASK3119066_BGWZ0843_LUMEN_NA_OMA_DEM_EGNU_QWEST_GOOGLE_SPAN_1"

# Set the ArcGIS Pro project and map view
aprx = arcpy.mp.ArcGISProject("CURRENT")
# Use below if not in a current aprx
# aprx = arcpy.mp.ArcGISProject(r"J:\ArcMap\Projects\DARK_FIBER_OVERPULL\overpull.aprx")

# SET THE ACITVE MAP
m = aprx.activeMap
# LIST THE LAYERS
lyrList = m.listLayers()

# Define the layers you want to export
layer_variables = {
    "Route": m.listLayers(active_route)[0],
    "MH": m.listLayers(active_mh)[0],
    "Site": m.listLayers(active_sites)[0]
}

# Need to define symbology for each layer
route_symb = r"J:\ArcMap\Projects\DARK_FIBER_OVERPULL\LAYER_STYLE\OVERPULL_ROUTE.lyrx"
mhsp_symb = r"J:\ArcMap\Projects\DARK_FIBER_OVERPULL\LAYER_STYLE\OVERPULL_MHSPLICE.lyrx"
site_symb = r"J:\ArcMap\Projects\DARK_FIBER_OVERPULL\LAYER_STYLE\OVERPULL_SITES.lyrx"

# Apply symbology to each layer
def apply_symbology(layer_name, symbology_path):
    layer = m.listLayers(layer_name)[0]
    arcpy.management.ApplySymbologyFromLayer(
        in_layer=layer,
        in_symbology_layer=symbology_path,
        symbology_fields=None,
        update_symbology="DEFAULT"
    )

# Define the layers and symbology paths
layer_symbology = {
    active_route: route_symb,
    active_mh: mhsp_symb,
    active_sites: site_symb
}

# Apply symbology to each layer
for layer_name, symbology_path in layer_symbology.items():
    apply_symbology(layer_name, symbology_path)




# SET THE MAP VIEW
mv = aprx.activeView

# Calculate a buffer distance in map units (adjust this value as needed)
buffer_distance = 0.1  # Example: 10,000 map units

for layer_name, layer in layer_variables.items():
    # Specify layer visibility
    for lyr in layer_variables.values():
        lyr.visible = False
    layer.visible = True

    # Write SQL Query to select all features in the specified layer
    sql_query = '1=1'
    arcpy.management.SelectLayerByAttribute(layer, 'NEW_SELECTION', sql_query)

    # Zoom to all layers
    mv.zoomToAllLayers()

    # Modify the extent by adding a buffer around the features
    extent = mv.camera.getExtent()
    extent.XMin -= buffer_distance
    extent.YMin -= buffer_distance
    extent.XMax += buffer_distance
    extent.YMax += buffer_distance
    mv.camera.setExtent(extent)

    # Clear Selection
    arcpy.management.SelectLayerByAttribute(layer, 'CLEAR_SELECTION')

    # Export the map view
    output_file = os.path.join(output_location, f'{layer_name}_VIEW.png')
    mv.exportToPNG(output_file, width=500, height=500, world_file=True, color_mode="32-BIT_WITH_ALPHA")