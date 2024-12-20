from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
import os

# from postprocessing import evaluate_response
from prompt_template import (
    PERSONA_TEMPLATE,
    TIMESHIFT_PERSONA_TEMPLATE,
    RECOMMENDATION_TEMPLATE,
    POLARITY_TEMPLATE,
    KEYWORDS_TEMPLATE,
    CATEGORY_TEMPLATE,
)


from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI")
client = OpenAI(api_key=api_key)


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
    question: str
    response: str
    timestamp: str
    typing_metrics: str


def get_user():
    user = None
    if os.path.exists("user.json"):
        with open("user.json", "r") as f:
            try:
                user = json.load(f)
                if len(user) == 0:
                    user = None
            except json.JSONDecodeError:
                user = None
    return user


def append_message(user, message):
    user[-1]["messages"].append(message)
    with open("user.json", "w") as f:
        json.dump(user, f)


@app.post("/api/messages/send")
async def send_message(msg: Message):
    # Create a timestamp for the message
    timestamp = datetime.now().isoformat()
    # Store the incoming user message and the AI's response
    response = msg.response
    question = msg.question
    polarity, keywords, category = evaluate_response(response, question)
    typing_metrics = json.loads(msg.typing_metrics)

    # Structure message with metrics
    new_message = {
        "timestamp": timestamp,
        "question": question,
        "response": response,
        "metrics": {
            "polarity": polarity,
            "keywords": keywords,
            "concerns": category,
        },
        "typing_metrics": typing_metrics,
    }

    # Append the message to the list
    user = get_user()
    if user:
        append_message(user, new_message)
    else:
        raise HTTPException(status_code=400, detail="Session not started")
    return {"success": True, "receivedMessage": new_message}


# @app.get("/api/messages")
# async def get_messages():
#     return {"messages": messages_list}


@app.get("/api/session/start")
async def start_session():
    ret_val = None
    user = get_user()

    if user:
        ret_val = {
            "oldUser": True,
            "recommendation": user[-1]["recommendation"],
            "final_persona": user[-1]["final_persona"],
        }
        if len(user) > 1 and user[-1]["final_persona"] == "":
            user[-1]["start_time"] = datetime.now().isoformat()
        else:
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


concerns = [
    "Stress",
    "Depression",
    "Bipolar disorder",
    "Anxiety",
    "PTSD",
    "ADHD",
    "Insomnia",
]


def evaluate_response(user_response, question=None):
    messages = [{"role": "system", "content": POLARITY_TEMPLATE}]
    if question:
        messages.append(
            {
                "role": "user",
                "content": f"Question: {question}\nUser response: {user_response}",
            }
        )
    else:
        messages.append({"role": "user", "content": user_response})

    polarity_response = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages
    )
    try:
        polarity = int(polarity_response.choices[0].message.content.strip())
    except (ValueError, IndexError, AttributeError) as e:
        raise ValueError("Failed to parse polarity response") from e

    # Extract keywords
    keywords_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": KEYWORDS_TEMPLATE},
            {"role": "user", "content": user_response},
        ],
    )
    keywords = eval(keywords_response.choices[0].message.content)

    # Categorize response based on keywords
    category_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CATEGORY_TEMPLATE},
            {"role": "user", "content": str(keywords)},
        ],
    )
    category = eval(category_response.choices[0].message.content)
    category = {concern: category.get(concern, 0) for concern in concerns}
    return polarity, keywords, category


def get_updated_persona(conversation):
    user = get_user()
    user_prompt = ""
    if len(user) > 1 and user[-2]["final_persona"]:
        user_prompt = "Initial persona: " + user[-2]["final_persona"] + "\n"
    else:
        user_prompt = "Initial persona: " + PERSONA_TEMPLATE + "\n"
    user_prompt += "Conversation: " + str(conversation)
    print(user_prompt)

    persona_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PERSONA_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
    )

    persona = persona_response.choices[0].message.content
    return persona


def time_shift_analysis(user):
    if len(user) < 2:
        return "Not enough data for time shift analysis"
    user_prompt = (
        "Initial persona: "
        + user[-2]["final_persona"]
        + "\n"
        + "Updated persona: "
        + user[-1]["final_persona"]
        + "\n"
    )

    time_shift_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": TIMESHIFT_PERSONA_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
    )

    time_shift = time_shift_response.choices[0].message.content
    return time_shift


def time_shift_analysis_overall(user):
    if len(user) < 2:
        return "Not enough data for time shift analysis"
    user_prompt = (
        "Initial persona: "
        + user[0]["final_persona"]
        + "\n"
        + "Updated persona: "
        + user[-1]["final_persona"]
        + "\n"
    )

    time_shift_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": TIMESHIFT_PERSONA_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
    )

    time_shift = time_shift_response.choices[0].message.content
    return time_shift


def get_recommendation(user):
    user_prompt = "Current persona: " + user[-1]["final_persona"] + "\n"
    recommendation_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": RECOMMENDATION_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
    )

    recommendation = recommendation_response.choices[0].message.content
    return recommendation


@app.get("/api/session/end")
async def end_session():
    print("Ending session")
    user = get_user()
    if user:
        conv_hist = ""
        for message in user[-1]["messages"]:
            conv_hist += f"Assistant: {message['question']}\nUser: {message['response']}\n"

        print(conv_hist)

        polarity, keywords, category = evaluate_response(conv_hist)
        user[-1]["metrics"] = {
            "polarity": polarity,
            "keywords": keywords,
            "concerns": category,
        }

        user[-1]["final_persona"] = get_updated_persona(conv_hist)
        user[-1]["time_shift"] = time_shift_analysis(user)
        user[-1]["recommendation"] = get_recommendation(user)

        avg_keystrokes = sum(
            [msg["typing_metrics"]["keystrokes"] for msg in user[-1]["messages"]]
        ) / len(user[-1]["messages"])
        avg_backspaces = sum(
            [msg["typing_metrics"]["backspaces"] for msg in user[-1]["messages"]]
        ) / len(user[-1]["messages"])
        avg_speed = sum(
            [msg["typing_metrics"]["typingSpeed"] for msg in user[-1]["messages"]]
        ) / len(user[-1]["messages"])

        user[-1]["metrics"]["keystrokes"] = avg_keystrokes
        user[-1]["metrics"]["backspaces"] = avg_backspaces
        user[-1]["metrics"]["speed"] = avg_speed

        with open("user.json", "w") as f:
            json.dump(user, f)

        return {
            "success": True,
            "recommendation": user[-1]["recommendation"],
            "time_shift": user[-1]["time_shift"],
        }
    else:
        raise HTTPException(status_code=400, detail="Session not started")


@app.get("/api/session/summary")
async def get_summary():
    user = get_user()
    if user:
        return user
    else:
        raise HTTPException(status_code=400, detail="Session not started")


@app.get("/api/session/overalltimeshift")
async def get_overalltimeshift():
    user = get_user()
    if user:
        return {"time_shift": time_shift_analysis_overall(user)}
    else:
        raise HTTPException(status_code=400, detail="Session not started")

@app.get("/api/reset")
async def reset():
    if os.path.exists("user.json"):
        os.remove("user.json")
    return {"success": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port if necessary
