import dspy
import xml.etree.ElementTree as ET

from utils.dtd_validator import validate_xml
from utils.data import prepareData, saveData, xml2spans
from utils.config_info import getModel
from agent_dspy import genAgent
from annotator import annotator

# TODO: - Verify validity of xml output against dtd, correct OR warn user
#       - Decide if there is a verification fo the xml aginas dtd now that creatProject does it

def runPipeline(datasetID, modelID='default', example_shots=3):
    
    # Get default model from the config
    if modelID == 'default':
        modelID = getModel()
    
    print("Preparing data...")
    dtd_file, train_xml, raw_xml = prepareData(datasetID)
    
    with open(dtd_file, 'r', encoding='utf-8') as f:
        dtd = f.read()
    
    # (valid, msg) = validate_xml(dtd_file, train_xml)
    # if not valid:
        # raise ValueError(f"XML validation failed: {msg}")
    
    print("Converting data to dspy format...")
    pairs = xml2spans(train_xml, example_shots)

    examples = [
                dspy.Example(raw_text=raw_text, spans=spans).with_inputs("raw_text") 
                for (raw_text, spans) in pairs
               ]
    
    print("Generating the annotation agent...")
    agent, lm = genAgent(dtd, examples, modelID)
    
    print("Performing annotation...")
    xml_tree = annotator(agent, raw_xml, dtd_file)
    lm.inspect_history(1)
    
    final_file = saveData(xml_tree, datasetID)
    
    print(f"\nXML annotated output saved to: {final_file}")
    return final_file
