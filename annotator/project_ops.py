from platformdirs import user_data_dir
import os, shutil


def createProject(datasetID, dtd_file, xml_file, raw_data_folder, outdir='default', overwrite=False):
    
    if (outdir == 'default'):
        
        outdir = user_data_dir('Projects', 'AutoXML')
    
    project_dir = os.path.join(outdir, datasetID)
    
    if not os.path.isfile(dtd_file):
        raise FileNotFoundError(f"DTD file not found: {dtd_file}")
    if not os.path.isfile(xml_file):
        raise FileNotFoundError(f"XML file not found: {xml_file}")
    if not os.path.isdir(raw_data_folder):
        raise FileNotFoundError(f"Raw data folder not found: {raw_data_folder}")
    
    if os.path.exists(project_dir):
        if overwrite:
            shutil.rmtree(project_dir)
        else:
            msg = (f"A project with datasetID '{datasetID}' already exists at {project_dir}." +
                   " Set flag --overwrite to overwrite the existing project.")
            raise FileExistsError(msg)
    
    os.makedirs(project_dir, exist_ok=False)
    
    shutil.copy(xml_file, os.path.join(project_dir, f"{datasetID}.xml"))
    shutil.copy(dtd_file, os.path.join(project_dir, f"{datasetID}.dtd"))
    shutil.copytree(raw_data_folder, os.path.join(project_dir, f"raw_{datasetID}"))

    print(f"Project <{datasetID}> created. Saved to:\n{project_dir}")
    
    return project_dir


def listProjects():
    
    outdir = user_data_dir('Projects', 'AutoXML')
    
    projects = os.listdir(outdir)
    
    if (len(projects) > 0):
        print("Projects:")
        for project in projects:
            print(f" ->{project}")
    else:
        print("No projects yet. Use autoxml create to start a project.")
    
    print(f"(Located at: {outdir})")
    
    return outdir
    
# createProject("postcards",
              # r"C:\Users\tomas\Documents\Tese\AutoXML\data\postcards\postcards.dtd",
              # r"C:\Users\tomas\Documents\Tese\AutoXML\data\postcards\postcards.xml",
              # r"C:\Users\tomas\Documents\Tese\AutoXML\data\postcards\raw_postcards",
              # overwrite=True
             # )