# 📄 PaperInsight AI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange.svg)

**PaperInsight AI** is an advanced, AI-powered system designed to analyze, score, and evaluate research papers with the rigor of a professional academic reviewer. By leveraging **Retrieval-Augmented Generation (RAG)** and **Google's Gemini AI**, the system employs a multi-agent architecture to autonomously parse PDFs, compare them against a dataset of prior work, and provide detailed, constructive feedback.

## ✨ Features

- **📄 Smart PDF Parsing:** Automatically detects and extracts key sections like Abstract, Introduction, Methodology, Results, and Conclusion from your PDF papers.
- **🧠 Multi-Agent Evaluation Framework:**
  - **Reviewer Agent:** Evaluates clarity, writing structure, and grammar.
  - **Research Agent:** Checks for novelty and academic contribution by comparing against an embedded local dataset.
  - **Data Agent:** Critiques the robustness of the methodology and results.
  - **Meta Agent:** Synthesizes the reviews to provide a final, balanced score.
- **🔍 RAG-Powered Plagiarism/Novelty Check:** Uses `sentence-transformers` and `faiss-cpu` to retrieve semantic matches against existing papers.
- **📊 Granular Scoring & Probability:** Outputs a 0-10 score across Novelty, Methodology, Clarity, and Results, along with an estimated Acceptability Probability.
- **💡 Iterative Improvement:** A dedicated endpoint to re-write and professionally improve weak sections.
- **🎨 Glassmorphism UI:** A sleek, modern frontend served natively via the backend.

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **AI/ML:** Google Gemini API (`gemini-2.5-flash`), Sentence-Transformers (`all-MiniLM-L6-v2`), FAISS Vector Index
- **PDF Processing:** PyMuPDF (`fitz`)
- **Frontend:** HTML, Vanilla CSS, Vanilla JS

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/PaperInsight-AI.git
cd PaperInsight-AI
```

### 2. Setup the Backend Environment
Navigate to the `backend` directory and install the required Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure API Keys
You need a Google Gemini API Key. Ensure that your `.env` file (inside the `backend/` directory) contains:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
Start the FastAPI server:
```bash
python app.py
```
The server will start on `http://127.0.0.1:8000`. The frontend will be served automatically from the root URL `/`.

## 📁 Project Structure

```text
PaperInsight-AI/
├── backend/
│   ├── app.py               # Main FastAPI server and routing
│   ├── pdf_parser.py        # PyMuPDF extraction and sectioning logic
│   ├── rag.py               # AI Agents, FAISS Index, and evaluation prompts
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # API Keys
├── frontend/
│   ├── index.html           # Main Application UI
│   ├── app.js               # Frontend logic and API integration
│   └── style.css            # Custom CSS styles (if segregated)
└── dataset/
    └── papers.json          # Local JSON database of papers for RAG context
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
This project is licensed under the MIT License.
