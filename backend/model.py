import requests
import json
import logging
import os

def generate_section(topic: str, section: str, pdf_text: str = None, max_length: int = 512) -> str:
    """
    Generates a specific section of a research paper using Hugging Face Inference API
    """
    # Get API token from environment variable
    api_token = os.environ.get("HF_API_TOKEN")
    if not api_token:
        return "Error: Hugging Face API token not found"
    
    # API endpoint - you can change this to any model on Hugging Face
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-8B-Instruct"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
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
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        result = response.json()
        
        # The response format may vary depending on the model
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        
        return result.get('generated_text', 'No text generated')
        
    except Exception as e:
        logging.error(f"Error generating text: {str(e)}")
        return f"Error generating text: {str(e)}"

