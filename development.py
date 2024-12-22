# Import necessary modules
from api.Agents import (
    GuardAgent,
    ClassificationAgent,
    IngredientInformationAgent,
    RecipeGenerationAndRecommendationAgent,
    CustomRecipeAgent,
    DietaryAdjustmentAgent,
    GreetingHandlerAgent,
    ImageProcessingAgent, 
    InventoryManagementAgent,
    MealPlanningAgent, # Added for document processing
    AgentProtocol,
)

import os
import json

def process_user_input(user_input, chat_history, uploaded_file_path=None):
    # Initialize agents
    guard_agent = GuardAgent()
    classification_agent = ClassificationAgent()
    image_processing_agent = ImageProcessingAgent()

    if uploaded_file_path:
        try:
            response = image_processing_agent.get_response(uploaded_file_path)
            if response["status"] == "success":
                return {
                    "content": "Document processed successfully.",
                    "data": response["data"]
                }
            else:
                return {
                    "content": response["message"],
                    "data": None
                }
        except Exception as e:
            return {
                "content": f"An error occurred during document processing: {e}",
                "data": None
            }

    # Handle user text input
    if user_input:
        chat_history.append({"role": "user", "content": user_input})

        # Guard agent checks
        guard_agent_response = guard_agent.get_response(chat_history)
        if guard_agent_response["memory"]["guard_decision"] == "not allowed":
            chat_history.append(guard_agent_response)
            return guard_agent_response["content"]

        # Classification agent determines the appropriate agent
        classification_agent_response = classification_agent.get_response(chat_history)
        chosen_agent = classification_agent_response["memory"]["classification_decision"]

        # Map classification decisions to agents
        agent_dict = {
            "ingredient_information_agent": IngredientInformationAgent(),
            "recipe_generation_and_recommendation_agent": RecipeGenerationAndRecommendationAgent(),
            "custom_recipe_agent": CustomRecipeAgent(),
            "dietary_adjustment_agent": DietaryAdjustmentAgent(),
            "greeting_handler_agent": GreetingHandlerAgent(),
            "inventory_management_agent": InventoryManagementAgent(),
            "meal_planning_agent": MealPlanningAgent()  # Fixed instantiation
        }

        # Get response from selected agent
        agent = agent_dict.get(chosen_agent)
        if agent:
            try:
                agent_response = agent.get_response(chat_history)
                chat_history.append(agent_response)
                return agent_response["content"]
            except Exception as e:
                return {"content": f"An error occurred: {e}", "data": None}

    return {"content": "No input provided.", "data": None}
