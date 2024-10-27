from schema import User, Conversation, Message
from backend.prompt_template import POLARITY_TEMPLATE, KEYWORDS_TEMPLATE, CATEGORY_TEMPLATE, NEXT_QUESTION_TEMPLATE, PERSONA_TEMPLATE, TIMESHIFT_PERSONA_TEMPLATE, RECOMMENDATION_TEMPLATE
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


api_key = os.getenv("OPENAI")
client = OpenAI(api_key=api_key)
concerns = ['Stress', 'Depression', 'Bipolar disorder',
            'Anxiety', 'PTSD', 'ADHD', 'Insomnia']
user = User()

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
    return polarity, keywords, category


def get_next_question(conv_until_now):
    print(conv_until_now)
    print()
    next_question_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": NEXT_QUESTION_TEMPLATE}, {
            "role": "user", "content": conv_until_now}]
    )

    next_question = next_question_response.choices[0].message.content
    return next_question


conversation = []

initial_question = "How are you feeling today? "
question = initial_question
user_response = input(question + "\n")
conv_until_now = ""

while user_response != "exit":
    try:
        polarity, keywords, category = evaluate_response(user_response, question)
        print(polarity)
        print(keywords)
        print(category)

        message = Message(question=question, response=user_response,
                          polarity=polarity, keywords=keywords, concerns=category)
        conversation.append(message)
        conv_until_now += f"Assistant: {question}\nUser: {user_response}\n"

        question = get_next_question(conv_until_now)
        user_response = input(question + "\n")
    except Exception as e:
        print(e)
        break


start_time = "2022-10-10T12:00:00Z"
end_time = "2022-10-10T12:30:00Z"

polarity, keywords, category = evaluate_response(conv_until_now)

conversation = Conversation(messages=conversation, start_time=start_time,
                            end_time=end_time, polarity=polarity, keywords=keywords, concerns=category)
user.conversations.append(conversation)


def get_updated_persona(conversation):
    user_prompt = ""
    if user.conversations[-2].persona:
        user_prompt = "Initial persona: " + user.conversations[-2].persona + "\n"
    user_prompt += "Conversation: " + str(conversation)
    print(user_prompt)

    persona_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": PERSONA_TEMPLATE},
                  {"role": "user", "content": user_prompt}]
    )

    persona = persona_response.choices[0].message.content
    return persona


# print(conversation)
updated_persona = get_updated_persona(conversation)
print(updated_persona)

user.conversations[-1].persona = updated_persona


def time_shift_analysis(user):
    user_prompt = "Initial persona: " + user.conversations[-2].persona + "\n" + \
        "Updated persona: " + user.conversations[-1].persona + "\n"

    time_shift_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": TIMESHIFT_PERSONA_TEMPLATE},
                  {"role": "user", "content": user_prompt}]
    )

    time_shift = time_shift_response.choices[0].message.content
    return time_shift


time_shift = time_shift_analysis(user)
print(time_shift)



def get_recommendation(user):
    user_prompt = "Current persona: " + user.persona[-1] + "\n"
    recommendation_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": RECOMMENDATION_TEMPLATE},
                    {"role": "user", "content": user_prompt}]
    )

    recommendation = recommendation_response.choices[0].message.content
    return recommendation

recommendation = get_recommendation(user)
