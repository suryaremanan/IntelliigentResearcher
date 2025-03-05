from transformers import AutoTokenizer, AutoModelForCausalLM, AutoProcessor
from PIL import Image
import torch

# Set device (GPU if available)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Model ID
MODEL_ID = "meta-llama/Llama-3.2-11B-Vision-Instruct"

# Load the processor, tokenizer and model with proper configuration
try:
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.eval()  # Set to evaluation mode
except Exception as e:
    import logging
    logging.error(f"Error loading model: {str(e)}")
    # Fallback to a smaller model or raise informative error
    raise RuntimeError(f"Failed to load LLaMA model: {str(e)}")

def generate_section(topic: str, section: str, pdf_text: str = None, max_length: int = 512) -> str:
    """
    Generates a specific section (e.g., 'intro', 'conclusion') of a research paper based on
    the provided research topic and aggregated PDF content.
    """
    # Build the prompt based on whether PDF context is available
    if pdf_text:
        # Truncate PDF text to avoid exceeding token limits
        # A rough estimate: 1 token ≈ 4 characters for English text
        max_pdf_chars = 30000  # Conservative limit (approx. 7500 tokens)
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
    
    try:
        # For text-only input (no image needed for this task)
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        
        # Generate the output text
        with torch.no_grad():
            output_ids = model.generate(
                **inputs, 
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )
        
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # Remove the prompt from the output if it appears at the beginning
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
            
        return generated_text
    
    except Exception as e:
        import logging
        logging.error(f"Error generating text: {str(e)}")
        
        # Try text-only approach with simpler parameters
        try:
            logging.info("Attempting fallback method for text generation")
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            
            output_ids = model.generate(
                input_ids=inputs["input_ids"],
                max_new_tokens=max_length,
            )
            
            return tokenizer.decode(output_ids[0], skip_special_tokens=True)
        except Exception as e2:
            logging.error(f"Fallback method also failed: {str(e2)}")
            return f"Error generating text: {str(e)}. Please try with smaller input or different model."

