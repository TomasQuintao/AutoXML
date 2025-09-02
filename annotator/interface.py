from flask import Flask, render_template
from platformdirs import user_data_dir
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

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

@app.route("/Projects/<datasetID>")
def project_view(datasetID):
    return render_template("project_view.html", datasetID=datasetID, file_index=0)

if __name__ == "__main__":
    app.run(debug=True)
