from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
from backend.prompt_template import POLARITY_TEMPLATE, KEYWORDS_TEMPLATE, CATEGORY_TEMPLATE, NEXT_QUESTION_TEMPLATE
from schema.schema import User, Conversation, Message


api_key = os.getenv("OPENAI")
client = OpenAI(api_key=api_key)


def evaluate_response(user_response):
    user_response = user_response
    polarity_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": POLARITY_TEMPLATE}, {"role": "user", "content": user_response}]
    )

    polarity = int(polarity_response.choices[0].message.content)


    keywords_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": KEYWORDS_TEMPLATE}, {"role": "user", "content": user_response}]
    )

    keywords = eval(keywords_response.choices[0].message.content)
    # print(keywords)


    category_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": CATEGORY_TEMPLATE}, {"role": "user", "content": str(keywords)}]
    )

    category = eval(category_response.choices[0].message.content)
    # print(type(category))
    # print(category)

    return polarity, keywords, category


def get_next_question(conv_until_now):
    print(conv_until_now)
    print()
    next_question_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": NEXT_QUESTION_TEMPLATE}, {"role": "user", "content": conv_until_now}]
    )

    next_question = next_question_response.choices[0].message.content
    return next_question

conversation = []
concerns = ['Stress', 'Depression', 'Bipolar disorder', 'Anxiety', 'PTSD', 'ADHD', 'Insomnia']

initial_question = "How are you feeling today? "
question = initial_question
user_response = input(question + "\n")
conv_until_now = ""

while user_response != "exit":
    polarity, keywords, category = evaluate_response(user_response)
    category = {concern: category.get(concern, 0) for concern in concerns}
    print(polarity)
    print(keywords)
    print(category)

    message = Message(question=question, response=user_response, polarity=polarity, keywords=keywords, concerns=category)
    conversation.append(message)
    conv_until_now += f"Assistant: {question}\nUser: {user_response}\n"

    question = get_next_question(conv_until_now)
    user_response = input(question + "\n")


print(conversation)

start_time = "2022-10-10T12:00:00Z"
end_time = "2022-10-10T12:30:00Z"
polarity = sum([message.polarity for message in conversation]) / len(conversation)
keywords = [keyword for message in conversation for keyword in message.keywords]
concerns = {concern: sum([message.concerns[concern] for message in conversation]) / len(conversation) for message in conversation for concern in message.concerns}

conversation = Conversation(messages=conversation, start_time=start_time, end_time=end_time, polarity=polarity, keywords=keywords, concerns=concerns)

user = User(persona=[], conversations=[conversation])

print(user.json())