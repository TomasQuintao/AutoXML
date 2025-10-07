import dspy
import xml.etree.ElementTree as ET

from annotator.utils.dtd_validator import validate_xml
from annotator.utils.data import prepareData, saveData, xml2spans
from annotator.utils.config_info import getModel
from annotator.utils.logs import create_log_file
from annotator.agent_dspy import genAgent
from annotator.annotator import annotator

# TODO: - Verify validity of xml output against dtd, correct OR warn user
#       - Decide if there is a verification fo the xml aginas dtd now that creatProject does it

def runPipeline(datasetID, api_key='default', modelID='default', example_shots=3, max_tokens=4000):
    
    
    # Get default model from the config
    if modelID == 'default':
        modelID = getModel()
    
    if api_key == 'default':
        api_key = "TOGETHER_AI_API_KEY"
    
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
    agent, lm = genAgent(dtd, examples, modelID, api_key, max_tokens=max_tokens)
    
    print("Performing annotation...")
    
    log_path = create_log_file(datasetID)
    xml_tree = annotator(agent, raw_xml, dtd_file, lm, datasetID)
    print("\nLLM history logged to: ", log_path)
    #lm.inspect_history(1)
    
    final_file = saveData(xml_tree, datasetID)
    
    print(f"\nXML annotated output saved to: {final_file}")
    return final_file
