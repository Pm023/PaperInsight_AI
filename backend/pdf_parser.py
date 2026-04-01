import fitz
import re

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def detect_sections(text: str) -> dict:
    sections = {
        "Abstract": "",
        "Introduction": "",
        "Methodology": "",
        "Results": "",
        "Conclusion": ""
    }
    
    # Simple regex-based extraction
    patterns = {
        "Abstract": r"(?i)abstract[\s\S]*?(?=introduction|1\.?\s+introduction|$)",
        "Introduction": r"(?i)(?:introduction|1\.?\s+introduction)[\s\S]*?(?=methodology|methods|2\.?\s+method|related work|$)",
        "Methodology": r"(?i)(?:methodology|methods|proposed method)[\s\S]*?(?=results|experiments|evaluation|$)",
        "Results": r"(?i)(?:results|experiments|evaluation)[\s\S]*?(?=conclusion|discussion|$)",
        "Conclusion": r"(?i)(?:conclusion|discussion)[\s\S]*?(?=references|acknowledgments|$)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            # removing the section header word itself generically if we wanted, 
            # but returning the matched content is good enough for AI.
            sections[key] = match.group(0).strip()
            
    # If regex fails, fallback: just give the first chunks to Abstract
    if not sections["Abstract"] and len(text) > 500:
        sections["Abstract"] = text[:1500]
    
    return sections
