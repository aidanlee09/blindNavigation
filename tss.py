from fastapi import HTTPException
from starlette.responses import FileResponse
import os
import requests
import time


def text_to_speech(text):
    api_key = os.getenv("ELEVENLABS_API_KEY")

    API_URL = "https://api.elevenlabs.io/v1/text-to-speech/9BWtsMINqrJLrRacOk9x"

    HEADERS = {
        "xi-api-key": api_key
    }

    body = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        "optimize_streaming_latency": 3,
        "output_format": "mp3_44100_128"
    }

    response = requests.post(API_URL, headers=HEADERS, json=body)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="API request failed")

    # Ensure output directory exists
    os.makedirs("audio", exist_ok=True)

    timestamp = int(time.time())
    filename = f"audio/output.mp3"

    # Write the binary response content to a file
    with open(filename, "wb") as f:
        f.write(response.content)