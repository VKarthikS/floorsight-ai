# Project overview

## Problem

Flooring is difficult to evaluate from a small product sample. This project explores whether image segmentation and generative image editing can produce a useful room-level preview from a room photo and flooring reference.

## Approaches explored

1. End-to-end generative editing with a room image, reference image, and constrained prompt.
2. Cloud batch processing with inputs and outputs stored in Google Cloud Storage.
3. Explicit floor segmentation followed by texture tiling, lighting transfer, and compositing.

## Technical challenges

- Restricting edits to the floor region.
- Preserving furniture, cabinetry, appliances, shadows, and reflections.
- Matching the floor texture to room perspective and scale.
- Handling model refusals or responses without an output image.
- Protecting uploaded images and API credentials.

## Future improvements

- Add automated tests and fixture images licensed for redistribution.
- Validate file types, dimensions, and upload limits.
- Add perspective-aware texture projection.
- Track model latency, cost, and visual-quality metrics.
- Add clear retention and deletion controls for uploaded images.
