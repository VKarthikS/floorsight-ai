from typing import Optional
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

from .config import API_KEY

def replace_floor_gemini(
    kitchen_img: Image.Image,
    floor_sample_img: Image.Image,
    model: str = "gemini-2.5-flash-image-preview",
) -> Optional[bytes]:
    """
    Returns PNG bytes (or None if generation failed/refused).
    """
    client = genai.Client(api_key=API_KEY)

    prompt_text = (
        "This is a kitchen image. Replace the existing floor with the texture and style from the second image.\n"
        "Keep the cabinets, wall, appliances, and all other objects exactly as they are.\n"
        "The new floor should follow the perspective of the original kitchen floor."
    )

    response = client.models.generate_content(
        model=model,
        contents=[prompt_text, kitchen_img, floor_sample_img],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"]
            # If you later hit schema errors again, we’ll keep this minimal.
        ),
    )

    # Extract returned image bytes (robust path)
    try:
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
    except Exception:
        return None

    return None
