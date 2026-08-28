import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

import app as floor_app


class FloorSightTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.original_outputs = floor_app.OUTPUTS_DIR
        floor_app.OUTPUTS_DIR = Path(self.temp_directory.name)
        floor_app.app.config.update(TESTING=True)
        self.client = floor_app.app.test_client()

    def tearDown(self):
        floor_app.OUTPUTS_DIR = self.original_outputs
        self.temp_directory.cleanup()

    def test_index_lists_sample_rooms_and_flooring(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"FloorSight", response.data)
        self.assertIn(b"Local preview", response.data)

    def test_local_preview_generates_an_image(self):
        floor_name = floor_app.image_options(floor_app.FLOORS_DIR)[0]
        room_name = floor_app.image_options(floor_app.ROOMS_DIR)[0]
        response = self.client.post(
            "/edit",
            data={
                "floor_choice": floor_name,
                "demo_room": room_name,
                "render_mode": "local",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Preview ready", response.data)
        self.assertEqual(len(list(floor_app.OUTPUTS_DIR.glob("*.jpg"))), 1)

    def test_invalid_upload_returns_a_clear_error(self):
        floor_name = floor_app.image_options(floor_app.FLOORS_DIR)[0]
        response = self.client.post(
            "/edit",
            data={
                "floor_choice": floor_name,
                "room": (io.BytesIO(b"not an image"), "room.jpg"),
                "render_mode": "local",
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Upload a valid JPG, PNG, or WebP image", response.data)

    def test_invalid_catalog_path_is_rejected(self):
        room_name = floor_app.image_options(floor_app.ROOMS_DIR)[0]
        response = self.client.post(
            "/edit",
            data={
                "floor_choice": "../secret.env",
                "demo_room": room_name,
                "render_mode": "local",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"catalogue image is unavailable", response.data)


if __name__ == "__main__":
    unittest.main()
