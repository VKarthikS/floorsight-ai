import cv2
import numpy as np

def apply_floor(base_img, floor_mask, flooring_img):
    h, w = base_img.shape[:2]

    # repeat flooring texture
    tile = cv2.resize(flooring_img, (300, 300))
    tiled = np.tile(tile, (h // 300 + 1, w // 300 + 1, 1))
    tiled = tiled[:h, :w]

    # lighting preservation
    gray = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    shading = cv2.GaussianBlur(gray, (51, 51), 0)
    shading = shading / shading.max()

    blended = tiled.astype(float)
    for c in range(3):
        blended[:, :, c] *= shading

    blended = blended.astype(np.uint8)

    mask_3c = cv2.merge([floor_mask]*3)
    inv_mask = cv2.bitwise_not(mask_3c)

    bg = cv2.bitwise_and(base_img, inv_mask)
    fg = cv2.bitwise_and(blended, mask_3c)

    return cv2.add(bg, fg)
