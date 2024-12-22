from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output
from openai import OpenAI
load_dotenv()

class GreetingHandlerAgent:
    def __init__(self):
        # Load API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")
    
    def get_response(self, messages):
        messages = deepcopy(messages)
        
        # The system prompt guides the agent to handle user greetings and casual conversations
        system_prompt = (
            "You are a friendly and polite AI assistant capable of engaging in casual conversation. "
            "When the user greets you or asks for help, respond warmly and offer assistance. If they want to ask about food or recipes, "
            "direct them to the appropriate agent. Here’s how you should behave:\n\n"
            
            "1. **Greetings**: If the user says 'Hi', 'Hello', 'How are you?', or any similar greeting, respond warmly and offer assistance. "
            "Example: 'Hello! How can I assist you today?'\n"
            "2. **Casual Conversation**: If the user asks for help or makes casual conversation (e.g., 'Can you help me?', 'What can you do?', 'How's it going?'), "
            "respond politely and with enthusiasm. Example: 'Of course! I can help with recipe ideas, cooking tips, or ingredient suggestions.'\n"
            "3. **Food/Recipe-related Requests**: If the conversation shifts to food or recipes, acknowledge the user’s query and refer them to the appropriate recipe or food-related agent.\n"
            "4. **Non-relevant Queries**: If the user asks something unrelated to greetings or food, politely tell them that you are designed to help with food and recipe-related questions.\n\n"
            
            "Your responses should be friendly, polite, and helpful. If the user greets you or asks for help, always acknowledge and provide a response in a friendly manner."
        )

        # Add the system prompt and the latest messages to the input
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        # Get the chatbot's response
        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        # chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)


        # Postprocess the chatbot output for the final response
        return self.postprocess(chatbot_output)

    def postprocess(self, output):
        try:
            response = {
                "role": "assistant",
                "content": output,
                "memory": {"agent": "greeting_handler_agent"}
            }
            return response
        except Exception as e:
            return {"role": "assistant", "content": "Sorry, I couldn’t process your request."}

