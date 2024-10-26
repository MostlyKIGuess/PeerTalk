from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
import os

app = FastAPI()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend's URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    user_message: str
    ai_response: str
    previous_ai_message: str
    timestamp: str

# Initialize a list to store messages
messages_list = []

# Load existing messages from the JSON file if it exists
if os.path.exists("messages.json"):
    try:
        with open("messages.json", "r") as f:
            messages_list = json.load(f)
            if not isinstance(messages_list, list):
                messages_list = []
    except json.JSONDecodeError:
        messages_list = []

@app.post("/api/messages/send")
async def send_message(msg: Message):
    # Create a timestamp for the message
    timestamp = datetime.now().isoformat()

    # Store the incoming user message and the AI's response
    response_message = msg.ai_response
    
    # Create a new message object
    new_message = {
        "user_message": msg.user_message,
        "ai_response": response_message,
        "previous_ai_message": msg.previous_ai_message,
        "timestamp": timestamp
    }

    # Append the new message to the list
    messages_list.append(new_message)

    # Save the entire list to the JSON file
    with open("messages.json", "w") as f:
        json.dump(messages_list, f, indent=4)

    return {"success": True, "receivedMessage": response_message}

@app.get("/api/messages")
async def get_messages():
    return {"messages": messages_list}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port if necessary