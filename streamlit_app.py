import streamlit as st
import requests
import os
from PyPDF2 import PdfReader
import io

st.title("Research Paper Section Generator (Chat Mode)")

# Get Hugging Face API token from Streamlit secrets
hf_api_token = st.secrets.get("HF_API_TOKEN", None)
if not hf_api_token:
    st.error("Hugging Face API token not found in secrets. Please add it in the Streamlit Cloud dashboard.")
    st.stop()

# Function to extract text from PDF bytes
def extract_text_from_pdf(file_bytes):
    text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text

# Function to generate text using Hugging Face API
def generate_section(topic, section, pdf_text=None, max_length=512):
    # API endpoint - using Llama-3.2-8B-Instruct (or any available model)
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-8B-Instruct"
    
    headers = {
        "Authorization": f"Bearer {hf_api_token}",
        "Content-Type": "application/json"
    }
    
    # Build the prompt
    if pdf_text:
        # Truncate PDF text to avoid exceeding token limits
        max_pdf_chars = 30000
        truncated_pdf = pdf_text[:max_pdf_chars]
        if len(pdf_text) > max_pdf_chars:
            truncated_pdf += "... [content truncated due to length]"
            
        prompt = (
            f"Generate the '{section}' section for a research paper on the topic: '{topic}'. "
            f"Base your response on the following research paper excerpts:\n\n"
            f"{truncated_pdf}"
        )
    else:
        prompt = (
            f"Generate the '{section}' section for a research paper on the topic: '{topic}'. "
            "Include comprehensive details and follow academic style."
        )
    
    # Request payload
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_length,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    
    try:
        with st.spinner("Generating content... This may take a minute."):
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            result = response.json()
            
            # Check response format
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            
            return result.get('generated_text', 'No text generated')
            
    except Exception as e:
        return f"Error generating text: {str(e)}"

# Main app interface
st.markdown("Upload your PDF research papers and specify the research topic. Then type the section you want (e.g., 'intro', 'methodology', etc.) in the chatbox.")

with st.form("chat_form"):
    topic = st.text_input("Enter the research topic", "Deep Learning for Medical Imaging")
    uploaded_files = st.file_uploader("Upload PDF(s) of research papers", type=["pdf"], accept_multiple_files=True)
    message = st.text_input("What section do you want to generate? (e.g., intro, literature review)")
    submitted = st.form_submit_button("Send")

if submitted:
    # Process PDFs if uploaded
    aggregated_text = ""
    if uploaded_files:
        for uploaded_file in uploaded_files:
            pdf_bytes = uploaded_file.getvalue()
            pdf_text = extract_text_from_pdf(pdf_bytes)
            aggregated_text += pdf_text + "\n"
    
    # Generate the text
    generated_text = generate_section(topic, message, aggregated_text if aggregated_text.strip() else None)
    
    # Display the result
    st.subheader(f"Generated '{message}' Section:")
    st.write(generated_text)

