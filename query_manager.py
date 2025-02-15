import base64

import torch
import io
import uuid
import os
from PIL import Image
import pillow_heif
from dotenv import load_dotenv
import numpy as np
from elevenlabs import Voice, VoiceSettings, play
from elevenlabs.client import ElevenLabs
from llm_converse import converse
import json
from image_processor import ImageProcessor

load_dotenv()

class QueryManager:
    def __init__(self, model):
        self.image_processor = ImageProcessor()
        self.reset_memory()
        self.conversation_history = []  # Stores chat history
        self.image_history = {}         # Stores images as {image_id: PIL Image}
        self.depth_history = {}         # Stores depth recognition results
        self.sound_history = []         # Stores detected sounds
        self.gpt_history = {}           # Stores GPT responses
        self.model = model              # PyTorch depth recognition model
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    def reset_memory(self):
        """Clears all stored data in QueryManager."""
        self.conversation_history = []  # Reset chat history
        self.image_history = {}  # Reset stored images
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

            return processed_image

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

        json = converse(prompt, image, "gpt-4o")
        return json

    def detect_objects_and_estimate_depth(self, image_id):
        """Processes an image to detect objects and estimate depth."""
        if image_id not in self.image_history:
            return {"error": "Image ID not found."}

        image = self.image_history[image_id]
        transform = torch.nn.Sequential(torch.nn.Upsample(size=(256, 256), mode="bilinear"))
        img_tensor = transform(torch.tensor(np.array(image)).unsqueeze(0).float()).to(self.device)

        # Run depth recognition model
        with torch.no_grad():
            depth_map = self.model(img_tensor)

        depth_data = depth_map.squeeze().cpu().numpy().tolist()
        self.depth_history[image_id] = depth_data

        return {"depth_map": depth_data}


    def text_to_speech(self, text):
        """Converts GPT's response into speech using ElevenLabs."""
        print("🔊 Generating speech...")
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("Error: ElevenLabs API key not found. Check your .env file.")
            return

        client = ElevenLabs(api_key=api_key)
        try:
            # Convert text to speech
            audio = client.text_to_speech.convert(
                text=text,  # Fix: Use 'text' instead of 'input_text'
                voice_id="gOkFV1JMCt0G0n9xmBwV",  # Replace with a valid voice ID
                model_id="eleven_monolingual_v1",
                output_format="mp3_44100_128"
            )

            # Play the generated speech
            play(audio)

        except Exception as e:
            print(f"❌ Voice synthesis failed: {e}")
