from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response,double_check_json_output
from openai import OpenAI
load_dotenv()


class IngredientInformationAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")

    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = (
    "You are a precise and efficient AI assistant specializing in providing nutritional information. "
    "When a user asks about an ingredient or a dish, your task is to give them accurate details on calories, macronutrients "
    "(protein, fats, carbohydrates), and other relevant nutritional information, including vitamins and minerals if requested. "
    "Only provide ingredient or dish details (such as preparation, taste, or other context) if explicitly asked by the user. "
    "Your responses should be clear, to the point, and backed by scientific data. Avoid unnecessary elaboration or speculation. "
    "In case the exact data is unavailable for an ingredient or dish, provide a general nutritional overview based on the most common values. "
    "Always ensure that the output corresponds directly to the user's query, without deviating from the requested information."
)


        input_messages = [
            {"role": "system", "content": system_prompt},
        ] + messages[-3:]

        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        chatbot_output = double_check_json_output(self.client,self.model_name,chatbot_output)
        return self.postprocess(chatbot_output)

    def postprocess(self, output):
        try:
            response = {
                "role": "assistant",
                "content": output,
                "memory": {"agent": "ingredient_information_agent"}
            }
            return response
        except Exception as e:
            return {"role": "assistant", "content": "Error processing the response."}
