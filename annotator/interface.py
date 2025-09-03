from flask import Flask, render_template, request, jsonify
from platformdirs import user_data_dir
import xml.etree.ElementTree as ET
import os

from utils.dtd_validator import validate_xml
from dtd_parser.functions import parseDTD, get_labels

app = Flask(__name__)

@app.route("/Projects/<datasetID>")
def project_view(datasetID):
    
    projects_dir = user_data_dir('Projects', 'AutoXML')
    dataset_dir = os.path.join(projects_dir, datasetID)
    dtd_path = os.path.join(dataset_dir, f"{datasetID}.dtd")
    
    dtd_tree = parseDTD(dtd_path)
    
    return render_template(
        "project_view.html", 
        datasetID=datasetID, 
        file_index=0,
        labels=get_labels(dtd_tree)
        )

@app.route("/Projects/<datasetID>/file/<int:index>")
def getDoc(datasetID, index):
    
    projects_dir = user_data_dir('Projects', 'AutoXML')
    dataset_dir = os.path.join(projects_dir, datasetID)
    xml_path = os.path.join(dataset_dir, f"{datasetID}.xml")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Allow loop around
    index = index % len(root)
    doc = root[index]
    
    content = ET.tostring(doc, encoding='unicode')

    return {"text": content, "index": index, "total": len(root)}

@app.route("/Projects/<datasetID>/save/<int:index>", methods=["POST"])
def saveDoc(datasetID, index):
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"success": False, "message": "No text provided"}), 400
    
    projects_dir = user_data_dir('Projects', 'AutoXML')
    dataset_dir = os.path.join(projects_dir, datasetID)
    xml_path = os.path.join(dataset_dir, f"{datasetID}.xml")
    dtd_path = os.path.join(dataset_dir, f"{datasetID}.dtd")
    xml_check = os.path.join(dataset_dir, f"check.xml")
    
    dtd_tree = parseDTD(dtd_path)
    root_tag = dtd_tree['root']['tag']
    
    new_doc_string = data['text']
    edited_xml = f"<{root_tag}>{new_doc_string}</{root_tag}>"
    
    with open(xml_check, 'w', encoding='utf-8') as f:
        f.write(edited_xml)
    
    # Validate the edited XML the user wants to save
    try:
        (valid, msg) = validate_xml(dtd_path, xml_check)
        if valid:
            log = "Valid XML."
        else:
            log = "Invalid XML:\n" + "\n".join(str(e) for e in msg)
            
    except Exception as e:
        valid = False
        log = f"Failed XML validation: {e}"
    
    if not valid:
        return jsonify({"success": False, "message": f"Failed save.\n{log}"}), 200
    
    new_doc = ET.fromstring(new_doc_string)
    new_text = "".join(new_doc.itertext())
    index = int(new_doc.get('id'))
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    doc = root[index]
    text = "".join(doc.itertext())
    
    # Guaranteeing the text remains unchanged
    if new_text != text:
        return jsonify({"success": False, "message": f"Failed save. Original text was altered."}), 200
        
    new_doc.set('state', 'ready')
    root[index] = new_doc
    
    new_tree = ET.ElementTree(root)
    new_tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    
    return jsonify({"success": True, "message": f"File {index} updated."}), 200

if __name__ == "__main__":
    app.run(debug=True)
