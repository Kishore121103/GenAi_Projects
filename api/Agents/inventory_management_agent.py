import requests
from dotenv import load_dotenv
import os
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output
from openai import OpenAI

load_dotenv()

class InventoryManagementAgent:
    def __init__(self):
        self.api_base_url = "http://localhost:5105"
        self.get_items_api = f"{self.api_base_url}/api/Message/get-items"  # Endpoint to fetch the groceries
        self.model_name = os.getenv("MODEL_NAME")
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

    def fetch_available_ingredients(self):
        """Fetch available ingredients from the API."""
        try:
            response = requests.get(self.get_items_api)
            if response.status_code == 200:
                # Check if the response is a list
                if isinstance(response.json(), list):
                    return {"data": response.json()}  # Wrap the list in a dictionary
                return response.json()  # Assume it’s already a dictionary
            else:
                return {"error": f"Error fetching ingredients: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"error": f"Failed to fetch ingredients: {e}"}

    def get_response(self, messages):
        """
        Generate a response based on the chat history and available ingredients.
        """
        # Fetch available ingredients from the external service
        ingredients_response = self.fetch_available_ingredients()
        if "error" in ingredients_response:
            return {"role": "assistant", "content": ingredients_response["error"]}

        # Extract the list of ingredients
        ingredients = ingredients_response.get("data", [])
        if not ingredients:
            return {"role": "assistant", "content": "No ingredients are available in the inventory."}

        # Construct a system prompt to guide the assistant
        system_prompt = (
            "You are an AI assistant managing inventory. "
            "You have access to a list of available ingredients in the inventory. "
            "Your tasks include: \n"
            "- Displaying the list of available ingredients when requested by the user.\n"
            "- Providing details such as ingredient names and available quantities.\n"
            "- Ensure the inventory list is current and easy to understand for the user.\n"
        )

        # Add system prompt and the assistant's available ingredients to the message list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"Here is the list of available ingredients: {ingredients}"}
        ] + messages[-3:]  # Add the last 3 user-assistant messages for context

        # Fix: Ensure correct arguments are passed to `get_chatbot_response`
        try:
            chatbot_output = get_chatbot_response(
                self.client,
                self.model_name,  # Ensure the correct model name is passed
                messages  # Pass messages as required
            )
        except Exception as e:
            return {"role": "assistant", "content": f"An error occurred while generating the response: {e}"}

        # Double-check the response
        # chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)

        return {
            "role": "assistant",
            "content": chatbot_output,
            "memory": {"agent": "inventory_management_agent"}
        }
