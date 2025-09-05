import xml.etree.ElementTree as ET
from spacy.tokens import DocBin
from platformdirs import user_data_dir
import re, sys, spacy, os

from dtd_parser.functions import parseDTD, assignLayer
from utils.data import prepareData, stripTags

def prepareTrainData(datasetID):
    
    dtd_file, train_xml, _ = prepareData(datasetID)
    
    with open(dtd_file, 'r', encoding='utf-8') as f:
        dtd = f.read()
    
    xml_string = stripTags(train_xml, string_output=True)
    root = ET.fromstring(xml_string)
    
    dtd_tree = parseDTD(dtd)
    layers = assignLayer(dtd_tree)
    depth = max(layers.values())
    
    TRAIN_DATA = []
    for document in root:
        TRAIN_DATA.append(extract_tags(document))
        
    DATA_LAYERS = {}
    for i in range(1,depth+1):
        DATA_LAYERS[i] = [] 
  
    # Dividing the different layers into different trainsets
    for text, annotations in TRAIN_DATA:
        for i in range(1,depth+1):
            ents = []
            for (st, end, label) in annotations["entities"]:
                if(layers[label]==i):
                    ents.append((st,end,label))
            DATA_LAYERS[i].append((text, {'entities': ents}))
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    layers_path = os.path.join(dataset_path, "layers")
    
    os.makedirs(layers_path, exist_ok=True)
    
    warning_log = ""
    
    nlp = spacy.blank("en")
    for i in range(1,depth+1):    
        TRAIN_DATA = DATA_LAYERS[i]
        
        n = int(0.85 * len(TRAIN_DATA))
        DEV_DATA = TRAIN_DATA[n:]
        TRAIN_DATA = TRAIN_DATA[:n]
        
        doc_id = 0        
        warning_log += saveDocBin(
            TRAIN_DATA,
            nlp, 
            os.path.join(layers_path, f"layer{i}_train.spacy")
            )
        warning_log += saveDocBin(
            DEV_DATA, 
            nlp, 
            os.path.join(layers_path, f"layer{i}_dev.spacy"),
            n
            )
    
    log_path = os.path.join(layers_path, "logs.txt")
    if (len(warning_log)>0):
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(warning_log)
        print("Invalid annotations were skipped. Logs at:\n",log_path)
    elif (os.path.exists(log_path)):
        os.remove(log_path)
    
    out_files = [(os.path.join(layers_path, f"layer{i}_train.spacy"),
                 os.path.join(layers_path, f"layer{i}_dev.spacy")) 
                 for i in range(1,depth+1)]
    
    return out_files 
    
def extract_tags(document):
    
    clean_xml(document)
    
    tag_list = []
    
    get_position(document, tag_list, 0)
    
    tag_list = tag_list[1:]

    full_text = ("".join(document.itertext()))

    text_anno = (full_text, {"entities": tag_list})
    
    return text_anno
    
def get_position(element, tag_list, position):
    
    text = "".join(element.itertext())

    if (len(text) > 0):
        if (text[0] == ' ' or text[0] == '\n'):
            span = (position + 1, position + len(text), element.tag)
        else:
            span = (position, position + len(text), element.tag)
        tag_list.append(span)
    
    position += len(element.text or "")
    
    for child in element:
        position = get_position(child, tag_list, position)
    
    position += len(element.tail or "")
   
    return position
    
# Deleting contiguous whitespace
def clean_xml(element):
    
    element.text = re.sub(r"\s+", " ", element.text or "")
    element.text = re.sub(r"•", "", element.text or "")
    
    element.tail = re.sub(r"•", "", element.tail or "")
    element.tail = re.sub(r"\s+", " ", element.tail or "")
    
    for child in element:
        clean_xml(child)  

def saveDocBin(train_data, nlp, out_file, doc_id=0):
    log = ""
    db = DocBin()
    
    for text, annotations in train_data:
        doc = nlp.make_doc(text)
        ents = []
        
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            if span is None:
                warning = (f"WARNING: Invalid span at ({start},{end}), labeled {label} in document {doc_id}.\nCaptured text:\n{text[start:end]}\n")
                #print(warning)
                log += warning
            else:
                ents.append(span)
        doc_id += 1
        doc.ents = ents
        db.add(doc)
        
    db.to_disk(out_file)
    
    return log

prepareTrainData("resumes")