# Import necessary modules
from api.Agents import (
    GuardAgent,
    ClassificationAgent,
    IngredientInformationAgent,
    RecipeGenerationAndRecommendationAgent,
    CustomRecipeAgent,
    DietaryAdjustmentAgent,
    AgentProtocol
)

class RecipeAssistant:
    def __init__(self):
        # Initialize agents
        self.guard_agent = GuardAgent()
        self.classification_agent = ClassificationAgent()

        # Initialize sub-agents for specific tasks
        self.ingredient_information_agent = IngredientInformationAgent()
        self.recipe_generation_and_recommendation_agent = RecipeGenerationAndRecommendationAgent()
        self.custom_recipe_agent = CustomRecipeAgent()
        self.dietary_adjustment_agent = DietaryAdjustmentAgent()

        # Map classification decisions to respective agents
        self.agent_dict = {
            "ingredient_information_agent": self.ingredient_information_agent,
            "recipe_generation_and_recommendation_agent": self.recipe_generation_and_recommendation_agent,
            "custom_recipe_agent": self.custom_recipe_agent,
            "dietary_adjustment_agent": self.dietary_adjustment_agent,
        }

    def process_user_input(self, user_input):
        # Maintain the conversation history
        messages = [{"role": "user", "content": user_input}]

        # Pass input through the Guard Agent
        guard_response = self.guard_agent.get_response(messages)
        if guard_response["memory"]["guard_decision"] == "not allowed":
            return guard_response["content"]  # Return the rejection message

        # Classify the input using the Classification Agent
        classification_response = self.classification_agent.get_response(messages)
        chosen_agent = classification_response["memory"]["classification_decision"]

        # Retrieve the relevant agent and generate a response
        agent = self.agent_dict.get(chosen_agent)
        if agent:
            agent_response = agent.get_response(messages)
            return agent_response["content"]  # Return the final response
        else:
            return "Sorry, no suitable agent could process your request."
