# Fish Vision - Web App

A web application for detecting fish in images using deep learning. Upload images and get real-time detection results with confidence scores and bounding boxes.

## Features

- 🐟 **AI-Powered Detection**: Uses Faster R-CNN ResNet50 FPN for accurate fish detection
- 📤 **Easy Upload**: Drag & drop or click to upload images
- 🎯 **Confidence Control**: Adjust detection sensitivity with a confidence threshold slider
- 🎨 **Visual Results**: See annotated images with detection boxes and confidence scores
- 📊 **Detailed Statistics**: View detection count and individual fish confidence levels
- ⚡ **GPU Support**: Automatically uses GPU if available, falls back to CPU

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

1. Clone the repository and navigate to the project directory:

```bash
cd fish_vision
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

If you have a GPU and want to use CUDA, install the appropriate PyTorch version:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Running the Web App

### Option 1: Direct Python

1. Start the Flask server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

3. Upload an image of fish and click "Detect Fish" to see the results

### Option 2: Docker (Recommended)

1. Ensure Docker and Docker Compose are installed
2. Run the application:

```bash
docker-compose up --build
```

3. Open your web browser and navigate to:

```
http://localhost:5000
```

For detailed Docker setup and GPU support, see [DOCKER.md](DOCKER.md)

## How It Works

1. **Upload**: Select or drag & drop an image containing fish
2. **Configure**: Adjust the confidence threshold (0-100%) - higher values are more selective
3. **Detect**: Click "Detect Fish" to run inference
4. **Results**: View the annotated image with bounding boxes and confidence scores

## Project Structure

```
fish_vision/
├── app.py                 # Flask web server
├── train.py              # Training script for the model
├── infer.py              # Inference utilities
├── dataset.py            # Dataset handling
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose orchestration
├── .dockerignore          # Files to exclude from Docker build
├── DOCKER.md             # Docker setup guide
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic
├── uploads/             # Uploaded images and results (auto-created)
└── data/                # Training/validation data
```

## Model Details

- **Architecture**: Faster R-CNN with ResNet50 backbone + FPN
- **Classes**: 2 (Background + Fish)
- **Input**: RGB images (any size)
- **Output**: Bounding boxes with confidence scores

## Configuration

You can customize the Flask app by editing `app.py`:

- **Port**: Change the port in the last line (default: 5000)
- **Max file size**: Modify `MAX_CONTENT_LENGTH` (default: 50MB)
- **Upload folder**: Change `UPLOAD_FOLDER` path
- **Confidence threshold**: Default is 0.5 (50%) - adjust in the UI

## Tips for Best Results

- Use clear, well-lit images of fish
- Keep image size reasonable (< 50MB)
- Start with the default 50% confidence threshold
- Lower the threshold to detect more fish (may include false positives)
- Raise the threshold to be more selective (may miss some fish)

## Troubleshooting

**Issue**: "CUDA out of memory"

- Solution: Close other GPU applications, reduce image size, or use CPU mode

**Issue**: Model takes too long to load

- Solution: First run is slower due to model download. Subsequent runs will be faster

**Issue**: "No module named torch"

- Solution: Make sure you've installed all dependencies: `pip install -r requirements.txt`

## API Endpoints

### POST /api/detect

Upload an image for fish detection.

**Parameters:**

- `file` (multipart/form-data): Image file
- `confidence` (float): Confidence threshold (0.0-1.0)

**Response:**

```json
{
  "success": true,
  "detections_count": 5,
  "detections": [
    {
      "id": 1,
      "confidence": "95.23%",
      "box": [x1, y1, x2, y2]
    }
  ],
  "result_image_url": "/api/result/result_20231215_120530.png",
  "original_image_url": "/api/result/20231215_120530_image.png"
}
```

### GET /api/health

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "device": "cuda" or "cpu",
  "model_loaded": true
}
```

## License

This project includes code for fish detection using deep learning. See your institution's guidelines for licensing.

## Support

For bugs, feature requests, or questions, please open an issue in the repository.
