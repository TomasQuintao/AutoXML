from platformdirs import user_data_dir
from threading import Thread
import os, shutil, webbrowser, subprocess, socket, time, re, threading, configparser, signal, requests
import xml.etree.ElementTree as ET

from annotator.utils.port_tools import wait_for_port
from annotator.utils.dtd_validator import validate_xml
from annotator.dtd_parser.functions import fix_attributes
from annotator.interface import app

def createProject(datasetID, dtd_file, xml_file, raw_data_folder, overwrite=False):
    
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
    # Also changes the other attributes to #IMPLIED to prevent errors later
    dtd_path = os.path.join(project_dir, f"{datasetID}.dtd")
    fix_attributes(
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
    
    # process = subprocess.Popen(
        # ["py", "-m", "annotator.interface"], 
        # stdout=subprocess.PIPE, 
        # stderr=subprocess.STDOUT, 
        # text=True
    # )

    # host, port = None, None

    # for line in iter(process.stdout.readline, ''):
        # print(line, end='')
        # match = re.search(r"Running on http://([\d\.]+):(\d+)", line)
        
        # if match:
            # host, port = match.group(1), int(match.group(2))
            # break

    # if host is None or port is None:
        # print("Could not detect Flask server host and port.")
        # process.terminate()
        # return

    host, port = "127.0.0.1", 5000
    url = f"http://{host}:{port}/Projects/{datasetID}"

    flask_thread = Thread(target=lambda: app.run(host=host, port=port, debug=False))
    flask_thread.start()
    
    def handle_sigint(sig, frame):
        print("\nCtrl+C detected, shutting down Flask server...")
        try:
            requests.post(f"http://{host}:{port}/shutdown")
        except Exception:
            pass
        exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        wait_for_port(host, port)
    except TimeoutError:
        print(f"Flask did not start in {timeout}s. Shutting down...")
        try:
            requests.post(f"http://{host}:{port}/shutdown")
        except Exception:
            pass
        return

    # Open browser after server is ready
    webbrowser.open(url)
    print(f"Opening project '{datasetID}' at {url}")

    # Keep main thread alive so Flask thread keeps running
    try:
        while flask_thread.is_alive():
            flask_thread.join(timeout=1)
    except KeyboardInterrupt:
        # Fallback if Ctrl+C was not caught by signal
        print("\nKeyboardInterrupt detected, shutting down Flask server...")
        try:
            requests.post(f"http://{host}:{port}/shutdown")
        except Exception:
            pass

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
