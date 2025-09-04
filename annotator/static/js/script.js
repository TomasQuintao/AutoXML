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
const dropdown = document.getElementById("label-dropdown");
const logs = document.getElementById("logs");
const stateBox = document.getElementById("state-box");

let totalFiles = 0;
let isLoading = false;
let state = "ready"

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
		state = data.state

		// Update the input box and total and state box
		fileNumberInput.value = fileIndex + 1; // 1-based
		totalFilesEl.textContent = totalFiles;
		stateBox.textContent = state.toUpperCase()
		
		if (state==="ready") stateBox.style.backgroundColor = "#4CAF50"; // red;
		else if (state==="raw") stateBox.style.backgroundColor = "#F44336"; // red
		
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
        logs.textContent = data.message;// + "\n";

        // Reset baseline text
        //originalText = editedText;
        //saveBtn.disabled = true;
		if (data.success) {
			console.log("loading...");
			await loadDoc(fileIndex);
		}
		
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
	dropdown.focus();
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
	codeEl.focus();
	
	highlightCode(codeEl);
}

// Handle click on an option on dropdown
dropdown.addEventListener("click", (e) => {
    const selectedOption = dropdown.options[dropdown.selectedIndex];
    if (selectedOption && selectedOption.value) {
        wrapSelection(selectedOption.value);
    }
});

// Handle **Enter key** on dropdown
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

// Deleting tags when clicking
codeEl.addEventListener("click", (e) => {
    if (!e.target.classList.contains("hljs-tag")) return;

    const clickedTag = e.target.textContent.trim();
    const tagName = clickedTag.match(/^<\/?\s*([^\s>]+)/)[1];
    const isOpening = !clickedTag.startsWith("</");

    // Get all tag spans
    const tags = Array.from(codeEl.querySelectorAll(".hljs-tag"));

    let correspondingTag = null;
	let counter = 0;
    if (isOpening) {
        // Find the next closing tag with the same name
        for (let i = tags.indexOf(e.target) + 1; i < tags.length; i++) {
            const next_text = tags[i].textContent.trim();
            if (next_text.startsWith(`</${tagName}`)) {
				if (counter>0) counter--;
				else {
					correspondingTag = tags[i];
					break;
				}
            }
			if (next_text.startsWith(`<${tagName}`)) {counter++;}
        }
    } else {
        // Find the previous opening tag with the same name
        for (let i = tags.indexOf(e.target) - 1; i >= 0; i--) {
            const next_text = tags[i].textContent.trim();
            if (next_text.startsWith(`<${tagName}`)) {
				if (counter>0) counter--;
				else {
					correspondingTag = tags[i];
					break;
				}
            }
			if (next_text.startsWith(`</${tagName}`)) {counter++;}
        }
    }

    console.log("Clicked tag:", clickedTag);
    if (correspondingTag) {
		console.log("Corresponding tag:", correspondingTag.textContent);
		removeTag(e.target, correspondingTag);
	} 
});

// Function to remove tags from the text
function removeTag(openTag, closeTag) {
    // Remove the clicked/opening tag
    openTag.remove();

    // Remove the corresponding tag if it exists
    if (closeTag) closeTag.remove();

    // Trigger input event to enable save button
    codeEl.dispatchEvent(new Event("input"));

    // Optionally, re-highlight
    //highlightCode(codeEl);
}

// Function to higlight the xml
function highlightCode(el) {
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => hljs.highlightElement(el));
    } else {
        setTimeout(() => hljs.highlightElement(el), 0);
    }
}