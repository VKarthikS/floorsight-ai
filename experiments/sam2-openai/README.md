# SAM2 + OpenAI experiment

This incomplete experiment separates the workflow into floor segmentation, reference analysis, and texture compositing. It is retained to document the explored architecture, not as a runnable application.

Known gaps:

- The segmentation experiment references the older `segment_anything` API while the checkpoint is named for SAM2.
- The model checkpoint is intentionally excluded from Git.
- The OpenAI image input and upload-stream handling need to be updated and tested.
- Texture compositing does not yet perform perspective projection.
