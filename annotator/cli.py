import argparse
from project_ops import createProject, listProjects, openProject, setModel
from pipeline import runPipeline

def main():
    parser = argparse.ArgumentParser(description="AutoXML CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create project
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("datasetID")
    create_parser.add_argument("dtd_file")
    create_parser.add_argument("xml_file")
    create_parser.add_argument("raw_data_folder")
    create_parser.add_argument("--outdir", default="default")
    create_parser.add_argument("--overwrite", action="store_true")
    
    # List projects
    list_parser = subparsers.add_parser("list", help="List all projects")

    # Annotate project
    annotate_parser = subparsers.add_parser("annotate", help="Annotate raw text in an existing project")
    annotate_parser.add_argument("datasetID")
    annotate_parser.add_argument("--modelID", default="default")  
    annotate_parser.add_argument("--example_shots", type=int, default=3)
    
    # Open project
    open_parser = subparsers.add_parser("open", help="Open a project in browser")
    open_parser.add_argument("datasetID", help="Project dataset ID")
    
    # Define default model
    set_parser = subparsers.add_parser("set", help="Define a default annotation model")
    set_parser.add_argument("modelID", help="Model ID")
    
    args = parser.parse_args()

    if args.command == "create":
        createProject(args.datasetID, args.dtd_file, args.xml_file, args.raw_data_folder,
                      outdir=args.outdir, overwrite=args.overwrite)
    
    elif args.command == "list":
        listProjects()
        
    elif args.command == "annotate":
        runPipeline(args.datasetID, modelID=args.modelID, example_shots=args.example_shots)
        
    elif args.command == "open":
        openProject(args.datasetID)
    
    elif args.command == "set":
        setModel(args.modelID)

if __name__ == "__main__":
    main()
