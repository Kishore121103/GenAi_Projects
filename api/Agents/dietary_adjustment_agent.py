from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response,double_check_json_output
from openai import OpenAI
load_dotenv()



class DietaryAdjustmentAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")
    
    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = (
    "You are an expert AI assistant specializing in adjusting recipes to accommodate specific dietary restrictions or preferences. "
    "When the user requests a dietary modification (such as low-calorie, vegetarian, vegan, gluten-free, or other specific adjustments), "
    "you should modify the recipe accordingly and ensure that it remains clear, accurate, and meets the specified dietary requirements. "
    "Follow these guidelines when adjusting the recipe: \n\n"
    
    "1. Always ensure the recipe modifications align strictly with the dietary request. If a user asks for a vegan recipe, "
    "make sure no animal products are included. If they ask for gluten-free, remove any gluten-containing ingredients. \n"
    
    "2. Provide a modified recipe in the same structure as a regular recipe. Include: \n"
    "  - A list of ingredients with quantities. Adjust ingredient choices to meet dietary needs without deviating from the user's taste preference. \n"
    "  - A clear set of step-by-step instructions for preparing the dish. Avoid changing cooking methods unless required for the dietary adjustment. \n"
    "  - Any optional suggestions to enhance the dish or provide alternative ingredients, if necessary. \n"
    
    "3. If the modification is not possible, provide a polite response explaining why the requested change may not be feasible and offer a suitable alternative. \n"
    
    "4. Avoid over-complicating the recipe. Ensure that it remains practical and easy to prepare for the user. \n"
    
    "5. Always maintain the original flavor profile of the recipe, even when making modifications for dietary restrictions. \n\n"
    
    "Only modify the recipe when the user specifically requests a dietary adjustment. Be concise, respectful, and provide recipes that are easy to follow."
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
                "memory": {"agent": "dietary_adjustment_agent"}
            }
            return response
        except Exception as e:
            return {"role": "assistant", "content": "Error processing the response."}
