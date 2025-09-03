from flask import Flask, render_template, request, jsonify
from platformdirs import user_data_dir
import xml.etree.ElementTree as ET
import os

from utils.dtd_validator import validate_xml
from dtd_parser.functions import parseDTD

app = Flask(__name__)

@app.route("/Projects/<datasetID>")
def project_view(datasetID):
    return render_template("project_view.html", datasetID=datasetID, file_index=0)

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
    
    edited_xml = f"<{root_tag}>{data['text']}</{root_tag}>"
    
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
    
    if valid:
        message = f"File {index} updated.\n"
    else:
        message = f"Failed save.\n{log}"
    
    return jsonify({"success": valid, "message": message}), 200

if __name__ == "__main__":
    app.run(debug=True)
