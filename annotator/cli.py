import argparse

def main():
    parser = argparse.ArgumentParser(description="AutoXML CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create project
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("datasetID")
    create_parser.add_argument("dtd_file")
    create_parser.add_argument("xml_file")
    create_parser.add_argument("raw_data_folder")
    create_parser.add_argument("--overwrite", action="store_true")
    
    # List projects
    list_parser = subparsers.add_parser("list", help="List all projects")
    list_parser.add_argument("--no_display", action="store_false", dest="display")
    
    # Open project
    open_parser = subparsers.add_parser("open", help="Open a project in browser")
    open_parser.add_argument("datasetID", help="Project dataset ID")

    # Annotate project with dspy
    annotate_parser = subparsers.add_parser("annotate", help="Annotate raw text in an existing project")
    annotate_parser.add_argument("datasetID")
    annotate_parser.add_argument("--modelID", default="default")  
    annotate_parser.add_argument("--example-shots", type=int, default=3)
    
    # Define default model for dspy
    set_parser = subparsers.add_parser("set", help="Define a default annotation model")
    set_parser.add_argument("modelID", help="Model ID")
    
    # Prepare training data for nested NER
    prep_parser = subparsers.add_parser("prepare", help="Prepare spacy training data for nested ner")
    prep_parser.add_argument("datasetID", help="Project dataset ID")
    
    # Train a NER model for a specific layer
    train_parser = subparsers.add_parser("train", help="Train a spacy ner model for a data layer")
    train_parser.add_argument("datasetID", help="Project dataset ID")
    train_parser.add_argument("layer", type=int)
    train_parser.add_argument("model")
    
    # Use the spacy models for inference and merge their annotations
    merge_parser = subparsers.add_parser("merge", help="Annotate with sapcy models and merge layers")
    merge_parser.add_argument("datasetID", help="Project dataset ID")
    merge_parser.add_argument("--models", action="extend", nargs="+", type=str, dest="model_list")

    
    args = parser.parse_args()

    if args.command == "create":
        from annotator.project_ops import createProject
        createProject(args.datasetID, args.dtd_file, args.xml_file, args.raw_data_folder,
                      overwrite=args.overwrite)
    
    elif args.command == "list":
        from annotator.project_ops import listProjects
        listProjects(display=args.display)
        
    elif args.command == "annotate":
        from annotator.pipeline import runPipeline
        runPipeline(args.datasetID, modelID=args.modelID, example_shots=args.example_shots)
        
    elif args.command == "open":
        from annotator.project_ops import openProject
        openProject(args.datasetID)
    
    elif args.command == "set":
        from project_ops import setModel
        setModel(args.modelID)
    
    elif args.command == "prepare":
        from annotator.layer_splitter import prepareTrainData
        prepareTrainData(args.datasetID)
    
    elif args.command == "train":
        from annotator.train_layer import trainModel
        trainModel(args.datasetID, args.layer, args.model)
    
    elif args.command == "merge":
        from annotator.merger import merge
        merge(args.datasetID, args.model_list)

if __name__ == "__main__":
    main()
