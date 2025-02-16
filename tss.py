from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import requests
import time
import aiofiles
from starlette.responses import FileResponse
import os
class TextRequest(BaseModel):
    text: str

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

    timestamp = int(time.time())
    filename = f"audio/output_{timestamp}.mpga"

    async with aiofiles.open(filename, "wb") as f:
        await f.write(response.content)

    return {"message": "Output saved successfully", "filename": filename}

@app.get("/download/{filename}")
async def download(filename: str):
    filepath = f"audio/{filename}"
    try:
        return FileResponse(filepath, media_type="audio/mpeg", filename=filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
