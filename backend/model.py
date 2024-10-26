from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

app = FastAPI()

# Load the Hugging Face API token from the environment variable
# hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
hf_token = "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"

if not hf_token:
    raise EnvironmentError("HUGGINGFACE_HUB_TOKEN environment variable not set")

# Load the model and tokenizer with the token
config = PeftConfig.from_pretrained("zementalist/llama-3-8B-chat-psychotherapist", use_auth_token=hf_token)
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct", use_auth_token=hf_token)
model = PeftModel.from_pretrained(base_model, "zementalist/llama-3-8B-chat-psychotherapist", use_auth_token=hf_token)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct", use_auth_token=hf_token)

class ChatRequest(BaseModel):
    input_text: str

class ChatResponse(BaseModel):
    response_text: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    input_text = request.input_text
    inputs = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=100)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return ChatResponse(response_text=response_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)