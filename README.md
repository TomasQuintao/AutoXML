# AutoXML

*autoxml* is a CLI-only Python package for managing XML annotation projects, with two different approaches to (semi-)automatic annotation.
The first approach uses more traditional NLP pipelines, based on spaCy's NER models, while the second one relies on LLMs, using the DSPy framework.
This results in different annotation workflows, explained later.

## Installation

Before installing the project, check if you have the requirements on your machine.
To download this project from the repository, execute: 
`git clone https://github.com/TomasQuintao/AutoXML.git`

 I recommend creating a [virtual environment](https://docs.python.org/3/library/venv.html) to avoid any conflicts, located inside the downloaded project folder.
```
cd AutoXML
python -m venv my_venv
```
If you created a virtual environment, activate it first, and then proceed with the actual installation of  the package.
```
my_venv\Scripts\activate.bat
pip install .
```

# Configuration

In order to use the LLM version of the annotator, it is required to have access to an LLM API,
for example [together.ai](https://www.together.ai/) (**only works with together.ai, for now**).
An API key must be generated and defined as an environment variable named `TOGETHER_AI_API_KEY`.

`setx TOGETHER_AI_API_KEY "your-key-here"` (on windows)


### System Requirements
Developed on Windows (compatibility with other OS not yet tested).
-  [Python](https://www.python.org/downloads/)
-  [pip](https://pypi.org/project/pip/)
- [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

## Tutorial

After installing, to start an annotation project use the `autoxml create` command.
Make sure the data is in the correct format (examples on the *AutoXMl\data folder*).  

`autoxml create ex_project data\postcards\postcards.dtd data\postcards\postcards.xml data\postcards\raw_postcards`

Having now a project to work with, to visualize and manage annotations, use the command:  

`autoxml open ex_project`

This command opens a browser page (hosted on a local server) which allows viewing all project
documents and their annotations. It is also a manual annotation interface, where tags can added, by selecting text, or removed.



## Commands
Small documentation of CLI

### *create*
Create an annotation project.  
`autoxml create [projectID] [dtd_path] [xml_path] [folder_path] [--overwrite]`
| Argument | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|
| `dtd_path` | Path <small>(Positional)</small> | Location of the DTD file|
| `xml_path` | Path <small>(Positional)</small> | Location of the XML training data |
| `folder_path` | Path <small>(Positional)</small> | Location of the folder containing the text documents |
| `--overwrite` | bool <small>(Flag)</small> | Overwite an existing project|

### *list*
List existing projects.  
`autoxml list`

### *open*
Open the annotation interface for the specified project.  
`autoxml open [projectID]`
| Argument | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|

### *set*
Define a default LLM model to use for annotation  
`autoxml set [modelID]`
| Argument | Type | Description | 
|--|--|--|
| `modelID` | str <small>(Positional)</small> | ID of a model provided by an LLM API|

### *annotate*
Annotate raw documents of a project using DSPy version  
`autoxml annotate [projectID] [--modelID] [--example-shots] `
| Arguments | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|
| `--modelID` | Optional[str] <small>(Option)</small> | ID of a model provided by an LLM API|
| `--example-shots` | Optional[int] <small>(Option)</small> | Number of examples to provide to the LLM. Defaults to 3 |


### *prepare*
Prepare layers of training data in spaCy format  
`autoxml prepare [projectID]`
| Arguments | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|

### *train*
Train a spaCy NER model for a single layer of the XML/DTD  
`autoxml train [projectID] [layer] [model]`
| Argument | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|
| `layer` | int <small>(Positional)</small> | Layer of the training data|
| `model` | (ner\|trf) <small>(Positional)</small> | Pipeline to be trained. ner - spaCy ner; trf - transformer + spaCy ner  |

### *merge*
Use trained ner models to annotate new data  
`autoxml merge [projectID] [--models] `
| Argument | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|
| `--models` | List[(ner\|trf)] <small>(Positional)</small> | List of spaCy models to use for each layer |
