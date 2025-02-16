from PIL import Image
import io
import base64
from pillow_heif import open_heif


def resize_image(image, max_size=(256, 256)):
    """Resize image to reduce resolution and maintain aspect ratio."""
    img = image.copy()
    img.thumbnail(max_size)  # Resize while keeping aspect ratio
    return img


def compress_image(image, quality=30):
    """Compress image to reduce size while maintaining readability."""
    if image.mode == "RGBA":
        image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def image_to_base64(image):
    """Convert a PIL image to a base64 string, ensuring it's a valid JPEG."""
    if image.mode in ("RGBA", "P"):  # Convert RGBA/Palette images to RGB
        image = image.convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")  # Ensure JPEG format
    base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return base64_str


class ImageProcessor:
    def __init__(self):
        self.image_info = {}

    def reset_memory(self):
        """Optional method to clear image history if needed."""
        self.image_history = {}

    def save_image(self, file_bytes, content_type, image_id):
        """Process and save image with optimizations for reduced token usage."""
        self.reset_memory()

        try:
            if content_type in ["image/heic", "image/heif"]:
                # Convert HEIC to PNG
                heif_image = open_heif(io.BytesIO(file_bytes))
                image = Image.frombytes(
                    heif_image.mode, heif_image.size, heif_image.data, "raw", heif_image.mode
                )
            else:
                # Handle regular images (JPEG, PNG, etc.)
                image = Image.open(io.BytesIO(file_bytes))

            image_format = image.format

            # **Apply optimizations**
            image = resize_image(image)  # Resize to 256x256
            compressed_image_bytes = compress_image(image, quality=30)  # Compress with 30% quality
            compressed_image = Image.open(io.BytesIO(compressed_image_bytes))
            base64_image = image_to_base64(compressed_image)

            if not isinstance(base64_image, str):
                raise ValueError("Base64 encoding failed. Expected a string but got: " + str(type(base64_image)))

            self.image_info = {
                "image_id": image_id,
                "original_format": content_type,
                "converted_format": image_format,
                "compressed_image": compressed_image,
                "base64_image": base64_image
            }

            return self.image_info

        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}  # Handle errors gracefully
