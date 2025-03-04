from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from dotenv import load_dotenv
from huggingface_hub import login

# Load environment variables
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Authenticate with Hugging Face
login(token=HUGGINGFACE_TOKEN)

app = FastAPI()

print("🔹 Loading LLaMA 1B Model...")
model_name = "meta-llama/Llama-3.2-1B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=HUGGINGFACE_TOKEN)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto", token=HUGGINGFACE_TOKEN)

# Define the request body structure
class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_text(request: PromptRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt").to("mps")
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.7,  # Increases response randomness
        top_k=50,         # Avoids low-probability outputs
        top_p=0.9,        # Nucleus sampling for better diversity
        repetition_penalty=1.2  # Prevents repetitive responses
    )
    return {"response": tokenizer.decode(outputs[0], skip_special_tokens=True)}

