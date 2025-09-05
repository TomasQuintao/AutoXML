from platformdirs import user_data_dir
import xml.etree.ElementTree as ET
import spacy, re, os

from project_ops import listProjects

# To be decided:
# - Enforcing the rules of the DTD by eliminating tags
#                       OR
# - Give the user warnings of the non conforming tags

def infer(datasetID, model_list):
    
    if datasetID not in listProjects(display=False):
        raise FileNotFoundError(f"Project '{datasetID}' does not exist." 
                                " Use command 'create' to start a project")
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    model_dir = os.path.join(dataset_path, "models")
    
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Project '{datasetID}' has no models available." 
                                " Use command 'prepare' to convert data to spacy format"
                                " and command 'train' to train a model first")
    
    nlp_list = []
    for model in model_list:
        model_path = os.path.join(model_dir, model)
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model '{model}' does not exist." 
                                    "Use command 'train' to train a model first")
        else:
            nlp = spacy.load(os.path.join(model_path, "model-best"))
            nlp_list.nlp
    
    