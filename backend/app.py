from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uvicorn

from pdf_parser import extract_text_from_pdf, detect_sections
from rag import evaluate_paper, improve_section

app = FastAPI(title="PaperInsight AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "dataset", "papers.json")

import traceback

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    contents = await file.read()
    
    try:
        text = extract_text_from_pdf(contents)
        sections = detect_sections(text)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
        
    try:
        # evaluate the paper using RAG and Gemini Agents
        evaluation = evaluate_paper(sections, DATASET_PATH)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during AI evaluation: {str(e)}")
    
    # Merge the parsed sections with the evaluation
    response_data = evaluation.model_dump()
    response_data["extracted_sections"] = {k: v[:200] + "..." if len(v) > 200 else v for k, v in sections.items() if v}
    response_data["weakest_section"] = "Methodology" if evaluation.methodology_score < evaluation.novelty_score else "Abstract" # generic fallback logic for demo
    
    return response_data

class ImproveRequest(BaseModel):
    text: str

@app.post("/improve")
async def improve_paper_section(request: ImproveRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required.")
    
    improved = improve_section(request.text)
    return {"improved_text": improved}

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
