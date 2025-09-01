let datasetID = document.body.dataset.datasetId;
let fileIndex = parseInt(document.body.dataset.fileIndex);

const textDisplay = document.getElementById("text-display");
const fileNameEl = document.getElementById("file-name");

async function loadFile(index) {
    const res = await fetch(`/Projects/${datasetID}/file/${index}`);
    const data = await res.json();
    textDisplay.textContent = data.text;
    fileNameEl.textContent = `File ${data.index + 1} of ${data.total}: ${data.file_name}`;
    fileIndex = data.index;
}

document.getElementById("prev-btn").onclick = () => loadFile(fileIndex - 1);
document.getElementById("next-btn").onclick = () => loadFile(fileIndex + 1);

loadFile(fileIndex);