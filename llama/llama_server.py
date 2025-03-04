from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import os
from dotenv import load_dotenv
from huggingface_hub import login
import torch

# Load environment variables
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Authenticate with Hugging Face
login(token=HUGGINGFACE_TOKEN)

app = FastAPI()

print("🔹 Loading LLaMA 1B Model...")
model_name = "meta-llama/Llama-3.2-1B-Instruct"

# Initialize the Hugging Face pipeline for text generation
pipe = pipeline(
    "text-generation",
    model=model_name,
    torch_dtype=torch.bfloat16,  # BF16 is better than FP16 for stability
    device_map="auto",
    token=HUGGINGFACE_TOKEN
)

# Define the request body structure
class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_text(request: PromptRequest):
    # Structure the input as a conversation
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Keep responses concise and accurate."},
        {"role": "user", "content": request.prompt},
    ]

    # Generate text using the pipeline
    outputs = pipe(messages, max_new_tokens=100)

    # Extract the response from the pipeline output
    generated_text = outputs[0]["generated_text"]

    return {"response": generated_text}


