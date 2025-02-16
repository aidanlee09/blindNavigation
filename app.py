from fastapi import FastAPI, UploadFile, File
from query_manager import QueryManager
from tss import text_to_speech
from fastapi import HTTPException
from starlette.responses import FileResponse

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
    text_to_speech(response)
    filepath = f"audio/output.mp3"
    try:
        return FileResponse(filepath, media_type="audio/mpeg", filename=filepath)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    # return {"description": response}

# @app.post("/follow-up/")
# async def follow_up(question: str):
#     followup_response = query_manager.ask_gpt(question)
#     query_manager.text_to_speech(followup_response)
#     return {"followup_response": followup_response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
