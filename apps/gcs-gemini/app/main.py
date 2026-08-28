from google.cloud import storage

from .config import PROJECT_ID, BUCKET_NAME
from .gcs_io import read_image_from_gcs_with_pillow, upload_bytes_to_gcs
from .render import replace_floor_gemini

def run_test():
    storage_client = storage.Client(project=PROJECT_ID)

    kitchen = read_image_from_gcs_with_pillow(BUCKET_NAME, "uploads/kitchen.jpg", storage_client)
    mocha   = read_image_from_gcs_with_pillow(BUCKET_NAME, "floors_catalog/mocha.jpg", storage_client)

    out_bytes = replace_floor_gemini(kitchen, mocha)
    if not out_bytes:
        raise RuntimeError("No image returned by Gemini.")

    upload_bytes_to_gcs(
        bucket_name=BUCKET_NAME,
        blob_name="outputs/kitchen_mocha.png",
        data=out_bytes,
        content_type="image/png",
        client=storage_client,
    )

    print("Done. Uploaded: gs://{}/outputs/kitchen_mocha.png".format(BUCKET_NAME))

if __name__ == "__main__":
    run_test()
