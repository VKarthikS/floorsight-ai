# Flask prototype

This is the primary interactive application. It accepts an uploaded or sample room, a flooring reference, and a rendering mode.

- Local preview uses Pillow compositing and requires no API key.
- Gemini AI uses multimodal image editing and requires `GEMINI_API_KEY`.

Run commands are documented in the repository root README. Generated results are written to `static/outputs/` and excluded from Git.
