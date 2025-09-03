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
const dropdown = document.getElementById("label-dropdown")
const logs = document.getElementById("logs")

let totalFiles = 0;
let isLoading = false;

// Save button only enabled when the content changes
saveBtn.disabled = true
let originalText = codeEl.textContent;

codeEl.addEventListener("input", () => {
	saveBtn.disabled = codeEl.textContent === originalText
});

// Function to load a new document
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

		highlightCode(codeEl)

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

loadDoc(fileIndex);

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
        logs.textContent += data.message

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

// SELECTING LABELS WITH DROPDOWN

// Show dropdown when text is selected
codeEl.addEventListener("mouseup", () => {
    const selection = window.getSelection();
	
	// check if selection is not empty
    if (selection.rangeCount === 0) {
        dropdown.style.display = "none";
        return;
    }
	
	// check if selection is inside the xml display
    const range = selection.getRangeAt(0);
    if (!codeEl.contains(range.commonAncestorContainer)) {
        dropdown.style.display = "none";
        return;
    }
	
	// check if selection has more than whiteSpace
    const text = selection.toString().trim();
    if (!text) {
        dropdown.style.display = "none";
        return;
    }

    // Position dropdown near selection
    const rect = range.getBoundingClientRect();
    dropdown.style.left = rect.left + window.scrollX + "px";
    dropdown.style.top = rect.bottom + window.scrollY + "px";
    dropdown.style.display = "block";
	
	// Remember the current range
    dropdown.currentRange = range;
	
	// focus keyboard on dropdown
	dropdown.focus()
	dropdown.size = dropdown.options.length; //expand options
});

// Hide dropdown if user clicks outside
document.addEventListener("mousedown", (e) => {
    if (!dropdown.contains(e.target)) {
        dropdown.style.display = "none";
		dropdown.size = 0; //colapse options
    }
});

// When user selects a label (click or Enter) add a tag to the text
// Function to wrap selected text
function wrapSelection(label) {
    if (!dropdown.currentRange || !label) return;

    const range = dropdown.currentRange;
    const selectedText = range.toString();

    const tagNode = document.createTextNode(`<${label}>${selectedText}</${label}>`);
    range.deleteContents();
    range.insertNode(tagNode);

    // Reset dropdown
    //dropdown.selectedIndex = 0;
    dropdown.style.display = "none";
    dropdown.size = 0;
	
	// Close selection
	const selection = window.getSelection();
	selection.removeAllRanges();
	
	// Update codeEL to enable save buttton
    codeEl.dispatchEvent(new Event("input"));
    dropdown.currentRange = null;
	codeEl.focus()
	
	highlightCode(codeEl)
}

// Handle click on an option on dropdown
dropdown.addEventListener("click", (e) => {
    const selectedOption = dropdown.options[dropdown.selectedIndex];
    if (selectedOption && selectedOption.value) {
        wrapSelection(selectedOption.value);
    }
});

// Handle **Enter key**
dropdown.addEventListener("keydown", (e) => {
	
	const allowedKeys = ["Enter", "ArrowUp", "ArrowDown"];
	
    if (e.key === "Enter") {
        e.preventDefault();
        const selectedOption = dropdown.options[dropdown.selectedIndex];
        if (selectedOption && selectedOption.value) {
            wrapSelection(selectedOption.value);
        }
    }
	
	// If any other key is pressed, close dropdown and return focus
    if (!allowedKeys.includes(e.key)) {
        dropdown.style.display = "none";
        dropdown.size = 0;
        codeEl.focus(); // return focus to editor
    }
});

// Function to higlight the xml
function highlightCode(el) {
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => hljs.highlightElement(el));
    } else {
        setTimeout(() => hljs.highlightElement(el), 0);
    }
}