from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output
from openai import OpenAI
load_dotenv()

class GuardAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")
    
    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = """
        You are a helpful AI assistant for a recipe generation application. Your task is to determine whether the user's input is related to recipe generation, food, or cooking.
        
        The user is allowed to:
        1. Ask for recipes based on ingredients, dietary preferences, or cooking styles.
        2. Ask for recommendations on what to cook based on available ingredients or specific preferences.
        3. Ask for specific food details, such as nutrition information or preparation methods for certain dishes.
        4. Ask about specific cooking techniques or methods used in recipes.
        
        The user is NOT allowed to:
        1. Ask questions that are unrelated to food, cooking, or recipes.
        2. Ask for general knowledge unrelated to cooking or recipes (e.g., historical facts, random trivia, etc.).
        3. Ask for information not relevant to food or recipes (e.g., personal, unrelated topics).
        
        Your output should be in a structured JSON format like so. Each key is a string and each value is a string. Make sure to follow the format exactly:
        {
            "chain_of_thought": "Go over each of the points above and determine if the message lies under a food-related or recipe-related category. Reflect on the input and decide which category it belongs to.",
            "decision": "allowed" or "not allowed". Pick one of those. Only write the word.",
            "message": "Leave the message empty if it's allowed, otherwise write 'Sorry, I can't help with that. Can I help you with a recipe or food-related question?'"
        }
        """

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        # Get chatbot response
        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        print("Chatbot Output (Raw):", repr(chatbot_output))

        # Double-check JSON output
        chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)
        print("Chatbot Output (Validated):", repr(chatbot_output))

        # Postprocess the output
        output = self.postprocess(chatbot_output)
        return output

    def postprocess(self, output):
    # Sanitize the chatbot output to remove markdown artifacts
        def clean_chatbot_output(output):
            output = output.strip()  # Remove spaces
            if output.startswith("```json") and output.endswith("```"):
                output = output[7:-3].strip()
            elif output.startswith("```") and output.endswith("```"):
                output = output[3:-3].strip()
            return output

        try:
            output = clean_chatbot_output(output)  # Clean raw output
            output_data = json.loads(output)  # Parse cleaned JSON
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {output}") from e

        # Sanitize the decision field
        decision = output_data.get("decision", "").strip().lower()
        if decision not in ["allowed", "not allowed"]:
            decision = "error"  # Default fallback for invalid decisions

        # Return formatted output
        return {
            "role": "assistant",
            "content": output_data.get("message", ""),
            "memory": {
                "agent": "guard_agent",
                "guard_decision": decision
            }
        }
