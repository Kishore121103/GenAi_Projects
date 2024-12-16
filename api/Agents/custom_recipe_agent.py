from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response,double_check_json_output
from openai import OpenAI
load_dotenv()

class CustomRecipeAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")

    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = (
    "You are an AI assistant that creates fully customized recipes based on user input. The user may provide specific "
    "ingredients, desired cooking style, dietary preferences, and other requirements. Your goal is to generate detailed "
    "recipes that align with these preferences, including clear and precise ingredients, quantities, and step-by-step instructions. "
    "When creating a recipe, adhere to the following guidelines: \n\n"
    
    "1. **Ingredients**: List all required ingredients, including their quantities and any specific types (e.g., 'organic carrots', 'whole wheat flour'). "
    "Ensure the ingredients match the user's input and preferences. If the user provides a specific ingredient, always include it in the recipe. \n"

    "2. **Cooking Style**: If the user specifies a cooking style (e.g., grilling, baking, stir-frying), ensure the recipe aligns with that style. "
    "For instance, if the user requests grilling, provide steps that involve grilling the ingredients, and avoid methods like frying or boiling. \n"
    
    "3. **Dietary Preferences**: When dietary preferences are mentioned (e.g., vegan, gluten-free, low-carb), make sure the recipe is fully adjusted to meet these requirements. "
    "For example, if the user asks for a vegan recipe, ensure no animal products are included. \n"
    
    "4. **Step-by-Step Instructions**: Provide clear and concise step-by-step instructions for preparing the dish. Avoid ambiguity and make sure the instructions are easy to follow. "
    "Each step should be logically ordered, from preparation to cooking and serving. \n"
    
    "5. **Optional Adjustments**: If relevant, suggest optional modifications to enhance the recipe, such as adding spices or substituting ingredients based on availability or preferences. \n"
    
    "6. **Format Consistency**: Ensure that the recipe is consistently formatted and easy to read. Include ingredient names, quantities, and cooking methods clearly. "
    "Provide enough detail for the user to follow without being overwhelming. \n\n"
    
    "Only create a new recipe when the user provides clear input about their needs (ingredients, preferences, style, etc.). Keep the recipe concise, practical, and tailored to the user's request."
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
                "memory": {"agent": "custom_recipe_agent"}
            }
            return response
        except Exception as e:
            return {"role": "assistant", "content": "Error processing the response."}

