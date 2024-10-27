# import google.generativeai as genai
import os
import json
from datetime import datetime
from prompt_template import POLARITY_TEMPLATE, KEYWORDS_TEMPLATE, CATEGORY_TEMPLATE




from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI")
client = OpenAI(api_key=api_key)
concerns = ['Stress', 'Depression', 'Bipolar disorder',
            'Anxiety', 'PTSD', 'ADHD', 'Insomnia']

def evaluate_response(user_response, question=None):
    messages = [{"role": "system", "content": POLARITY_TEMPLATE}]
    if question:
        messages.append({"role": "user", "content": f"Question: {question}\nUser response: {user_response}"})
    else:
        messages.append({"role": "user", "content": user_response})

    polarity_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
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
            {"role": "user", "content": user_response}
        ]
    )
    keywords = eval(keywords_response.choices[0].message.content)

    # Categorize response based on keywords
    category_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CATEGORY_TEMPLATE},
            {"role": "user", "content": str(keywords)}
        ]
    )
    category = eval(category_response.choices[0].message.content)
    category = {concern: category.get(concern, 0) for concern in concerns}
    print(polarity)
    print(keywords)
    print(category)
    return polarity, keywords, category

# # Process each message
# for msg in messages:
#     if msg.get("question") == "How are you doing?" and current_session["messages"]:
#         # Append the current session and start a new one
#         sessions.append(current_session)
#         current_session = {
#             "start_time": msg["timestamp"],
#             "messages": []
#         }

#     response = msg["response"]
#     question = msg["question"]

#     # Call Gemini API for analysis
#     polarity, keywords, category = analyze_with_gemini(response, question)

#     # Structure message with metrics
#     message_info = {
#         "question": question,
#         "response": response,
#         "metrics": {
#             "polarity": polarity,
#             "keywords": keywords,
#             "concerns": category,
#         }
#     }

#     # Add message to the current session
#     current_session["messages"].append(message_info)

# # Append the last session if it has messages
# if current_session["messages"]:
#     sessions.append(current_session)

# # Output structured sessions data in JSON format
# output = json.dumps({"sessions": sessions}, indent=4)
# print(output)
