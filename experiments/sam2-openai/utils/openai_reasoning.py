import base64
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_flooring_reference(image_bytes):
    image_b64 = base64.b64encode(image_bytes).decode()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "Analyze this flooring image.\n"
                        "Return STRICT JSON with:\n"
                        "reference_type (texture_closeup or full_room),\n"
                        "pattern, orientation, scale_hint, rotation_deg"
                    )
                },
                {
                    "type": "input_image",
                    "image_base64": image_b64
                }
            ]
        }]
    )

    return response.output_text
