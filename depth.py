import cv2
import torch
import os
import numpy as np
from scipy import stats
from depth_anything_v2.dpt import DepthAnythingV2
from sam import segment_anything


def depth_calculation(compressed_img):
    model_configs = {
        'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
        'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
        'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]}
    }

    encoder = 'vitb'  # or 'vits', 'vitb'
    dataset = 'hypersim'  # 'hypersim' for indoor model, 'vkitti' for outdoor model
    max_depth = 20  # 20 for indoor model, 80 for outdoor model

    model = DepthAnythingV2(**{**model_configs[encoder], 'max_depth': max_depth})

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = model.to(device)

    model.load_state_dict(
        torch.load(f'checkpoints/depth_anything_v2_metric_{dataset}_{encoder}.pth', map_location='cpu'))
    model.eval()

    depth = model.infer_image(compressed_img)  # HxW depth map in meters in numpy

    rounded_depth = np.round(depth, 2)

    # Compute statistics
    average = np.mean(rounded_depth)  # Mean (Average)
    mode_result = stats.mode(rounded_depth, axis=None)  # Flatten array and find mode
    mode = mode_result.mode if np.isscalar(mode_result.mode) else mode_result.mode[0]

    threshold = max(average, mode)

    sam_mask = segment_anything(compressed_img)

    mask = np.where(depth < threshold, depth, 0) * sam_mask

    non_zero_values = mask[mask != 0]  # Extract non-zero values
    distance_average = np.mean(non_zero_values) if non_zero_values.size > 0 else 0  # Avoid division by zero

    return distance_average