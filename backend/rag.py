import json
import os
import faiss
import numpy as np
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize Embedder (Using absolute best lightweight sentence transformer for local usage)
embedder = SentenceTransformer('all-MiniLM-L6-v2')
client = None
try:
    client = genai.Client() # Picks up GEMINI_API_KEY from environment
except Exception as e:
    print("Warning: Gemini client could not be initialized. Make sure GEMINI_API_KEY is set in your environment variables.")

class EvaluationResult(BaseModel):
    score: float = Field(description="Final score out of 10")
    acceptance_probability: str = Field(description="Probability of acceptance, e.g., '68%'")
    strengths: list[str] = Field(description="List of 2-3 strengths of the paper")
    weaknesses: list[str] = Field(description="List of 2-3 weaknesses of the paper")
    suggestions: list[str] = Field(description="List of actionable suggestions for improvement")
    novelty_score: float = Field(description="Novelty score out of 10")
    methodology_score: float = Field(description="Methodology score out of 10")
    clarity_score: float = Field(description="Clarity score out of 10")
    results_score: float = Field(description="Results score out of 10")

def load_dataset_and_build_index(dataset_path: str):
    if not os.path.exists(dataset_path):
        return [], None
    with open(dataset_path, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    if not papers:
        return [], None

    texts = [p.get('title', '') + " " + p.get('abstract', '') for p in papers]
    embeddings = embedder.encode(texts)
    
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings).astype('float32'))
    
    return papers, index

def retrieve(query: str, papers: list, index, top_k=2):
    if not index or not papers or not query.strip():
        return []
    query_embedding = embedder.encode([query]).astype('float32')
    D, I = index.search(query_embedding, top_k)
    results = [papers[i] for i in I[0] if i < len(papers) and i >= 0]
    return results

def evaluate_paper(sections: dict, dataset_path: str) -> EvaluationResult:
    papers, index = load_dataset_and_build_index(dataset_path)
    abstract = sections.get("Abstract", "")
    similar_papers = retrieve(abstract, papers, index)
    
    context_str = "\n\n".join([f"Title: {p['title']}\nAbstract: {p['abstract']}\nResults: {p.get('results', '')}" for p in similar_papers])
    
    paper_content = f"""
    Abstract: {sections.get('Abstract', '')}
    Introduction: {sections.get('Introduction', '')[:2000]}
    Methodology: {sections.get('Methodology', '')[:2000]}
    Results: {sections.get('Results', '')[:2000]}
    Conclusion: {sections.get('Conclusion', '')[:1000]}
    """

    prompt = f"""
    You are a Meta-Agent combining the reviews of 3 sub-agents (Reviewer, Research, Data) for a research paper evaluation.
    
    --- USER PAPER TO EVALUATE ---
    {paper_content}
    
    --- RETRIEVED SIMILAR PAPERS (Context for assessing novelty/plagiarism) ---
    {context_str}
    
    --- TASK ---
    Act as the following agents internally:
    1. Reviewer Agent: Evaluate the clarity, writing, and structure.
    2. Research Agent: Evaluate novelty and academic contribution based on the Retrieved Similar Papers provided above.
    3. Data Agent: Evaluate the methodology and results.
    4. Meta Agent: Combine findings and provide final scores.
    
    Weights for final score: 
    - Novelty (30%)
    - Methodology (25%)
    - Clarity (15%)
    - Results (20%)
    - Citations (10% - assume average 7/10 if not present).
    
    CRITICAL INSTRUCTIONS:
    - The provided text is extracted via PDF parsing and may have truncated or missing sections. Do not penalize the paper if a dedicated section (e.g., Methodology) is missing; evaluate based on the content present across all sections.
    - Be objective, constructive, and fair. High-quality or publishable papers MUST receive high scores (8-10).
    - Ensure the `acceptance_probability` closely matches the final score proportionally (e.g., a score of 8.5/10 should roughly translate to an 85% probability). Do not output low probabilities for high scores, or arbitrarily low numbers.
    """

    if not client or not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "YOUR_API_KEY_HERE":
        raise ValueError("GEMINI_API_KEY is not configured. Please add a valid Gemini API Key to the backend/.env file.")

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationResult,
            temperature=0.2,
        ),
    )
    
    return EvaluationResult.model_validate_json(response.text)

def improve_section(section_text: str) -> str:
    if not client or not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "YOUR_API_KEY_HERE":
        raise ValueError("GEMINI_API_KEY is not configured.")
        
    prompt = f"Improve the following section of a research paper to make it more professional, clearer, and academically rigorous. Fix grammar and enhance vocabulary. Return ONLY the improved text:\n\n{section_text}"
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4)
    )
    return response.text
