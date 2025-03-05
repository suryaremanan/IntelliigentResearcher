import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pdf_extractor import extract_text_from_pdf
from model import generate_section

app = FastAPI()
# Enable CORS (useful during local development with Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_generate(
    topic: str = Form(...),
    message: str = Form(...),
    pdf_files: List[UploadFile] = File(...)
):
    """
    Chat endpoint to generate a specific section of a research paper.
    - topic: The research topic.
    - message: The section you want (e.g., 'intro', 'methodology').
    - pdf_files: One or more PDF research papers to extract context from.
    """
    aggregated_text = ""
    for pdf in pdf_files:
        pdf_bytes = await pdf.read()
        pdf_text = extract_text_from_pdf(pdf_bytes)
        aggregated_text += pdf_text + "\n"
    
    if not aggregated_text.strip():
        return {"error": "No text extracted from the uploaded PDFs."}
    
    generated_text = generate_section(topic, section=message, pdf_text=aggregated_text)
    return {"generated_text": generated_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

