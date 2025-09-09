from platformdirs import user_data_dir
import xml.etree.ElementTree as ET
import spacy, re, os

from project_ops import listProjects
from dtd_parser.functions import parseDTD
from utils.data import prepareData, saveData, stripTags

# To be decided:
# - Enforcing the rules of the DTD by eliminating tags
#                       OR
# - Give the user warnings of the non conforming tags

def merge(datasetID, model_list):
    
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
    for (i, model) in enumerate(model_list, start=1):
        model = f"layer{i}_{model}_model"
        model_path = os.path.join(model_dir, model)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model '{model}' does not exist." 
                                    " Use command 'train' to train a model first")
        else:
            nlp = spacy.load(os.path.join(model_path, "model-best"))
            nlp_list.append(nlp)

    dtd_file, _, raw_xml = prepareData(datasetID)
    
    with open(dtd_file, 'r', encoding='utf-8') as f:
        dtd = f.read()

    dtd_tree = parseDTD(dtd)
    root_name = dtd_tree['root']['tag']
    doc_name = dtd_tree['root']['children'][0]
    
    raw_tree = ET.parse(raw_xml)
    raw_root = raw_tree.getroot()
    
    # New xml to store the annotations
    root = ET.Element(root_name)
    root.text = "\n"
    
    for doc in raw_root:
        text = "".join(doc.itertext())
        
        element = ET.Element(doc_name)
        element.set('id', doc.get('id'))
        element.set('state', 'raw')

        element = merge_annotations(text, nlp_list, dtd, element)
        
        element_string = ET.tostring(element, encoding='unicode')
        element_string = stripTags(element_string, string_output=True)
        element = ET.fromstring(element_string)
        
        element.tail = "\n\n"
        
        root.append(element)
        
    tree = ET.ElementTree(root)
    
    final_file = saveData(tree, datasetID)
    
    print(f"Changes saved to {final_file}")
    return final_file

def merge_annotations(full_text, nlp_list, dtd, doc_element):
    
    layered_spans = {}
    
    l = 1
    # Generating annotations for each layer
    for nlp in nlp_list:
        
        doc = nlp(full_text)
        
        if ('ner' in nlp.pipe_names):
            spans = doc.ents
            labels = nlp.get_pipe("ner").labels
        else:
            return "Error: Entity Recognizer missing from the pipeline"
            
        # Ensuring compliance with the DTD, number of occurrences and order
        #spans = cut_extra(labels, spans, dtd)
        
        layered_spans[l] = spans
        
        l+=1
    
    # Ensure proper nesting
    #layered_spans = ensure_nesting(layered_spans, dtd, l-1)
    
    doc_element = layers2xml(full_text, layered_spans, l-1, doc_element)

    return doc_element

def layers2xml(text, layered_spans, layer, root):
    
    i = layer - 1
    
    # Creating the elements of the last layer
    previous_elements = []
    
    for span in layered_spans[layer]:
        elem = ET.Element(span.label_)
        elem.text = text[span.start_char:span.end_char]
        previous_elements.append((elem, span.start_char, span.end_char))
    
    while (i>0):
        
        # Appending the previous elements to each element, and then updating the previous elements list
        for span in layered_spans[i]:
            label, start, end = span.label_, span.start_char, span.end_char
            
            current_element = ET.Element(label)
            
            # Separating the elements nested in this layer, from the ones nested above (due to non captured tags)
            nested_elems = []
            new_elems = []
            for p_elem in previous_elements:
                if (p_elem[1] >= start and p_elem[2] <= end):
                    nested_elems.append(p_elem)
                elif (p_elem[2] <= start or p_elem[1] >= end): # Does not add overlapping spans
                    new_elems.append(p_elem)
            previous_elements = new_elems     
            
            # In case there are no child elements of the current span
            if (len(nested_elems) == 0):
                current_element.text = text[start:end]
            else:
                first_child = nested_elems[0]
                current_element.text = text[start:first_child[1]]
                
                # Appending the nested elements to the current element
                for j in range(len(nested_elems)):
                    subElem, subStart, subEnd = nested_elems[j]
                    
                    # The last subElement of the current element
                    if (j == len(nested_elems)-1):
                        subElem.tail = text[subEnd:end]
                    # The other elements
                    else:
                        next_subElem, next_start, next_end = nested_elems[j+1]
                        if (subEnd < next_start):
                            subElem.tail = text[subEnd: next_start]
                    
                    current_element.append(subElem)
            
            previous_elements.append((current_element, start, end))
        
        previous_elements = sorted(previous_elements, key=lambda x: x[1])
        i-=1
    
    # Appending the top elements to the root
    if (len(previous_elements) == 0):
        root.text = text
    else:        
        first_child = previous_elements[0]
        root.text = text[:first_child[1]]
            
        # Appending the nested elements to the root
        for j in range(len(previous_elements)):
            elem, start, end = previous_elements[j]
                
            # The last element of the root
            if (j == len(previous_elements)-1):
                elem.tail = text[end:]
            # The other elements
            else:
                next_elem, next_start, next_end = previous_elements[j+1]
                if (end < next_start):
                    elem.tail = text[end: next_start]
                
            root.append(elem) 
    
    return root

# Assuming the parent layers are more probable to be correct, might be dubious <:|
def ensure_nesting(layered_spans, dtd, last_layer):
    
    i = last_layer
    
    parents = {}
    while (i>1):
        spans = layered_spans[i]
        
        filtered_spans = []
        for span in spans:
            label = span.label_
            
            # Checking if the span is correctly nested
            parent_label = parentOf(label, dtd)
            if is_nested(span, layered_spans, i, dtd, parent_label):    
                filtered_spans.append(span)

                
        layered_spans[i] = filtered_spans    
        
        i-=1
    return layered_spans

def is_nested(span, layered_spans, layer, dtd, parent_label):
    
    # Last layer was reached
    if (layer == 1): 
        return True
    
    # Checking if it is nested in the right one
    for p_span in layered_spans[layer-1]:
        if (span.start_char >= p_span.start_char and span.end_char <= p_span.end_char):
            if (p_span.label_ == parent_label):
                return True
            else:
                return False
    
    return is_nested(span, layered_spans, layer-1, dtd, parentOf(parent_label, dtd))

def parentOf(label, dtd):
    tag_name = r"[A-Za-z_][A-Za-z0-9._-]*"
    match = re.search(rf"<!ELEMENT\s+({tag_name})\s+.*?[\( ,\|]{label}[, \|\)\(\*\?\+]", dtd)
    return match.group(1)
        
def cut_extra(labels, spans, dtd):
    
    tag_name = r"[A-Za-z_][A-Za-z0-9._-]*"
    
    # Finding the relevant line of the DTD for the present layer
    mline = ""
    for line in dtd.splitlines():
        if all([re.match(rf"<!ELEMENT {tag_name} .*?[\( ,\|]{label}[, \|\)\(\*\?\+]", line) for label in labels]):
            mline = line
    
    # Check for modifiers on the label // ATTENTION! Does not work for nested declarations
    multi_label = {}
    for label in labels:
        if re.search(rf"{label}[\+\*] | {label}[^\)]*\)[\+\*]", mline):
            multi_label[label] = 2
        else:
            multi_label[label] = 1
    
    # Keeping only the first occurrence of a tag, when only one is allowed
    filtered_spans = []
    for span in spans:
        if (multi_label[span.label_] == 1):
            multi_label[span.label_] = 0
            filtered_spans.append(span)
        elif (multi_label[span.label_] == 2):
            filtered_spans.append(span)

    spans = filtered_spans
    
    # Checking if the order of the tags is correct, if defined in the DTD
    if re.search(rf"{tag_name},\s*{tag_name}", mline):
        label_order = re.findall(tag_name, mline)[2:]
        order_spans(spans, label_order)
    
    return spans
        
def order_spans(spans, order):
    # Não sei se vale a pena fazer isto
    pass
    