import xml.etree.ElementTree as ET
import re, sys, os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def getData(datasetID: str):
    
    dataset_path = os.path.join(PROJECT_ROOT, "data", datasetID)

    dtd_file = os.path.join(dataset_path, f"{datasetID}.dtd")
    xml_file = os.path.join(dataset_path, f"{datasetID}.xml")
    raw_data_folder = os.path.join(dataset_path, f"raw_{datasetID}")
    
    return dtd_file, xml_file, raw_data_folder

def saveData(xml_tree, datasetID):
    
    dataset_path = os.path.join(PROJECT_ROOT, "data", datasetID)
    
    output_file = os.path.join(dataset_path, f"output_{datasetID}.xml")
    
    xml_tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    return output_file

def xml2spans(xml_file, count=0):
    global position
    
    xml_string = stripTags(xml_file, string_output=True)
    root = ET.fromstring(xml_string)
    
    pairs = []
    
    if count==0:
        count = len(root)
    
    i=0
    for document in root:
        if  (i == count):
            break
        
        full_text = "".join(document.itertext())
        spans = []
        position = 0
        get_position(document, spans)
        
        # Removing the root tag, not useful for the annotation
        spans = spans[1:]
        
        pairs.append((full_text, spans))
        i+=1
    return pairs

def get_position(element, tag_list):
    global position
    
    text = "".join(element.itertext())

    if (len(text) > 0):
        span = {'text': text, 'label': element.tag, 'start': position, 'end': position + len(text)}
        tag_list.append(span)
    
    position += len(element.text or "")
    
    for child in element:
        get_position(child, tag_list)
    
    position += len(element.tail or "")
   
    return tag_list

def stripTags(xml_file, string_output=False):
    
    with open(xml_file, 'r', encoding='utf-8') as file:
        xml = file.read() 
    
    text = xml[39:]
    declaration = xml[:39]
    
    # Jumping leading and trailing whitespaces
    open_tag = r"(<[^\/][^>]*>)"
    close_tag = r"(<\/[^>]+>)"
    text = re.sub(open_tag + r"(\s+)(?=[^<])", r"\2" + r"\1", text)
    text = re.sub(r"(?<=[^>])(\s+)" + close_tag, r"\2" + r"\1", text)
    text = re.sub(open_tag + r"(\s+)" + open_tag, r"\2" + r"\1" + r"\3", text)
    text = re.sub(close_tag + r"(\s+)" + close_tag, r"\1" + r"\3" + r"\2", text)

    if string_output:
        output = declaration + text
    else:
        output = f"{xml_file[:-4]}_cl.xml"
        with open(output, 'w', encoding='utf-8') as f:
            f.write(declaration + text)
        
    return output
