// TODO: The page freezes when the buttons are spammed
let container = document.getElementById("text-display");
let datasetID = container.dataset.dataset;
let fileIndex = parseInt(container.dataset.fileIndex);

const fileNameEl = document.getElementById("file-name");
const fileNumberInput = document.getElementById("file-number-input");
const totalFilesEl = document.getElementById("total-files");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const saveBtn = document.getElementById("save-btn")
const codeEl = document.getElementById("xml-code");

let totalFiles = 0;
let isLoading = false;

// Save button only enabled when the content changes
saveBtn.disabled = true
let originalText = codeEl.textContent;

codeEl.addEventListener("input", () => {
	saveBtn.disabled = codeEl.textContent === originalText
});

async function loadDoc(index) {
	if (isLoading) return;

	isLoading = true;
	prevBtn.disabled = true;
	nextBtn.disabled = true;
	fileNumberInput.disabled = true;

	try {
		const res = await fetch(`/Projects/${datasetID}/file/${index}`);
		if (!res.ok) throw new Error("Failed to fetch file");

		const data = await res.json();

		codeEl.textContent = data.text;

		if ('requestIdleCallback' in window) {
			requestIdleCallback(() => hljs.highlightElement(codeEl));
		} else {
			setTimeout(() => hljs.highlightElement(codeEl), 0);
		}

		fileIndex = data.index;
		totalFiles = data.total;

		// Update the input box and total
		fileNumberInput.value = fileIndex + 1; // 1-based
		totalFilesEl.textContent = totalFiles;
		
		originalText = data.text;
		saveBtn.disabled = true

	} catch (err) {
		console.error(err);
		alert("Error loading file");
	} finally {
		prevBtn.disabled = false;
		nextBtn.disabled = false;
		fileNumberInput.disabled = false;
		isLoading = false;
	}
}

// Saving the edited content
saveBtn.onclick = async () => {
    const editedText = codeEl.textContent;

    try {
        const res = await fetch(`/Projects/${datasetID}/save/${fileIndex}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: editedText }),
        });

        if (!res.ok) throw new Error("Failed to save");

        const data = await res.json();
        console.log("Saved:", data);

        // Reset baseline text
        originalText = editedText;
        saveBtn.disabled = true;
    } catch (err) {
        console.error(err);
        alert("Error saving changes");
    }
};

// Navigation buttons
prevBtn.onclick = () => loadDoc(fileIndex - 1);
nextBtn.onclick = () => loadDoc(fileIndex + 1);

// Jump to file when pressing Enter in the input
fileNumberInput.addEventListener("keydown", (e) => {
	if (e.key === "Enter") {
		let val = parseInt(fileNumberInput.value);
		if (!isNaN(val)) {
			val = Math.max(1, Math.min(val, totalFiles)); // clamp
			loadDoc(val - 1); // convert to 0-based
		}
	}
});

loadDoc(fileIndex);