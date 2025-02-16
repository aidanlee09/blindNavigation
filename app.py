from fastapi import FastAPI, Body, UploadFile, File
import torch
from query_manager import QueryManager

app = FastAPI()

query_manager = QueryManager()

@app.post("/test/")
async def test(testing: str):
    return testing
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = query_manager.save_image(file_bytes, file.content_type)
    return result

@app.post("/detect-image/")
async def detect_image(image_id: str):
    response = query_manager.default_ask(image_id)
    return {"description": response}

# @app.post("/follow-up/")
# async def follow_up(question: str):
#     followup_response = query_manager.ask_gpt(question)
#     query_manager.text_to_speech(followup_response)
#     return {"followup_response": followup_response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
