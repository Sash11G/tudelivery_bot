from openai import OpenAI
from config import Config

openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)

def interpret_response(user_response):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "Your job is to simply interpret a message and evaluate if its meaning is agreeing/yes or negating/no and reply with either 'yes' or 'no', also the message you receive might be in Spanish. In that case, do the same but check if the user says 'si' or 'no', and you must also respond with 'yes' or 'no'."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_response}"
                    }
                    ]
                }
            ]
    )

    answer = response.choices[0].message.content
    print(answer)
    return answer == 'yes'


# _______________________ NEW _________________________


def interpret_intent(user_response):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that interprets user messages into specific intents: 'finalize', 'add', 'edit'. Respond with one of these intents based on the user's input."},
            {"role": "user", "content": user_response}
        ]
    )

    answer = response.choices[0].message.content.strip().lower()
    return answer


def interpret_order(user_response, current_order):
    prompt = f"Current order: {current_order}\n\nUser message: {user_response}\n\nUpdate the order details with the user's new request. Reply with the updated order in JSON format."

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that tracks a user's grocery order. When given the current order and a new user message, you should update the order and return it in JSON format."},
            {"role": "user", "content": prompt}
        ]
    )

    updated_order = response.choices[0].message.content.strip()
    return json.loads(updated_order)
