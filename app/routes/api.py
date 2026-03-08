import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
import torch
from app.services.detection import detect_fish, device

api_bp = Blueprint('api', __name__)


@api_bp.route('/detect', methods=['POST'])
def detect():
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
                'error': 'Invalid file type. Allowed: jpg, jpeg, png, bmp, gif'
            }), 400

        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get confidence threshold from request
        confidence = float(request.form.get('confidence', 0.5))

        # Run detection
        result_image, detections = detect_fish(filepath, confidence_threshold=confidence)

        # Save result image
        result_filename = f"result_{timestamp}.png"
        result_path = os.path.join(current_app.config['UPLOAD_FOLDER'], result_filename)
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


@api_bp.route('/result/<filename>')
def get_result(filename):
    """Serve result images"""
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        return send_file(filepath, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404


@api_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'model_loaded': True
    }), 200
