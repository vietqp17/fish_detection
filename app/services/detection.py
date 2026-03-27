import os
import sys
from typing import cast

if sys.platform == 'darwin':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor, fasterrcnn_mobilenet_v3_large_320_fpn

from torchvision.models.detection import ssdlite320_mobilenet_v3_large

import cv2
from PIL import Image, ImageDraw

# Device setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# Load model
def load_model_old():
    """Load the fish detection model"""
    model = fasterrcnn_mobilenet_v3_large_320_fpn(weights='DEFAULT')

    # model = ssdlite320_mobilenet_v3_large(weights="DEFAULT")
    box_predictor = cast(FastRCNNPredictor, model.roi_heads.box_predictor)
    in_features = box_predictor.cls_score.in_features
    num_classes = 2  # background + fish
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    model.to(device)
    model.eval()
    return model


def load_model():
    """Load the fish detection model"""

    num_classes = 2  # background + fish

    model = ssdlite320_mobilenet_v3_large(
        weights=None,
        #   weights="DEFAULT",
        num_classes=num_classes)

    model.to(device)
    model.eval()
    return model


model = load_model()


def detect_fish(image_path, confidence_threshold=0.5):
    """
    Detect fish in an image
    Returns: (image_with_boxes, detections_list)
    """

    print("Detecting fish in image:", image_path)

    # Read image
    image_cv = cv2.imread(image_path)
    if image_cv is None:
        raise FileNotFoundError(f'Could not read image: {image_path}')

    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)

    # Convert to tensor
    image_tensor = torch.tensor(image_rgb, dtype=torch.float32).permute(
        2, 0, 1).unsqueeze(0) / 255.0
    image_tensor = image_tensor.to(device)

    # Run inference
    with torch.no_grad():
        predictions = model([image_tensor.squeeze(0)])

    # Extract results
    boxes = predictions[0]['boxes'].cpu().numpy()
    scores = predictions[0]['scores'].cpu().numpy()

    # Filter by confidence
    mask = scores >= confidence_threshold
    boxes = boxes[mask]
    scores = scores[mask]

    # Draw boxes on image
    draw = ImageDraw.Draw(image_pil)
    detections = []

    for i, (box, score) in enumerate(zip(boxes, scores)):
        x1, y1, x2, y2 = box
        confidence = float(score)

        detections.append({
            'id': i + 1,
            'confidence': f'{confidence:.2%}',
            'box': [float(x1), float(y1),
                    float(x2), float(y2)]
        })

        # Draw bounding box
        outline_color = (0, 255, 0)  # Green
        draw.rectangle([x1, y1, x2, y2], outline=outline_color, width=2)

        # Draw label
        label = f'Fish {i+1}: {confidence:.1%}'
        label_size = draw.textbbox((0, 0), label)
        label_width = label_size[2] - label_size[0] + 4
        label_height = label_size[3] - label_size[1] + 4
        draw.rectangle([x1, y1 - label_height, x1 + label_width, y1],
                       fill=outline_color)
        draw.text((x1 + 2, y1 - label_height + 2), label, fill=(255, 255, 255))

    return image_pil, detections
