# Google Cloud Storage + Gemini prototype

This batch prototype reads a room image and flooring reference from a configured GCS bucket, generates an edited image with Gemini, and uploads the result to the bucket.

Required environment variables:

- `GOOGLE_CLOUD_PROJECT`
- `GCS_BUCKET_NAME`
- `GEMINI_API_KEY`

Application Default Credentials must also have access to the configured bucket.
