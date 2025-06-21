import base64
import io
from typing import List

from PIL import Image


def encode_images_to_base64(images: List[Image.Image]) -> List[str]:
    """Encodes a list of PIL Images to base64 strings."""
    encoded_images = []
    for img in images:
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        encoded_images.append(base64.b64encode(buffered.getvalue()).decode("utf-8"))
    return encoded_images
