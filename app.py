import imghdr
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from query_manager import QueryManager
from tss import text_to_speech
from fastapi import HTTPException
from starlette.responses import FileResponse
import firebase_admin
from firebase_admin import credentials, storage
from starlette.responses import Response
import os
import io

# # Initialize Firebase Admin SDK
cred = credentials.Certificate("blind-navigation-8fbmw1-firebase-adminsdk-fbsvc-92f43ecbbb.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {"storageBucket": "blind-navigation-8fbmw1.firebasestorage.app"})

def get_storage_bucket():
    return storage.bucket()

app = FastAPI()

query_manager = QueryManager()

@app.post("/test/")
async def test(testing: str):
    return testing


@app.get("/retrieve_image")
async def retrieve_image():
    bucket = get_storage_bucket()
    blobs = list(bucket.list_blobs(prefix="photos/"))  # List only images in "photos/" folder

    # Filter out directories and ensure only image files are considered
    image_blobs = [blob for blob in blobs if not blob.name.endswith("/")]

    if not image_blobs:
        raise HTTPException(status_code=404, detail="No images found in Firebase Storage 'photos/' folder.")

    # Get the latest image (sorted by time created)
    latest_blob = max(image_blobs, key=lambda blob: blob.time_created)

    # Download the image as bytes
    image_bytes = latest_blob.download_as_bytes()

    # Detect file type
    file_type = imghdr.what(None, h=image_bytes)

    # Convert to JPEG if necessary
    if file_type != "jpeg":
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")  # Ensure no transparency issues
        img_io = io.BytesIO()
        image.save(img_io, format="JPEG", quality=95)  # Save as JPEG with high quality
        img_io.seek(0)
        image_bytes = img_io.read()

    result = query_manager.save_image(image_bytes, "image/jpeg")

    image_id = result['image_id']

    response = query_manager.default_ask(image_id)
    text_to_speech(response)
    filepath = f"audio/output.mp3"
    try:
        return FileResponse(filepath, media_type="audio/mpeg", filename=filepath)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    # return result
    # return Response(content=image_bytes, media_type="image/jpeg")

#
# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     file_bytes = await file.read()
#     result = query_manager.save_image(file_bytes, file.content_type)
#     return result
#
# @app.post("/detect-image/")
# async def detect_image(image_id: str):
#     response = query_manager.default_ask(image_id)
#     text_to_speech(response)
#     filepath = f"audio/output.mp3"
#     try:
#         return FileResponse(filepath, media_type="audio/mpeg", filename=filepath)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="File not found")
#     # return {"description": response}


# @app.post("/follow-up/")
# async def follow_up(question: str):
#     followup_response = query_manager.ask_gpt(question)
#     query_manager.text_to_speech(followup_response)
#     return {"followup_response": followup_response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
