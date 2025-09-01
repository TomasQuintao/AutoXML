import argparse
from project_ops import createProject, listProjects
#from annotate import annotateProject

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
    # annotate_parser = subparsers.add_parser("annotate", help="Annotate an existing project")
    # annotate_parser.add_argument("project_dir")
    # annotate_parser.add_argument("--type", default="default")

    args = parser.parse_args()

    if args.command == "create":
        createProject(args.datasetID, args.dtd_file, args.xml_file, args.raw_data_folder,
                      outdir=args.outdir, overwrite=args.overwrite)
    elif args.command == "list":
        listProjects()
    # elif args.command == "annotate":
        # annotateProject(args.project_dir, annotation_type=args.type)

if __name__ == "__main__":
    main()
