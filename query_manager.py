import torch
import io
import openai
import uuid
import os
from PIL import Image
import pillow_heif
from dotenv import load_dotenv
import numpy as np
from elevenlabs import Voice, VoiceSettings, play
from elevenlabs.client import ElevenLabs

load_dotenv()

class QueryManager:
    def __init__(self, model):
        self.conversation_history = []  # Stores chat history
        self.image_history = {}         # Stores images as {image_id: PIL Image}
        self.depth_history = {}         # Stores depth recognition results
        self.sound_history = []         # Stores detected sounds
        self.gpt_history = {}           # Stores GPT responses
        self.model = model              # PyTorch depth recognition model
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    def save_image(self, file_bytes, content_type):
        """Saves an image to memory and converts HEIC if needed."""
        image_id = str(uuid.uuid4())  # Generate a unique ID

        try:
            if content_type in ["image/heic", "image/heif"]:
                # Convert HEIC to PNG
                heif_image = pillow_heif.open_heif(io.BytesIO(file_bytes))
                image = Image.frombytes(
                    heif_image.mode, heif_image.size, heif_image.data, "raw", heif_image.mode
                )
                image_format = "PNG"
            else:
                # Handle regular images (JPEG, PNG, etc.)
                image = Image.open(io.BytesIO(file_bytes))
                image_format = image.format

            self.image_history[image_id] = image
            return {"image_id": image_id, "original_format": content_type, "converted_format": image_format}

        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}

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

    def ask_gpt_about_image(self, image_id):
        """Uses GPT-4 to describe the scene based on an uploaded image."""
        if image_id not in self.image_history:
            return {"error": "Image ID not found."}

        prompt = "Describe the surroundings and objects in the uploaded image."
        return self.ask_gpt(prompt)

    # def ask_gpt(self, prompt):
    #     """Sends a prompt to GPT-4 and returns the response."""
    #     openai_api_key = os.getenv("OPENAI_API_KEY")
    #     response = openai.ChatCompletion.create(
    #         model="gpt-4",
    #         messages=[{"role": "system", "content": "You are assisting a visually impaired user."}]
    #                   + self.conversation_history
    #                   + [{"role": "user", "content": prompt}],
    #         api_key=openai_api_key
    #     )
    #     reply = response["choices"][0]["message"]["content"]
    #     self.conversation_history.append({"role": "assistant", "content": reply})
    #     return reply

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
