from fastapi import FastAPI, UploadFile, File
import torch
from query_manager import QueryManager

app = FastAPI()

depth_model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
query_manager = QueryManager(depth_model)

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = query_manager.save_image(file_bytes, file.content_type)
    return result

@app.post("/describe-image/")
async def describe_image(image_id: str):
    gpt_response = query_manager.ask_gpt_about_image(image_id)
    query_manager.text_to_speech(gpt_response)
    return {"gpt_response": gpt_response}

@app.post("/detect-depth/")
async def detect_depth(image_id: str):
    depth_result = query_manager.detect_objects_and_estimate_depth(image_id)
    return depth_result

# @app.post("/follow-up/")
# async def follow_up(question: str):
#     followup_response = query_manager.ask_gpt(question)
#     query_manager.text_to_speech(followup_response)
#     return {"followup_response": followup_response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
