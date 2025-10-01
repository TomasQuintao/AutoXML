from platformdirs import user_data_dir
from pathlib import Path
import os

def create_log_file(datasetID):
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    log_path = os.path.join(dataset_path, "LM_logs.txt")
    path = Path(log_path)
    
    path.open("w", encoding="utf-8").close() 
    
    return log_path

def log_history(history, datasetID):
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    log_path = os.path.join(dataset_path, "LM_logs.txt")
    
    with open(log_path, 'r', encoding='utf-8') as f:
        logs = f.read()
     
    logs += "\n\n" + '='*50 + "\n"
    for key in history:
        logs += key + '\n' + str(history[key]) + '\n\n'
        
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(logs)
