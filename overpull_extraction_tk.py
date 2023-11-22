'''
Overpull Extraction Script
Version 1.1.3

This script does the following:

1. Prompts the user for input parameters
2. Creates a new directory
3. Exports the following feature classes to the new directory:
    a. Fiber based on PRO Circuit Name
    b. MH based on CLLI associated to FiberCables in in PRO Circuit
    c. Sites based on CLLI associated to FiberCables in in PRO Circuit
    d. LH Route based on Spatial relationship to Fiber

4. Creates a metadata file in the new directory
5. Sets the metadata for each feature class
6. Saves the metadata for each feature class

This script is intended to be used as a tool in ArcGIS Pro
to facilitate the extraction of Overpull OSP assets.

Author: John Firnschild
V1 ish Created Date approx: 2022-12-13
Revised Date: 2023-10-13

V 1.1
Revisions include:
    1. Corrected progress bar increments
    2. Added metadata creation
    3. Added error handling on task number and fiber count

V 1.1.3
Revisions include:
    1. Added tag_lh .replace for hyphen to underscore
    2. Modified the Directory Name to GDB description

'''

# Import necessary libraries
import arcpy
import os
import shutil
import re
import tkinter as tk
from tkinter import ttk
from tkinter import Label, Button, Entry, filedialog, messagebox

import time
from PIL import ImageTk, Image

# Set Input Variables
fiber = r"\\nadnp1b_cifs.corp.intranet\NNSGIS3\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.fibercable"
route = r"\\nadnp1b_cifs.corp.intranet\NNSGIS3\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.Route"
mh = r"\\nadnp1b_cifs.corp.intranet\NNSGIS3\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.MH_HH"
site = r"\\nadnp1b_cifs.corp.intranet\NNSGIS3\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.Building"

# Create the GUI window
root = tk.Tk()

# Set the window title
root.title("Overpull Extractor")

# Set the window size
root.geometry("650x800")

# Set the window icon
root.iconbitmap(fr"\\nadnp1b_cifs.corp.intranet\NNSGIS3\John_Firnschild\PYTHON_SCRIPTS\icon\vaultboy.ico")

# Load the company logo image
lumen_logo = ImageTk.PhotoImage(Image.open(fr"\\nadnp1b_cifs.corp.intranet\NNSGIS3\John_Firnschild\PYTHON_SCRIPTS\icon\LUMEN_Logo2.jpg"))

# Define the colors
light_blue = "#38c6f3"
dark_blue = "#0075c9"


# Define the function to simplify the customer string
def simplify_customer(customer):
    """
    Simplifies a customer name by removing punctuation and legal suffixes.

    Args:
        customer (str): The name of the customer to simplify.

    Returns:
        str: The simplified customer name.
    """
    # Remove any punctuation and extra whitespace
    customer = re.sub(r'[^\w\s]', '', customer).strip()
    # Split the string into a list of words
    words = customer.split()
    # Remove any common legal suffixes
    suffixes = ['inc', 'llc', 'ltd', 'corp', 'limited']
    words = [word.upper() if word.lower() not in suffixes else '' for word in words]
    # Rejoin the words into a single string without spaces
    simplified_customer = ''.join(words)
    return simplified_customer


class metadata_create:
    def __init__(self, path, tags, summary, description, accessConstraints):
        self.path = path
        self.metadata = arcpy.metadata.Metadata(self.path)
        self.metadata.tags = tags
        self.metadata.summary = summary
        self.metadata.description = description
        self.metadata.accessConstraints = accessConstraints
        self.metadata.save()

# Define the function to create the deliverable files
def create_deliverable():
    # Create the progress bar
    # progress_bar = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate")
    # progress_bar.grid(row=11, column=0, columnspan=3)

    # Get the values from the GUI elements
    customer = customer_entry.get()
    simplified_customer = simplify_customer(customer)  # simplify the customer string
    tasknum = tasknum_entry.get()
    if not tasknum:
        messagebox.showinfo("Error", "Task number cannot be empty.")
        return
    if tasknum[0].isdigit():
        messagebox.showinfo("Error", "Task number cannot start with a number.")
        return
    orderid = orderid_entry.get()
    tag_span = tag_span_entry.get()
    PROCircuitName = PROCircuitName_entry.get()
    fibercount_str = fibercount_entry.get()
    try:
        fibercount = int(fibercount_str)
    except ValueError:
        messagebox.showinfo("Error", "Fiber count must be a number.")
        return
    fibertype = fibertype_entry.get()
    fibers = fibers_entry.get()
    azcities = azcities_entry.get()
    # Need to add error handling for tag_lh
    tag_lh = tag_lh_entry.get()
    tag_lh = tag_lh.replace("-", "_")
    requestor = requestor_entry.get()
    parent_dir = parent_dir_entry.get()
    # Update progress bar value
    progress_bar["value"] = 10
    progress_bar.update()

    # Define the metadata strings
    tag_info = "LUMEN LH ROUTE MH SPLICE SITES"
    span = "SPAN"
    timestamp = time.strftime("%m-%d-%Y")
    # Modified Directory Name
    directory_name = f"{tasknum}_{PROCircuitName}_LUMEN_{tag_lh}_{simplified_customer}_{span}_{tag_span}"

    # Define the metadata file path
    # construct the full path to the working directory
    path = os.path.join(parent_dir, directory_name)

    if os.path.exists(path):
        # directory already exists, delete it
        shutil.rmtree(path)
        arcpy.AddMessage("Directory overwritten.")

    # create the new directory
    os.mkdir(path)
    arcpy.AddMessage("Directory created.")
    # worgdb = arcpy.management.CreateFileGDB(path, f"{directory_name}", "CURRENT")

    # Define GDB name and Create the file geodatabase
    worgdb = arcpy.management.CreateFileGDB(path, f"LUMEN_{tag_lh}_{simplified_customer}_{span}_{tag_span}", "CURRENT")
    file_path = os.path.join(path, "metadata.txt")

    # Update progress bar value
    progress_bar["value"] = 20
    progress_bar.update()

    # Write the metadata to the file
    tag = f"{tag_info} {tag_lh} {span} {tag_span} {PROCircuitName}"
    summary = f"{span} {tag_span} Overpull from {azcities} for {customer} deliverable {orderid}: on fibers {fibers}."
    description = f"{tasknum} {requestor} {timestamp}"
    accessConstraints = f"Disclose and distribute only to LUMEN and {customer} employees and authorized persons working on behalf of LUMEN and {customer} having a legitimate business need to know. Disclosure and distribution is prohibited without authorization."
    with open(file_path, "w") as file:
        file.write("\n".join([tag, summary, description, accessConstraints]))

    # Create Medadata
    with open(file_path, 'r') as f:
        metadata = f.readlines()

    tags = metadata[0].strip()
    summary = metadata[1].strip()
    description = metadata[2].strip()
    accessConstraints = metadata[3].strip()

    # Update progress bar value
    progress_bar["value"] = 30
    progress_bar.update()

    # Geoprocessing
    pcresults = ""
    fieldMappings = ""
    pcresults = arcpy.FeatureClassToFeatureClass_conversion(fiber, worgdb, f"{PROCircuitName}",
                                                            "SEGMENTID IN (SELECT SEGMENTIDFKEY FROM NX_DATA.FIBER WHERE NX_DATA.FIBER.SIGNALIPID IN(SELECT IPID FROM NX_DATA.SIGNAL WHERE NX_DATA.SIGNAL.CIRCUITNAME LIKE '%" + PROCircuitName + "%'))",
                                                            fieldMappings)

    # Update progress bar value
    progress_bar["value"] = 35
    progress_bar.update()

    idCur = arcpy.SearchCursor(pcresults)
    cnt = 0
    results = []
    for idResult in idCur:
        results.append(idResult.FROM_STRUCTURE)
        results.append(idResult.TO_STRUCTURE)
        cnt = cnt + 1
    del idCur
    pointquery = ("CLLI IN " + str(results).replace("[", "(").replace("]", ")"))

    mhsplice_del = arcpy.conversion.FeatureClassToFeatureClass(mh, worgdb,
                                                               fr"LUMEN_MH_SPLICE_{tag_lh}_{span}_{tag_span}",
                                                               pointquery,
                                                               'CLLI "CLLI-CAPID" true true false 100 Text 0 0,First,#,MH_HH_Layer2,CLLI,0,100;LONGITUDE "Longitude" true true false 8 Double 8 38,First,#,MH_HH_Layer2,LONGITUDE,-1,-1;LATITUDE "Latitude" true true false 8 Double 8 38,First,#,MH_HH_Layer2,LATITUDE,-1,-1;SPAN_ID "SPAN_ID" true true false 5 Text 0 0,First,#',
                                                               '')
    deliverable = metadata_create(mhsplice_del, tags, summary, description, accessConstraints)

    # Update progress bar value
    progress_bar["value"] = 40
    progress_bar.update()

    site_del = arcpy.conversion.FeatureClassToFeatureClass(site, worgdb, fr"LUMEN_SITES_{tag_lh}_{span}_{tag_span}",
                                                           pointquery,
                                                           r'CLLI "CLLI" true true false 100 Text 0 0,First,#,J:\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.building,CLLI,0,100;ADDRESS "Address" true true false 255 Text 0 0,First,#,J:\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.building,ADDRESS,0,255;CITY "City" true true false 150 Text 0 0,First,#,J:\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.building,CITY,0,150;TYPE "TYPE" true true false 20 Text 0 0,First,#,J:\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.building,BUILDING_TYPE,0,20;LONG "LONG" true true false 8 Double 8 38,First,#,J:\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.building,LONGITUDE,-1,-1;LAT "LAT" true true false 8 Double 8 38,First,#,J:\ArcMap\Connections\NXPRD3_GISREAD.sde\NX_DATA.TelecomDatasetProjection\NX_DATA.building,LATITUDE,-1,-1',
                                                           '')
    deliverable = metadata_create(site_del, tags, summary, description, accessConstraints)

    # Update progress bar value
    progress_bar["value"] = 50
    progress_bar.update()

    arcpy.management.CalculateField(site_del, "SPAN_ID", fr'"{tag_span}"', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(mhsplice_del, "SPAN_ID", fr'"{tag_span}"', "PYTHON3", '', "TEXT",
                                    "NO_ENFORCE_DOMAINS")

    # Update progress bar value
    progress_bar["value"] = 60
    progress_bar.update()

    route_sel = arcpy.management.SelectLayerByLocation(route, "SHARE_A_LINE_SEGMENT_WITH", pcresults, None,
                                                       "NEW_SELECTION", "NOT_INVERT")
    arcpy.SetParameter(2, pcresults)

    # Update progress bar value
    progress_bar["value"] = 70
    progress_bar.update()

    route_del = arcpy.conversion.FeatureClassToFeatureClass(route_sel, worgdb,
                                                            fr"LUMEN_LH_ROUTE_{tag_lh}_{span}_{tag_span}", '',
                                                            'INSTALL "INSTALL" true false false 255 Text 0 0,First,#,Route,INSTALLATION_METHOD,0,255;INTERCITY "INTERCITY" true true false 100 Text 0 0,First,#,Route,INTERCITY_MARKET,0,100;LEGACY "LEGACY" true false false 255 Text 0 0,First,#,Route,NETWORK_BUILDER,0,255;SPAN_NAME "SPAN NAME" true true false 255 Text 0 0,First,#,Route,SPAN_NAME,0,255;ORDER_ID "ORDER_ID" true true false 255 Text 0 0,First,#;CIRCUIT_ID "CIRCUIT_ID" true true false 255 Text 0 0,First,#;FIBERCOUNT "FIBERCOUNT" true true false 255 Long 0 0,First,#;FIBER_TYPE "FIBER_TYPE" true true false 255 Text 0 0,First,#;FIBERS "FIBERS" true true false 255 Text 0 0,First,#;A_Z_ID "A_Z_ID" true true false 255 Text 0 0,First,#',
                                                            '')
    deliverable = metadata_create(route_del, tags, summary, description, accessConstraints)

    # Update progress bar value
    progress_bar["value"] = 80
    progress_bar.update()

    arcpy.management.CalculateField(route_del, "A_Z_ID", fr'"{azcities}"', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(route_del, "ORDER_ID", fr'"{orderid}"', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(route_del, "CIRCUIT_ID", fr'"{PROCircuitName}"', "PYTHON3", '', "TEXT",
                                    "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(route_del, "FIBERS", fr'"{fibers}"', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(route_del, "FIBERCOUNT", fr'"{fibercount}"', "PYTHON3", '', "LONG",
                                    "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(route_del, "FIBER_TYPE", fr'"{fibertype}"', "PYTHON3", '', "TEXT",
                                    "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(route_del, "SPAN_ID", fr'"{tag_span}"', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    # Update progress bar to 100% and close root window
    progress_bar["value"] = 100
    progress_bar.update()

    # Show a pop-up message
    messagebox.showinfo("Export Complete", f"Your data has been exported to {worgdb}")

    # Close the GUI window
    root.destroy()








# Define the function to open a browse dialog
def browse_folder():
    folder_path = filedialog.askdirectory()
    parent_dir_entry.delete(0, tk.END)
    parent_dir_entry.insert(0, folder_path)


# Create the GUI elements
logo_label = Label(root, image=lumen_logo)
logo_label.pack()

customer_label = tk.Label(root, text="Customer:")
customer_label.pack()
customer_entry = tk.Entry(root)
customer_entry.pack()

tasknum_label = tk.Label(root, text="Task Number:")
tasknum_label.pack()
tasknum_entry = tk.Entry(root)
tasknum_entry.pack()

orderid_label = tk.Label(root, text="Order ID:")
orderid_label.pack()
orderid_entry = tk.Entry(root)
orderid_entry.pack()

tag_span_label = tk.Label(root, text="Span Number:")
tag_span_label.pack()
tag_span_entry = tk.Entry(root)
tag_span_entry.pack()

PROCircuitName_label = tk.Label(root, text="PRO Circuit Name:")
PROCircuitName_label.pack()
PROCircuitName_entry = tk.Entry(root)
PROCircuitName_entry.pack()

fibercount_label = tk.Label(root, text="Fiber Count:")
fibercount_label.pack()
fibercount_entry = tk.Entry(root)
fibercount_entry.pack()

fibertype_label = tk.Label(root, text="Fiber Type:")
fibertype_label.pack()
fibertype_entry = tk.Entry(root)
fibertype_entry.pack()

fibers_label = tk.Label(root, text="Fibers:")
fibers_label.pack()
fibers_entry = tk.Entry(root)
fibers_entry.pack()

azcities_label = tk.Label(root, text="AZ Cities:")
azcities_label.pack()
azcities_entry = tk.Entry(root, width=100)
azcities_entry.pack()

tag_lh_label = tk.Label(root, text="Fiber Intercity Market:")
tag_lh_label.pack()
tag_lh_entry = tk.Entry(root)
tag_lh_entry.pack()

requestor_label = tk.Label(root, text="Requestor:")
requestor_label.pack()
requestor_entry = tk.Entry(root)
requestor_entry.pack()

parent_dir_label = tk.Label(root, text="Parent Directory:")
parent_dir_label.pack()
parent_dir_entry = tk.Entry(root, width=100)
parent_dir_entry.pack()

browse_button = tk.Button(root, text="Choose Parent Directory", bg=dark_blue, fg="white", command=browse_folder)
browse_button.pack(pady=10)

create_button = tk.Button(root, text="Execute", bg=light_blue, fg="white", command=create_deliverable)
create_button.pack(pady=10)

# Create progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.pack(pady=10)

# Run the GUI loop
root.mainloop()
