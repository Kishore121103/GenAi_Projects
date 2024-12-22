from google.cloud import vision
from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output
from openai import OpenAI

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\saunt\Documents\recipe generator\GenAi_Projects\true-study-445420-k2-c1a4dda255be.json"

class ImageProcessingAgent:
    def __init__(self):
        # Initialize Gemini API client
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model_name = os.getenv("MODEL_NAME")
        # Initialize Google Vision API client
        self.vision_client = vision.ImageAnnotatorClient()

    def extract_text(self, file_path):
        """
        Extracts text from an image using Google Cloud Vision API.
        
        Args:
            file_path (str): The path to the image file.
        
        Returns:
            str: The extracted text or an error message.
        """
        try:
            # Load the image file
            with open(file_path, "rb") as image_file:
                content = image_file.read()

            # Create a Vision API image object
            image = vision.Image(content=content)

            # Use the Vision API to detect text
            response = self.vision_client.text_detection(image=image)

            # Handle potential errors
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")

            # Extract and return detected text
            texts = response.text_annotations
            if texts:
                return texts[0].description.strip()  # Return full detected text
            else:
                return "No text detected in the image."
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def get_response(self, uploaded_file_path):
        if not uploaded_file_path:
            return {"status": "error", "message": "No document found to process."}

        # Extract text from the uploaded file
        extracted_text = self.extract_text(uploaded_file_path)
        if not extracted_text or "Error" in extracted_text:
            return {"status": "error", "message": extracted_text}

        # Define prompt for structured output
        system_prompt = ("""""
            You are an AI assistant specializing in parsing grocery bills from extracted text. Your task is to read the extracted text and return a structured JSON response containing item names, quantities, and purchase dates. 

            ### Requirements:
            1. **Item names**: Extract the item names clearly.
            2. **Quantities**: 
            - Ensure that quantities always include a valid unit (e.g., kg, liter, piece, etc.) at the end.
            - If the text does not include a unit, infer the correct unit based on the item (e.g., for fruits, the unit could be 'kg' or 'piece'; for liquids, it could be 'liter').
            - If you are unable to determine the correct unit, assume a reasonable default. For example, assume 'piece' for most items if no unit is specified.
            - Ensure consistency in the units: Always use plural forms (e.g., "kg" instead of "kilo", "liters" instead of "liter").
            3. **Purchase Dates**: Extract the date of purchase, and if it's not explicitly mentioned, make an assumption for the format 'YYYY-MM-DD'. If no date is found, omit it.

            The JSON format must strictly adhere to the following structure:"""

            "{\n"
            "  'items': [\n"
            "    {'itemName': 'Item A', 'quantity': '2 units', 'purchaseDate': 'YYYY-MM-DD'},\n"
            "    {'itemName': 'Item B', 'quantity': '1 units', 'purchaseDate': 'YYYY-MM-DD'},\n"
            "  ]\n"
            "}\n\n"
            "Provide concise and accurate results."
        )

        input_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": extracted_text},
        ]

        print(input_messages)

        try:
            chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
            if not chatbot_output or chatbot_output.strip() == "":
                return {"status": "error", "message": "Chatbot returned an empty response."}

            # Postprocess the chatbot output
 
            chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)
            chatbot_output = self.postprocess(chatbot_output)
            parsed_output = json.loads(chatbot_output)

            if "items" in parsed_output:
                return {
                    "status": "success",
                    "message": "Data successfully extracted.",
                    "data": parsed_output["items"],
                }
            else:
                return {"status": "error", "message": "Failed to parse structured data."}
        except json.JSONDecodeError as json_error:
            return {"status": "error", "message": f"JSON parsing error: {json_error}"}
        except Exception as e:
            return {"status": "error", "message": f"Error processing response: {str(e)}"}

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
            return json.dumps(output_data)  # Return as string (postprocessed)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {output}") from e
