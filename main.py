from fastapi import FastAPI, File, UploadFile
from PIL import Image
import pillow_heif
import io

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "🚀 FastAPI server is running!"}


@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    file_bytes = await file.read()

    # Detect file format
    if file.content_type in ["image/heic", "image/heif"]:
        try:
            # Convert HEIC to PIL Image
            heif_image = pillow_heif.open_heif(io.BytesIO(file_bytes))
            image = Image.frombytes(
                heif_image.mode, heif_image.size, heif_image.data, "raw", heif_image.mode
            )
            image_format = "PNG"  # Convert to PNG
        except Exception as e:
            return {"error": f"Failed to process HEIC file: {str(e)}"}

    else:
        try:
            # Handle regular image formats
            image = Image.open(io.BytesIO(file_bytes))
            image_format = image.format
        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}

    return {
        "filename": file.filename,
        "original_format": file.content_type,
        "converted_format": image_format
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
