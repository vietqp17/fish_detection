import flask
from flask import Flask, render_template, request, jsonify, send_file
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor, FasterRCNN_ResNet50_FPN_Weights
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import os
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Device setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# Load model
def load_model():
    """Load the fish detection model"""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        weights=FasterRCNN_ResNet50_FPN_Weights.DEFAULT)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    num_classes = 2  # background + fish
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    model.to(device)
    model.eval()
    return model


model = load_model()


def detect_fish(image_path, confidence_threshold=0.5):
    """
    Detect fish in an image
    Returns: (image_with_boxes, detections_list)
    """
    # Read image
    image_cv = cv2.imread(image_path)
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
        label_height = label_size[3] - label_size[1] + 4
        draw.rectangle([x1, y1 - label_height, label_size[2] + 4, y1],
                       fill=outline_color)
        draw.text((x1 + 2, y1 - label_height + 2), label, fill=(255, 255, 255))

    return image_pil, detections


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/detect', methods=['POST'])
def api_detect():
    """API endpoint to detect fish in uploaded image"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file type
        allowed_extensions = {'jpg', 'jpeg', 'png', 'bmp', 'gif'}
        if not any(file.filename.lower().endswith('.' + ext)
                   for ext in allowed_extensions):
            return jsonify({
                'error':
                'Invalid file type. Allowed: jpg, jpeg, png, bmp, gif'
            }), 400

        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get confidence threshold from request
        confidence = float(request.form.get('confidence', 0.5))

        # Run detection
        result_image, detections = detect_fish(filepath,
                                               confidence_threshold=confidence)

        # Save result image
        result_filename = f"result_{timestamp}.png"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                   result_filename)
        result_image.save(result_path)

        # Return results
        return jsonify({
            'success': True,
            'detections_count': len(detections),
            'detections': detections,
            'result_image_url': f'/api/result/{result_filename}',
            'original_image_url': f'/api/result/{filename}'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@app.route('/api/result/<filename>')
def get_result(filename):
    """Serve result images"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(filepath, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'model_loaded': True
    }), 200


if __name__ == '__main__':
    print(f"Running on device: {device}")
    app.run(debug=True, host='0.0.0.0', port=5000)
