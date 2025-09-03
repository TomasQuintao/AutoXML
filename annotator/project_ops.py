from platformdirs import user_data_dir
import os, shutil, webbrowser, subprocess, socket, time, re, threading, configparser
import xml.etree.ElementTree as ET

from utils.port_tools import wait_for_port
from utils.dtd_validator import validate_xml
from dtd_parser.functions import add_attributes

def createProject(datasetID, dtd_file, xml_file, raw_data_folder, outdir='default', overwrite=False):
    
    if (outdir == 'default'):
        
        outdir = user_data_dir('Projects', 'AutoXML')
    
    project_dir = os.path.join(outdir, datasetID)
    
    # Check if the files exist
    if not os.path.isfile(dtd_file):
        raise FileNotFoundError(f"DTD file not found: {dtd_file}")
    if not os.path.isfile(xml_file):
        raise FileNotFoundError(f"XML file not found: {xml_file}")
    if not os.path.isdir(raw_data_folder):
        raise FileNotFoundError(f"Raw data folder not found: {raw_data_folder}")
    
    # Check if the project already exists
    if os.path.exists(project_dir):
        if overwrite:
            shutil.rmtree(project_dir)
        else:
            msg = (f"A project with datasetID '{datasetID}' already exists at {project_dir}." +
                   " Set flag --overwrite to overwrite the existing project.")
            raise FileExistsError(msg)
    
    # Check if xml respects the DTD
    (valid, msg) = validate_xml(dtd_file, xml_file)
    if not valid:
        raise ValueError(f"XML validation failed: {msg}")
    
    os.makedirs(project_dir, exist_ok=False)
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    tag = root[0].tag
    
    # Creating a file containing all data with 
    # indication of annotation
    count = 0
    for doc in root:
        doc.set('id', str(count))
        doc.set('state', 'ready')
        count += 1
    
    for file in os.listdir(raw_data_folder):
        with open(os.path.join(raw_data_folder, file), "r", encoding="utf-8") as f:
            text = f.read()
        
        doc = ET.Element(tag)
        doc.text = text
        doc.set('id', str(count))
        doc.set('state', 'raw')
        count += 1
        
        root.append(doc)
    
    tree.write(os.path.join(project_dir, f"{datasetID}.xml"), encoding="utf-8", xml_declaration=True)
    
    # Adding the id and state attributes to the dtd
    dtd_path = os.path.join(project_dir, f"{datasetID}.dtd")
    add_attributes(
                   dtd_file,
                   tag,
                   [('id', 'CDATA', '#REQUIRED'), ('state', 'CDATA', '#REQUIRED')],
                   outpath=dtd_path
                   )

    print(f"Project <{datasetID}> created. Saved to:\n{project_dir}")
    return project_dir

def listProjects(display=True):
    
    outdir = user_data_dir('Projects', 'AutoXML')
    
    projects = os.listdir(outdir)
    
    if display:
        if (len(projects) > 0):
            print("Projects:")
            for project in projects:
                print(f" ->{project}")
        else:
            print("No projects yet. Use autoxml create to start a project.")
        
        print(f"(Located at: {outdir})")
    
    return projects
            
## TODO: Show the output of the server running
def openProject(datasetID):
    """Launch Flask app and open the browser for a project."""
    
    if datasetID not in listProjects(display=False):
        raise FileNotFoundError(f"Project '{datasetID}' does not exist." 
                                " Use command 'create' to start a project")
    
    # Start Flask server in a subprocess and capture stdout
    process = subprocess.Popen(
        ["py", "interface.py"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True
    )

    host, port = None, None

    # Parse Flask server output to get host and port
    for line in iter(process.stdout.readline, ''):
        print(line, end='')
        match = re.search(r"Running on http://([\d\.]+):(\d+)", line)
        
        if match:
            host, port = match.group(1), int(match.group(2))
            break

    if host is None or port is None:
        print("Could not detect Flask server host and port.")
        process.terminate()
        return

    try:
        # Wait until Flask server is ready
        wait_for_port(host, port)
        
        url = f"http://{host}:{port}/Projects/{datasetID}"
        webbrowser.open(url)
        print(f"Opening project '{datasetID}' at {url}")
        
    except TimeoutError as e:
        print(e)
        process.terminate()
        return

    # Keep process alive until manually closed
    process.wait()

def setModel(modelID):
    config_dir = user_data_dir('Config', 'AutoXML')
    os.makedirs(config_dir, exist_ok=True)  # ensure directory exists

    config_path = os.path.join(config_dir, 'config.ini')
    config = configparser.ConfigParser()
    
    if os.path.exists(config_path):
        config.read(config_path)

    if "Models" not in config:
        config["Models"] = {}

    config["Models"]["default"] = modelID

    with open(config_path, "w") as configfile:
        config.write(configfile)

    print(f"Config updated: default model set to {modelID}")
