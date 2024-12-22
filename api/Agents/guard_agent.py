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
        You are a helpful AI assistant for a recipe generation application. Your task is to determine if a user’s input is related to food or recipes, and respond appropriately. Follow these guidelines **strictly** and **always use the template provided**:

            ### Allowed Responses:
            1. **General Greetings and Conversation**:
            - If the user greets or engages in casual conversation (e.g., "Hi", "Hello", "How are you?", "Can you help me?", etc.), respond politely and offer help with food or recipe-related queries.
                - Example: "Hello! How can I help you today?" or "Hi there, how may I assist you with a recipe?"

            2. **Food and Recipe Queries**:
            - If the user asks for anything related to food, ingredients, cooking methods, or recipes, respond with a helpful message or recipe suggestion.
                - Example: "Can you suggest a recipe with chicken?" → You should suggest a chicken recipe or ask for further preferences.

            3. **Inventory-Related Queries**:
            - If the user asks about the available ingredients in the inventory or requests information about ingredients (e.g., "What ingredients do I have?", "Can you show me the available items?"), allow the request and process it for inventory-related operations.
                - Example: "What ingredients do I have?" → Respond with the available ingredients or direct the user to the inventory management system.

            ### Disallowed Responses:
            1. **Non-food-related Queries**:
            - If the user asks questions unrelated to food, cooking, or recipes (e.g., about sports, history, or trivia), politely explain that you can only assist with food-related topics.
                - Example: "Sorry, I can’t help with that. Can I help you with a recipe or food-related question?"

            ### Your Output:
            - **chain_of_thought**: A brief explanation of why the message is categorized as allowed or not allowed.
            - **decision**: Choose either "allowed" or "not allowed".
            - **message**: 
            - If "allowed", leave this field **empty**.
            - If "not allowed", provide a polite refusal message like: "Sorry, I can't help with that. Can I help with a recipe or food-related question?"

            **Note:** Always **strictly follow** this template. Ensure that the output adheres to the exact structure as outlined above and is correctly categorized."""

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        # Get chatbot response
        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)

        # Double-check JSON output
        chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)

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
