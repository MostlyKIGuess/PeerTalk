import google.generativeai as genai
import os
import json
from datetime import datetime

# Example messages
messages = [
       {
        "user_message": "hey i am kinda sad ",
        "ai_response": "Hey, I'm sorry to hear that you're feeling sad.  What's got you feeling down?  It's okay to talk about it. Sometimes just getting things out in the open helps, you know? \n",
        "previous_ai_message": "How are you doing?",
        "timestamp": "2024-10-27T03:44:44.109881"
    },
    {
        "user_message": "yeahm idk man this whole AI thing",
        "ai_response": "Haha, I get it! It's definitely a lot to wrap your head around, this whole AI thing.  What's making you feel that way?  Is it overwhelming, confusing, or just plain weird?  Let's talk about it. \ud83d\ude0a \n",
        "previous_ai_message": "Hey, I'm sorry to hear that you're feeling sad.  What's got you feeling down?  It's okay to talk about it. Sometimes just getting things out in the open helps, you know? \n",
        "timestamp": "2024-10-27T03:44:57.981684"
    },
    {
        "user_message": "what if it takes my job",
        "ai_response": "Oh no, that's a scary thought!  Tell me, what's making you think that might happen? It sounds like you're feeling anxious about the future, and that's totally understandable. It's always tough to feel uncertain about something as important as work. \n",
        "previous_ai_message": "Haha, I get it! It's definitely a lot to wrap your head around, this whole AI thing.  What's making you feel that way?  Is it overwhelming, confusing, or just plain weird?  Let's talk about it. \ud83d\ude0a \n",
        "timestamp": "2024-10-27T03:45:07.001779"
    },
    {
        "user_message": "idk man alright i will sleep",
        "ai_response": "Ah, the classic \"I'm gonna sleep it off\" approach.  Sometimes that's exactly what we need!  \ud83d\ude34  But hey, before you drift off, anything specific on your mind that's keeping you awake?  Maybe we can brainstorm some solutions for tomorrow. \ud83d\ude09 \n",
        "previous_ai_message": "Oh no, that's a scary thought!  Tell me, what's making you think that might happen? It sounds like you're feeling anxious about the future, and that's totally understandable. It's always tough to feel uncertain about something as important as work. \n",
        "timestamp": "2024-10-27T03:45:18.497992"
    },
    {
        "user_message": "i can't sleep rn as well but goodnight",
        "ai_response": "Ugh, the struggle is real!  Sleep just seems to disappear when you need it most, doesn't it?  What's keeping you up tonight?  Maybe we can brainstorm some calming thoughts to help you drift off.  Or, you know, if you're up for it, we could just chat and see where the night takes us. \ud83d\ude09  Good night to you too! \n",
        "previous_ai_message": "Ah, the classic \"I'm gonna sleep it off\" approach.  Sometimes that's exactly what we need!  \ud83d\ude34  But hey, before you drift off, anything specific on your mind that's keeping you awake?  Maybe we can brainstorm some solutions for tomorrow. \ud83d\ude09 \n",
        "timestamp": "2024-10-27T03:45:27.319112"
    },
    {
        "user_message": "hey ",
        "ai_response": "Hey there! What's going on today? \ud83d\ude0a  Anything you want to talk about? \n",
        "previous_ai_message": "How are you doing?",
        "timestamp": "2024-10-27T03:45:32.675523"
    },
    {
        "user_message": "yaeh so feeling better than yesterday",
        "ai_response": "That's great to hear!  What made today feel a little brighter than yesterday?  Sometimes even small shifts can make a big difference. \ud83d\ude0a \n",
        "previous_ai_message": "Hey there! What's going on today? \ud83d\ude0a  Anything you want to talk about? \n",
        "timestamp": "2024-10-27T03:45:43.079961"
    },
    {
        "user_message": "yeah prolly the sleep?",
        "ai_response": "Sounds like you're thinking about sleep, huh?  What's going on with it?  Is it not happening enough, or happening too much?  Or maybe it's just not the restful kind of sleep you're looking for?  Tell me more! \n",
        "previous_ai_message": "That's great to hear!  What made today feel a little brighter than yesterday?  Sometimes even small shifts can make a big difference. \ud83d\ude0a \n",
        "timestamp": "2024-10-27T03:45:51.661942"
    },
    {
        "user_message": "yeah it is tough lately ",
        "ai_response": "I hear you.  It sounds like things are feeling pretty rough right now.  What's been making things especially tough lately?  It's okay to just say whatever's on your mind - even if it doesn't feel like it makes sense.  Sometimes just getting it out there can help. \n",
        "previous_ai_message": "Sounds like you're thinking about sleep, huh?  What's going on with it?  Is it not happening enough, or happening too much?  Or maybe it's just not the restful kind of sleep you're looking for?  Tell me more! \n",
        "timestamp": "2024-10-27T03:46:03.322877"
    },
    {
        "user_message": "heyyyy ",
        "ai_response": "Hey there!  What's going on? \ud83d\ude0a  Anything exciting happening today?  \n",
        "previous_ai_message": "How are you doing?",
        "timestamp": "2024-10-27T03:46:23.499194"
    },
    {
        "user_message": "yeah i feel more secure about my job now",
        "ai_response": "That's great to hear! It sounds like you've been working hard and it's paying off.  What's changed that makes you feel more secure? \n",
        "previous_ai_message": "Hey there!  What's going on? \ud83d\ude0a  Anything exciting happening today?  \n",
        "timestamp": "2024-10-27T03:46:31.196247"
    },
    {
        "user_message": "idk i just realised ai can't take over my job",
        "ai_response": "Haha, that's a relief, right?  What kind of job do you have?  Is it one that's heavily reliant on creativity or human interaction?  I'm sure there's something unique about what you do that AI can't quite replicate.  \ud83d\ude09 \n",
        "previous_ai_message": "That's great to hear! It sounds like you've been working hard and it's paying off.  What's changed that makes you feel more secure? \n",
        "timestamp": "2024-10-27T03:46:38.820708"
    },
    {
        "user_message": "i feel much better",
        "ai_response": "That's wonderful to hear!  It's always a relief when things are looking up. What's been making you feel better lately?  Tell me all about it! \ud83d\ude0a \n",
        "previous_ai_message": "Haha, that's a relief, right?  What kind of job do you have?  Is it one that's heavily reliant on creativity or human interaction?  I'm sure there's something unique about what you do that AI can't quite replicate.  \ud83d\ude09 \n",
        "timestamp": "2024-10-27T03:46:42.311589"
    },
    {
        "user_message": "i will sleep now thanks tho",
        "ai_response": "Sounds like you're ready for some rest!  \ud83d\ude34  Hope you sleep well and wake up feeling refreshed.  Anything in particular you're looking forward to tomorrow? \n",
        "previous_ai_message": "That's wonderful to hear!  It's always a relief when things are looking up. What's been making you feel better lately?  Tell me all about it! \ud83d\ude0a \n",
        "timestamp": "2024-10-27T03:46:47.607392"
    },
    {
        "user_message": "nope just peace",
        "ai_response": "\"Nope, just peace\" - I love it!  Sometimes that's all we need, right?  What kind of peace are you feeling today? \ud83d\ude0c  Is it a quiet, calm kind of peace, or a joyful, energized kind of peace? \ud83d\ude04 \n",
        "previous_ai_message": "Sounds like you're ready for some rest!  \ud83d\ude34  Hope you sleep well and wake up feeling refreshed.  Anything in particular you're looking forward to tomorrow? \n",
        "timestamp": "2024-10-27T03:46:55.730351"
    }
    # Add additional messages as needed
]

# Set up API key (ensure it's added as an environment variable)
os.environ["API_KEY"] = "AIzaSyAD3Tfv9aCP1G_9CxE4Lkt9riv8z_81gGU"  # Replace with your actual API key
genai.configure(api_key=os.environ["API_KEY"])

# Initialize sessions list
sessions = []
current_session = {
    "start_time": None,
    "messages": []
}

# Function to analyze each message with the Gemini API
def analyze_with_gemini(user_message, ai_response):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt=user_message, context=ai_response)
    
    # Extract and organize specific metrics
    polarity = response.get("polarity", "neutral")
    keywords = response.get("keywords", [])
    concern_category = response.get("concern_category", "general")
    intensity_score = response.get("intensity_score", 0)
    sentiment_shift = response.get("sentiment_shift", "none")
    
    return polarity, keywords, concern_category, intensity_score, sentiment_shift

# Process each message
for msg in messages:
    if msg.get("previous_ai_message") == "How are you doing?" and current_session["messages"]:
        # Append the current session and start a new one
        sessions.append(current_session)
        current_session = {
            "start_time": msg["timestamp"],
            "messages": []
        }

    user_message = msg["user_message"]
    ai_response = msg["previous_ai_message"]

    # Call Gemini API for analysis
    polarity, keywords, category, intensity, sentiment_shift = analyze_with_gemini(user_message, ai_response)

    # Structure message with metrics
    message_info = {
        "question": ai_response,
        "response": user_message,
        "metrics": {
            "polarity": polarity,
            "keywords": keywords,
            "concern_category": category,
            "intensity_score": intensity,
            "sentiment_shift": sentiment_shift
        }
    }

    # Add message to the current session
    current_session["messages"].append(message_info)

# Append the last session if it has messages
if current_session["messages"]:
    sessions.append(current_session)

# Output structured sessions data in JSON format
output = json.dumps({"sessions": sessions}, indent=4)
print(output)
