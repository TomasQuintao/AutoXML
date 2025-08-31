from platformdirs import user_data_dir
import os, shutil


def createProject(datasetID, dtd_file, xml_file, raw_data_folder, outdir='default', overwrite=False):
    
    if (outdir == 'default'):
        
        outdir = user_data_dir('Projects', 'AutoXML')
    
    project_dir = os.path.join(outdir, datasetID)
    
    if os.path.exists(project_dir):
        
        if overwrite:
            shutil.rmtree(project_dir)
        else:
            msg = (f"A project with datasetID '{datasetID}' already exists at {project_dir}." +
                   " Set createProject(overwrite=True) to overwrite the existing project.")
            raise FileExistsError(msg)
    
    os.makedirs(project_dir, exist_ok=False)
    
    shutil.copy(xml_file, os.path.join(project_dir, f"{datasetID}.xml"))
    shutil.copy(dtd_file, os.path.join(project_dir, f"{datasetID}.dtd"))
    
    raw_data_dir = os.path.join(project_dir, f"raw_{datasetID}")
    shutil.copytree(raw_data_folder, raw_data_dir)

    print(f"Project <{datasetID}> created. Saved to:\n{project_dir}")
    
    return project_dir
    
createProject("postcards",
              r"C:\Users\tomas\Documents\Tese\AutoXML\data\postcards\postcards.dtd",
              r"C:\Users\tomas\Documents\Tese\AutoXML\data\postcards\postcards.xml",
              r"C:\Users\tomas\Documents\Tese\AutoXML\data\postcards\raw_postcards",
              overwrite=True
             )