from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import numpy as np

def segment_anything(compressed_img):
    sam = sam_model_registry["vit_b"](checkpoint="checkpoints/sam_vit_b_01ec64.pth")

    mask_generator = SamAutomaticMaskGenerator(sam)

    masks = mask_generator.generate(compressed_img)

    final_mask = np.zeros(compressed_img.shape[:2], dtype=np.uint8)

    # Combine all masks into one binary mask
    for mask in masks:
        final_mask |= mask["segmentation"].astype(np.uint8)

    return final_mask