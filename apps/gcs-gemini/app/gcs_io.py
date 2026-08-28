import io
from PIL import Image
from google.cloud import storage

def read_image_from_gcs_with_pillow(bucket_name: str, blob_name: str, client: storage.Client) -> Image.Image:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    image_bytes = blob.download_as_bytes()
    image_stream = io.BytesIO(image_bytes)

    img = Image.open(image_stream)
    img.load()  # important: avoid lazy-loading issues
    return img


def upload_bytes_to_gcs(bucket_name: str, blob_name: str, data: bytes, content_type: str, client: storage.Client):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)
