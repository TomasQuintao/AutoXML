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

### Configuration

In order to use the LLM version of the annotator, it is required to have access to an LLM API,
for example [together.ai](https://www.together.ai/) (**only works with together.ai, for now**).
An API key must be generated and defined as an environment variable named `TOGETHER_AI_API_KEY`.

`setx TOGETHER_AI_API_KEY "your-key-here"` (on windows)


### System Requirements
Developed on Windows (compatibility with other OS not yet tested).
-  [Python](https://www.python.org/downloads/)
-  [pip](https://pypi.org/project/pip/)
- [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
- ~2 GB of free disk space

## Tutorial

After installing, to start an annotation project use the `autoxml create` command.
Make sure the data is in the correct format (examples on the *AutoXML\data folder*).  

`autoxml create ex_project data\postcards\postcards.dtd data\postcards\postcards.xml data\postcards\raw_postcards`

Having now a project to work with, to visualize and manage annotations, use the command:  

`autoxml open ex_project`

This command opens a browser page (hosted on a local server) which allows viewing all project
documents and their annotations. It also works as a manual annotation interface, 
where annotations can be added by selecting text or removed by deleting the xml tags.
The documents with the state attribute set to "ready" are ready to be used as training examples,
the ones set to "raw" either have no annotations or are incomplete.
The "raw" documents can be annotated and saved, which will add them to the training examples.


The automatic annotation can be done in two ways, which have slightly different workflows.
The LLM version is simpler and faster to use, as it doesn't require training the model, which means
only a few annotated examples will suffice.
However, it is much more expensive, and does not necessarily guarantee better results.

### LLM Annotation
**WARNING: This version uses an LLM API, which requires buying credits with real money.**
**The price increases with the number of examples provided to the model and the number of raw documents annotated by the model, as each token processed by the LLM has a fixed cost.**

To use an LLM for annotation, make sure the Configuration section steps were followed first.
In order to save time, a default LLM model can be defined. Not all models will work, as some cannot comply with the required output format.  

`autoxml set "together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo"`

After defining a default model, to annotate the raw documents of the project execute:  

`autoxml annotate ex_project --example-shots 3`

The number of annotated examples provided to the model can be increased for better performance.
However, for now, using more than around 7 examples won't bring measurable improvements.

After the annotation, the newly annotated documents can be inspected and corrected using the `autoxml open` command.

### Nested NER

Using spaCy ner models for annotating the several layers of xml requires more setup, and considerably more training data
(minimum of 100 examples used in testing).

The first step is preparing spacy training data from the xml annotated documents.

`autoxml prepare ex_project`

This will generate separate training data for each model, which is responsible for annotating a single layer of the data.
Now comes the more time consuming step, the training of the models. 
The DTD defines how many layers the data has and, consequently, the number of models to train.
Supposing the `ex_project` has 3 layers, the following commands must be executed:

```
autoxml train ex_project 1 ner
autoxml train ex_project 2 ner
autoxml train ex_project 3 ner
```

The keyword `ner` indicates that a spaCy ner model will be trained. 
Later, if the performance of the simple ner model isn't sufficient, there is also the `trf` option,
which improves the results, but has a **considerably longer training time**, as it uses transformers.

The actual annotation is executed by choosing the model for each layer, starting by layer 1,
this time with a new command:  

`autoxml merge ex_project --models ner ner ner`


## Commands
Small documentation of the CLI

### *create*
Create an annotation project.  
`autoxml create [projectID] [dtd_path] [xml_path] [folder_path] [--overwrite]`
| Argument | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|
| `dtd_path` | Path <small>(Positional)</small> | Location of the DTD file|
| `xml_path` | Path <small>(Positional)</small> | Location of the XML training data |
| `folder_path` | Path <small>(Positional)</small> | Location of the folder containing the text documents |
| `--overwrite` | bool <small>(Flag)</small> | Overwrite an existing project|

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
| `layer` | int <small>(Positional)</small> | Number corresponding to the layer of the training data|
| `model` | (ner\|trf) <small>(Positional)</small> | Pipeline to be trained. ner - spaCy ner; trf - transformer + spaCy ner  |

### *merge*
Use trained ner models to annotate new data  
`autoxml merge [projectID] [--models] `
| Argument | Type | Description | 
|--|--|--|
| `projectID` | str <small>(Positional)</small> | Name for the project|
| `--models` | List[(ner\|trf)] <small>(Positional)</small> | List of spaCy models to use for each layer |
