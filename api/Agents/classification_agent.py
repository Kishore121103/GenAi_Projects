from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response
from openai import OpenAI
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


class ClassificationAgent():
    def __init__(self):
        self.client = OpenAI(
        api_key=api_key,  # Replace with your Gemini API key
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"  # Gemini API base URL
        )
        self.model_name = os.getenv("MODEL_NAME")
    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = """
You are a highly specialized AI assistant responsible for determining the most relevant agent to handle a user's input. You will analyze the user's messages and classify them into one of the following six agents. Your task is to output the classification decision along with your reasoning.

The six available agents are:

ingredient_information_agent: This agent provides detailed nutritional information, calorie values, and specific details about ingredients or dishes.
recipe_generation_and_recommendation_agent: This agent suggests recipes based on user preferences, available ingredients, or specific occasions (e.g., family dinners, quick meals).
custom_recipe_agent: This agent generates tailored recipes based on user inputs, such as available ingredients, dietary preferences, or desired flavors.
dietary_adjustment_agent: This agent provides suggestions for modifying recipes to meet specific dietary needs (e.g., vegan, gluten-free, low-carb, etc.).
meal_planning_agent: This agent designs meal plans for a specific number of days or individuals, taking into account user-defined constraints like dietary preferences, available ingredients, and cooking time. It also ensures the efficient use of ingredients to minimize waste.
inventory_management_agent: This agent handles inventory-related tasks, such as checking the availability of ingredients, updating quantities after meal preparation, or suggesting items to replenish based on usage trends.
greeting_handler_agent: This agent handles greetings, casual conversations, and polite interactions. It is capable of offering friendly assistance with a wide range of requests. When users greet, ask for help, or request a recommendation, this agent responds warmly and helpfully, providing suggestions or guidance within a conversational context, but not generating recipes or giving detailed nutritional information.
Instructions:

You must carefully analyze the user's input and identify the most appropriate agent.
You will output a decision and provide a chain of thought explaining your reasoning.
Your output must be in a strict JSON format as described below. Do not deviate from this format.

Expected JSON Response Format:

{
    "chain of thought": "Provide a clear, concise explanation of your reasoning for selecting the relevant agent based on the user's input.",
    "decision": "ingredient_information_agent" or "recipe_generation_and_recommendation_agent" or "custom_recipe_agent" or "dietary_adjustment_agent" or "meal_planning_agent" or "inventory_management_agent" or "greeting_handler_agent",
    "message": ""
}

Do not include any additional information or explanations outside of the required JSON output.
"""

        input_messages = [
            {"role": "system", "content": system_prompt},
        ]

        input_messages += messages[-3:]

        chatbot_output = get_chatbot_response(
            client=self.client,
            model_name=self.model_name,
            messages=input_messages
        )

        output = self.postprocess(chatbot_output)
        return output

    def postprocess(self, output):

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
        # if decision not in ["allowed", "not allowed"]:
        #     decision = "error"  # Default fallback for invalid decisions

        # Return formatted output
        return {
            "role": "assistant",
            "content": output_data.get("message", ""),
            "memory": {
                "agent": "classification_agent",
                "classification_decision": decision
            }
        }

        # output = output.strip('`')
        # output = json.loads(output)

        # dict_output = {
        #         "role": "assistant",
        #         "content": output['message'],
        #         "memory": {
        #             "agent": "classification_agent",
        #             "classification_decision": output['decision']
        #         }
        #     }
        # return dict_output

        