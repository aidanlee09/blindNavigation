import torch
import uuid
import os
from dotenv import load_dotenv
import numpy as np
from llm_converse import converse
from image_processor import ImageProcessor
import json
from depth import depth_calculation

load_dotenv()


def validate_json(json_data):
    """Validates if JSON has the correct format"""
    if not isinstance(json_data, dict):
        return False, "JSON is not a dictionary"

    # Required keys
    expected_keys = {"obstacle", "description"}

    # Check if all required keys are present
    if set(json_data.keys()) != expected_keys:
        return False, f"Missing or extra keys. Expected {expected_keys}, got {set(json_data.keys())}"

    # Check if `obstacle` is either 0 or 1
    if not isinstance(json_data["obstacle"], int) or json_data["obstacle"] not in [0, 1]:
        return False, "Invalid 'obstacle' value. Must be 0 or 1"

    # Check if `description` is a string
    if not isinstance(json_data["description"], str):
        return False, "Invalid 'description' value. Must be a string"

    return True, "Valid"

class QueryManager:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.reset_memory()
        self.conversation_history = []  # Stores chat history
        self.image_history = {}         # Stores images as {image_id: PIL Image}
        self.compressed_image_history = {} # Stores compressed images as {image_id: compressed image}
        self.depth_history = {}         # Stores depth recognition results
        self.sound_history = []         # Stores detected sounds
        self.gpt_history = {}           # Stores GPT responses
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    def reset_memory(self):
        """Clears all stored data in QueryManager."""
        self.conversation_history = []  # Reset chat history
        self.image_history = {}  # Reset stored images
        self.compressed_image_history = {}  # Reset stored images
        self.depth_history = {}  # Reset depth recognition results
        self.sound_history = []  # Reset detected sounds
        self.gpt_history = {}  # Reset stored GPT responses

    def save_image(self, file_bytes, content_type):
        self.reset_memory()

        image_id = str(uuid.uuid4())  # Generate a unique ID

        try:
            processed_image = self.image_processor.save_image(file_bytes, content_type, image_id)

            if "error" in processed_image:
                return processed_image  # Return error if processing fails

            # Store the optimized base64 image
            self.image_history[image_id] = processed_image["base64_image"]
            self.compressed_image_history[image_id] = processed_image["compressed_image"]

            return {"image_id": image_id}

        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}

    def default_ask(self, image_id):
        if image_id not in self.image_history:
            return {"error": "Image ID not found."}

        image = self.image_history.get(image_id)

        prompt_path = "prompts/obstacle.txt"

        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt = file.read().strip()

        json_string = converse(prompt, image, "gpt-4o")

        if json_string.startswith("```json"):
            json_string = json_string.replace("```json", "").strip()
        if json_string.endswith("```"):
            json_string = json_string.replace("```", "").strip()

        print(f"Received JSON string: {json_string}")

        data = json.loads(json_string)

        check, msg = validate_json(data)
        if not check:
            raise ValueError(f"Invalid JSON format: {msg}")

        if data['obstacle'] == 0:
            return data['description']

        if data['obstacle'] == 1:
            compressed_image = self.compressed_image_history[image_id]
            image = np.array(compressed_image)
            distance_to_obstacle = depth_calculation(image)
            obstacle_description = (f"{data['description']} Based on our calculations, the obstacle is approximately {distance_to_obstacle:.1f} meters away from you. "
                                    f"Please proceed with as much caution as possible.")
            return obstacle_description
