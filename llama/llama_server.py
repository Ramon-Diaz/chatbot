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
    prompt: list

@app.post("/generate")
async def generate_text(request: PromptRequest):
    messages = request.prompt  # Expecting full conversation history from Rasa

    # Use the chat-style input format recommended for LLaMA
    formatted_prompt = [
        {"role": "system", "content": "You are a helpful AI assistant. Keep responses concise and accurate."}
    ]
    formatted_prompt.extend(messages)

    # Generate text using the pipeline
    outputs = pipe(formatted_prompt, max_new_tokens=150)

    # Extract only the assistant's response
    generated_text = outputs[0]["generated_text"]

    # Append only the assistant's response to chat history
    messages.append({"role": "assistant", "content": generated_text})

    # Return only the assistant's latest response
    return {"response": generated_text}







