import io
import os
import uuid
from pathlib import Path

from flask import Flask, render_template, request, url_for
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR.parents[1] / ".env")
FLOORS_DIR = BASE_DIR / "static" / "floors"
ROOMS_DIR = BASE_DIR / "static" / "rooms"
OUTPUTS_DIR = BASE_DIR / "static" / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_PIXELS = 20_000_000
MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024


def image_options(directory: Path):
    return [
        path.name
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower().lstrip(".") in ALLOWED_EXTENSIONS
    ]


def display_name(filename: str) -> str:
    return Path(filename).stem.replace("-", " ").replace("_", " ").title()


def safe_catalog_path(directory: Path, filename: str) -> Path:
    clean_name = secure_filename(filename)
    path = directory / clean_name
    if clean_name != filename or not path.is_file() or path.parent != directory:
        raise ValueError("The selected catalogue image is unavailable.")
    return path


def open_image(source) -> Image.Image:
    Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
    try:
        image = Image.open(source)
        image.verify()
        source.seek(0)
        image = Image.open(source)
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception as exc:
        raise ValueError("Upload a valid JPG, PNG, or WebP image.") from exc


def local_floor_preview(room: Image.Image, floor: Image.Image) -> Image.Image:
    """Build a fast offline concept preview over the lower room plane."""
    room = room.copy()
    room.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
    width, height = room.size

    tile_size = max(160, width // 5)
    tile = ImageOps.fit(floor, (tile_size, tile_size), Image.Resampling.LANCZOS)
    texture = Image.new("RGB", room.size)
    for y in range(0, height, tile_size):
        offset = -tile_size // 2 if (y // tile_size) % 2 else 0
        for x in range(offset, width, tile_size):
            texture.paste(tile, (x, y))

    grayscale = ImageOps.grayscale(room).filter(ImageFilter.GaussianBlur(radius=18))
    shading = ImageEnhance.Contrast(grayscale).enhance(0.65)
    shaded_texture = Image.blend(texture, Image.merge("RGB", (shading,) * 3), 0.28)

    mask = Image.new("L", room.size, 0)
    mask_pixels = mask.load()
    horizon = int(height * 0.58)
    for y in range(horizon, height):
        progress = (y - horizon) / max(1, height - horizon)
        inset = int((1 - progress) * width * 0.23)
        for x in range(inset, width - inset):
            mask_pixels[x, y] = 255
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(3, width // 260)))
    return Image.composite(shaded_texture, room, mask)


def gemini_floor_preview(room: Image.Image, floor: Image.Image) -> Image.Image:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None or types is None:
        raise RuntimeError("Gemini mode is not configured. Use Local preview or add GEMINI_API_KEY.")

    client = genai.Client(api_key=api_key)
    prompt = (
        "Replace only the visible flooring in the first room photo using the "
        "second image as the exact flooring reference. Preserve the camera angle, "
        "walls, cabinets, furniture, appliances, lighting, shadows, and crop. "
        "Return one realistic edited image."
    )
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt, room, floor],
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
    except Exception as exc:
        app.logger.exception("Gemini rendering failed")
        raise RuntimeError(
            "Gemini could not create this preview. Check the API key, model access, and quota."
        ) from exc
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return Image.open(io.BytesIO(inline.data)).convert("RGB")
    raise RuntimeError("The image model returned no edited image.")


def render_index(error=None):
    return render_template(
        "index.html",
        floors=[(name, display_name(name)) for name in image_options(FLOORS_DIR)],
        rooms=[(name, display_name(name)) for name in image_options(ROOMS_DIR)],
        gemini_ready=bool(os.getenv("GEMINI_API_KEY") and genai),
        error=error,
    )


@app.get("/")
def index():
    return render_index()


@app.post("/edit")
def edit():
    try:
        floor_name = request.form.get("floor_choice", "")
        with safe_catalog_path(FLOORS_DIR, floor_name).open("rb") as floor_file:
            floor = open_image(floor_file)

        room_upload = request.files.get("room")
        demo_room = request.form.get("demo_room", "")
        if room_upload and room_upload.filename:
            room = open_image(room_upload.stream)
            room_label = secure_filename(room_upload.filename) or "Uploaded room"
        elif demo_room:
            with safe_catalog_path(ROOMS_DIR, demo_room).open("rb") as room_file:
                room = open_image(room_file)
            room_label = display_name(demo_room)
        else:
            raise ValueError("Upload a room photo or select a sample room.")

        mode = "gemini" if request.form.get("render_mode") == "gemini" else "local"
        result = gemini_floor_preview(room, floor) if mode == "gemini" else local_floor_preview(room, floor)

        output_name = f"{uuid.uuid4().hex}.jpg"
        result.save(OUTPUTS_DIR / output_name, "JPEG", quality=92, optimize=True)
        return render_template(
            "result.html",
            output_url=url_for("static", filename=f"outputs/{output_name}"),
            floor_name=display_name(floor_name),
            room_name=room_label,
            render_mode="Gemini AI" if mode == "gemini" else "Local concept",
        )
    except (ValueError, RuntimeError) as exc:
        return render_index(str(exc)), 400


@app.errorhandler(413)
def too_large(_error):
    return render_template(
        "error.html",
        message="The image is larger than the 12 MB upload limit.",
    ), 413


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )
