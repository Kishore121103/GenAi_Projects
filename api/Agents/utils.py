import openai
import os
from dotenv import load_dotenv



def get_chatbot_response(client,model_name, messages, temperature=0):

    # Prepare messages in the required format
    input_messages = []
    for message in messages:
        input_messages.append({"role": message["role"], "content": message["content"]})

    # Make a chat completion request
    response = client.chat.completions.create(
        model=model_name,  # Specify the Gemini model
        messages=input_messages,
        temperature=temperature,
        top_p=0.8,  # Nucleus sampling value
        max_tokens=2000  # Maximum tokens for response
    )

    # Extract and return the assistant's response
     # Extract and return the assistant's response
    chatbot_response = response.choices[0].message.content  # Access content attribute correctly
    print(chatbot_response)
    return chatbot_response

def double_check_json_output(client,model_name,json_string):
    prompt = f""" You will check this json string and correct any mistakes that will make it invalid. Then you will return the corrected json string. Nothing else. 
    If the Json is correct just return it.

    Do NOT return a single letter outside of the json string.

    {json_string}
    """

    messages = [{"role": "user", "content": prompt}]

    response = get_chatbot_response(client,model_name,messages)

    return response