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

### Requirements
Developed on Windows, not sure if it works with other OS
-  [Python](https://www.python.org/downloads/)
-  [pip](https://pypi.org/project/pip/)
- [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

## Tutorial



## Commands
Small documentation of CLI

### *create*
Create an annotation project
`autoxml create [projectID] [dtd_path] [xml_path] [folder_path] [--overwrite]`
- `projectID`


### *list*
Listing existing projects
`autoxml list`

### *open*
Opening the annotation interface
`autoxml open [projectID]`

### *set*
Defining a default LLM for DSPy
`autoxml set [modelID]`

### *annotate*
Annotating with DSPy version
`autoxml annotate [projectID] [--modelID] [--example-shots] `

### *prepare*
Preparing training data for spaCy
`autoxml prepare [projectID]`

### *train*
Training a spaCy NER model for a layer
`autoxml train [projectID] [layer] [model]`

### *merge*

`autoxml merge [projectID] [--models] `
