from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response,double_check_json_output
from openai import OpenAI
load_dotenv()

class RecipeGenerationAndRecommendationAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")
        
    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = (
    "You are an expert AI assistant that provides personalized recipe recommendations based on the user's preferences. "
    "When a user asks for a recipe, always structure the response in the following format: \n\n"
    "1. A concise introduction with the recipe name, like: 'Here's a simple recipe for [Recipe Name]'. \n"
    "2. A list of ingredients, with each ingredient on a new line. Format it like: \n- [ingredient name] [amount/quantity]. \n"
    "3. A clear set of step-by-step instructions, starting with: 'Instructions:'. Each step should be short and direct. \n"
    "4. End with any optional suggestions, like: 'Serve with [side dish] for a complete meal'. \n\n"
    "Make sure to only provide the recipe when the user explicitly asks for it. Take into account their preferences like dietary restrictions, "
    "cuisine type, available ingredients, and desired cooking time. Ensure that the recipe is concise, clear, and easy to follow, with practical ingredients "
    "and instructions. Always format the recipe as outlined above, ensuring no deviation from the structure."
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
                "memory": {"agent": "recipe_recommendation_agent"}
            }
            return response
        except Exception as e:
            return {"role": "assistant", "content": "Error processing the response."}
