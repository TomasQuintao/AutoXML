import dspy
import xml.etree.ElementTree as ET

from utils.dtd_validator import validate_xml
from utils.data import getData, saveData, xml2spans
from agent_dspy import genAgent
from annotator import annotator

# TODO: Verify validity of xml output against dtd, correct OR warn user

def main(datasetID, example_shots, modelID):
    
    dtd_file, xml_file, raw_data_folder = getData(datasetID)
 
    with open(dtd_file, 'r', encoding='utf-8') as f:
        dtd = f.read()
    
    (valid, msg) = validate_xml(dtd_file, xml_file)
    if (valid == False):
        return f"Error: {msg}"

    pairs = xml2spans(xml_file, example_shots)

    examples = [
                dspy.Example(raw_text=raw_text, spans=spans).with_inputs("raw_text") 
                for (raw_text, spans) in pairs
               ]

    agent, lm = genAgent(dtd, examples, modelID)
    #lm.inspect_history(1)
    
    xml_tree = annotator(agent, raw_data_folder, dtd_file)
    
    final_file = saveData(xml_tree, datasetID)
    
    return final_file

main("postcards", 3, 'together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo')