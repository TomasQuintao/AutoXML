import spacy, os, pathlib
from spacy.cli.train import train
from platformdirs import user_data_dir

from project_ops import listProjects

def trainModel(datasetID, layer, model):
    
    if datasetID not in listProjects(display=False):
        raise FileNotFoundError(f"Project '{datasetID}' does not exist." 
                                " Use command 'create' to start a project")
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    layers_dir = os.path.join(dataset_path, "layers")
    model_dir = os.path.join(dataset_path, "models")
    
    if not os.path.exists(layers_dir):
        raise FileNotFoundError(f"Project '{datasetID}' has no training data prepared." 
                                " Use command 'prepare' to convert data to spacy format")
    
    n_layers = len(os.listdir(layers_dir)) // 2
    if (layer<1 or layer>n_layers):
        raise ValueError(f"This dataset only has {n_layers} layers.")
    
    if model=="ner" or model=="trf":
        package_dir = pathlib.Path(__file__).resolve().parent.parent
        model_configs_dir = os.path.join(package_dir, "model_configs")
        config_path = os.path.join(model_configs_dir, f"spacy_{model}.cfg")
    else:
        raise ValueError(f"Model {model} is not supported. Choose either 'ner' or 'trf'")
    
    os.makedirs(model_dir, exist_ok=True)
    output_path = os.path.join(model_dir, f"layer{layer}_{model}_model")
    train_path = os.path.join(layers_dir, f"layer{layer}_train.spacy")
    dev_path = os.path.join(layers_dir, f"layer{layer}_dev.spacy")
    
    train(
        config_path=config_path,
        output_path=output_path, 
        overrides={"paths.train": train_path,
                   "paths.dev": dev_path}
    )
    
    return output_path
