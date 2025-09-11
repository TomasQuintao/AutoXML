import xml.etree.ElementTree as ET
import re, sys, os
from platformdirs import user_data_dir

def prepareData(datasetID: str):
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    
    dtd_file = os.path.join(dataset_path, f"{datasetID}.dtd")
    xml_file = os.path.join(dataset_path, f"{datasetID}.xml")
    #raw_data_folder = os.path.join(dataset_path, f"raw_{datasetID}")
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    train_root = ET.Element(root.tag)
    raw_root = ET.Element(root.tag)
    
    # Separating train data from raw data
    for doc in root:
        
        if (doc.attrib['state'] == 'ready'):
            train_root.append(doc)
            
        elif (doc.attrib['state'] == 'raw'):
            doc.tail = "\n\n"
            raw_root.append(doc)
    
    train_tree = ET.ElementTree(train_root)
    raw_tree = ET.ElementTree(raw_root)
    
    train_xml = os.path.join(dataset_path, f"train.xml")
    raw_xml = os.path.join(dataset_path, f"raw.xml")
    
    train_tree.write(train_xml, encoding="utf-8", xml_declaration=True)
    raw_tree.write(raw_xml, encoding="utf-8", xml_declaration=True)
    
    return dtd_file, train_xml, raw_xml

def saveData(xml_tree, datasetID):
    
    projects_path = user_data_dir('Projects', 'AutoXML')
    dataset_path = os.path.join(projects_path, datasetID)
    output_file = os.path.join(dataset_path, f"{datasetID}.xml")
    
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    for doc in xml_tree.getroot():
        index = int(doc.get('id'))
        root[index] = doc
    
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    return output_file

def xml2spans(xml_file, count):
    global position
    
    xml_string = stripTags(xml_file, string_output=True)
    root = ET.fromstring(xml_string)
    
    pairs = []
    
    if count==-1:
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

def stripTags(xml, string_output=False):
    
    if (xml[-4:] == ".xml"):
        with open(xml, 'r', encoding='utf-8') as file:
            xml = file.read() 
    
    declaration = ""
    for line in xml.splitlines():
        if (line[:2] == "<!" or line[:2] == "<?"):
            declaration += line + '\n'
    
    start = len(declaration)
    text = xml[start:]
    
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
