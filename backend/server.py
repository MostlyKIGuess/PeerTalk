from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
import os
from postprocessing import evaluate_response


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
    response: str
    question: str
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
    response = msg.response
    question = msg.question
    polarity, keywords, category = evaluate_response(response, question)

    # Structure message with metrics
    new_message = {
        "timestamp": timestamp,
        "question": question,
        "response": response,
        "metrics": {
            "polarity": polarity,
            "keywords": keywords,
            "concerns": category,
        }
    }

    # Append the new message to the list
    messages_list.append(new_message)

    # Save the entire list to the JSON file
    with open("messages.json", "w") as f:
        json.dump(messages_list, f, indent=4)

    return {"success": True, "receivedMessage": response}



@app.get("/api/messages")
async def get_messages():
    return {"messages": messages_list}


@app.get("/api/startsession")
async def start_session():
    messages_list.clear()
    user = None
    ret_val = None
    if os.path.exists("user.json"):
        with open("user.json", "r") as f:
            try:
                user = json.load(f)
                if len(user) == 0:
                    user = None
            except json.JSONDecodeError:
                user = None

    if user:
        ret_val = {
            "oldUser": True,
            "recommendation": user[-1]["recommendation"],
            "final_persona": user[-1]["final_persona"],
        }
        user.append(
            {
                "start_time": datetime.now().isoformat(),
                "messages": [],
                "recommendation": "",
                "final_persona": "",
                "metrics": {},
            }
        )
    else:
        ret_val = {"oldUser": False}
        user = [
            {
                "start_time": datetime.now().isoformat(),
                "messages": [],
                "recommendation": "",
                "final_persona": "",
                "metrics": {},
            }
        ]

    with open("user.json", "w") as f:
        json.dump(user, f)
    return ret_val


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port if necessary

