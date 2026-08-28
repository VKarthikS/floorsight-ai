import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
API_KEY = os.getenv("GEMINI_API_KEY")

if not PROJECT_ID or not BUCKET_NAME or not API_KEY:
    raise RuntimeError(
        "Set GOOGLE_CLOUD_PROJECT, GCS_BUCKET_NAME, and GEMINI_API_KEY."
    )
