import torch
import numpy as np
# from segment_anything import sam_model_registry, SamPredictor

MODEL_PATH = "sam2/sam2_hiera_large.pt"

sam = sam_model_registry["vit_h"](checkpoint=MODEL_PATH)
sam.to("cuda" if torch.cuda.is_available() else "cpu")
predictor = SamPredictor(sam)

def get_floor_mask(image_np):
    predictor.set_image(image_np)

    # prompt roughly bottom half of image
    h, w, _ = image_np.shape
    point_coords = np.array([[w // 2, int(h * 0.8)]])
    point_labels = np.array([1])

    masks, _, _ = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        multimask_output=False
    )

    return masks[0].astype(np.uint8) * 255
