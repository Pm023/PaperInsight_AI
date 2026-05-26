const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');

// Determine API base URL dynamically: use relative paths if served by the backend,
// or fallback to the standard port 8000 if opened via file:// or other frontend dev servers.
const API_BASE = window.location.protocol.startsWith('http') && !['5500', '3000', '5173', '8080'].includes(window.location.port)
    ? ""
    : "http://127.0.0.1:8000";

let globalWeakestSectionText = "The methodology section lacked sufficient detail regarding the evaluation metrics and baseline models used for comparison."; // dummy fallback

// Drag and Drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleUpload(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleUpload(e.target.files[0]);
    }
});

async function handleUpload(file) {
    if (file.type !== "application/pdf") {
        alert("Please upload a valid PDF file.");
        return;
    }

    uploadSection.classList.add('hidden');
    uploadSection.classList.remove('active-section');
    loadingSection.classList.remove('hidden');
    loadingSection.classList.add('active-section');

    const formData = new FormData();
    formData.append("file", file);

    try {
        // Assume backend is mounted serving the frontend on same domain/port
        const res = await fetch(`${API_BASE}/analyze`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.statusText}`);
        }

        const data = await res.json();
        renderResults(data);
    } catch (error) {
        console.error("Analysis failed:", error);
        alert(`Failed to analyze PDF. Error Details: ${error.message || error}\n\nPlease check browser console or backend logs.`);
        loadingSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        uploadSection.classList.add('active-section');
    }
}

function renderResults(data) {
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('active-section');

    // Setup main score
    document.getElementById('final-score').innerText = data.score.toFixed(1);
    document.getElementById('acc-prob').innerText = data.acceptance_probability;

    // Setup bars
    setTimeout(() => {
        document.getElementById('bar-novelty').style.width = `${(data.novelty_score / 10) * 100}%`;
        document.getElementById('score-novelty').innerText = data.novelty_score;

        document.getElementById('bar-method').style.width = `${(data.methodology_score / 10) * 100}%`;
        document.getElementById('score-method').innerText = data.methodology_score;

        document.getElementById('bar-clarity').style.width = `${(data.clarity_score / 10) * 100}%`;
        document.getElementById('score-clarity').innerText = data.clarity_score;

        document.getElementById('bar-results').style.width = `${(data.results_score / 10) * 100}%`;
        document.getElementById('score-results').innerText = data.results_score;
    }, 100);

    // Setup Lists
    const lstStrengths = document.getElementById('list-strengths');
    lstStrengths.innerHTML = "";
    data.strengths.forEach(s => {
        const li = document.createElement('li');
        li.innerText = s;
        lstStrengths.appendChild(li);
    });
    const lstWeaknesses = document.getElementById('list-weaknesses');
    lstWeaknesses.innerHTML = "";
    data.weaknesses.forEach(w => {
        const li = document.createElement('li');
        li.innerText = w;
        lstWeaknesses.appendChild(li);
    });


    const lstSuggestions = document.getElementById('list-suggestions');
    lstSuggestions.innerHTML = "";
    data.suggestions.forEach(s => {
        const li = document.createElement('li');
        li.innerText = s;
        lstSuggestions.appendChild(li);
    });
    
    // Save weakest section text for improving
    if (data.extracted_sections && data.weakest_section) {
        // Add a line break replacement to format multi-line if needed
        globalWeakestSectionText = data.extracted_sections[data.weakest_section] || "No content extracted for the weakest section.";
    }
}

// Improve Section Logic
document.getElementById('btn-improve').addEventListener('click', async () => {
    const btn = document.getElementById('btn-improve');
    const loader = document.getElementById('rewrite-loader');
    const container = document.getElementById('rewritten-text-container');
    const contentP = document.getElementById('rewritten-text-content');

    btn.disabled = true;
    loader.classList.remove('hidden');
    container.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/improve`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: globalWeakestSectionText })
        });
        
        const resData = await response.json();
        contentP.innerText = resData.improved_text;
        
        loader.classList.add('hidden');
        container.classList.remove('hidden');
    } catch(e) {
        console.error(e);
        alert("Failed to improve section.");
        loader.classList.add('hidden');
        btn.disabled = false;
    }
});
