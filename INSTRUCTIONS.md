# Citra KTR Map - YOLOv11 Smoking Detection System

Complete instructions for running the YOLOv11-based smoking detection system with Flask backend.

## Project Overview

This system uses YOLOv11 for detecting smoking activities in images. It provides a Flask API for training and prediction with automatic GPU/CPU detection.

### Detection Classes
- **ktr**: Main category (Kepatuhan Terhadap Regulasi)
- **Asbak**: Ashtray
- **Merokok**: Smoking (person smoking)
- **Rokok**: Cigarette

### Compliance Classification Rules
Based on detection results:
- **Patuh (Compliant)**: No Merokok & No Rokok detected
- **Tidak Patuh Ringan (Minor Violation)**: Has Rokok but No Merokok
- **Tidak Patuh Berat (Major Violation)**: Has Merokok detected

---

## Prerequisites

### System Requirements
- Python 3.8+
- CUDA-capable GPU (optional, for faster training)
- 8GB+ RAM recommended
- 10GB+ free disk space

### Required Python Packages
```bash
pip install ultralytics flask flask-cors torch pillow
```

---

## File Structure

```
Citra KTR Map/
├── data.yaml           # YOLO dataset configuration
├── train.py            # YOLOv11 training script
├── server.py           # Flask API server
├── train/              # Training dataset (images + labels)
│   ├── *.jpg/png/jpeg  # Image files
│   └── _annotations.coco.json
├── runs/train/exp/weights/
│   ├── best.pt         # Best trained model
│   └── last.pt         # Last checkpoint
├── uploads/            # Temporary upload folder
└── INSTRUCTIONS.md     # This file
```

---

## Quick Start

### Option 1: Using run.bat (Windows)

Simply run the provided `run.bat` file:
```cmd
run.bat
```

### Option 2: Manual Execution

#### Step 1: Install Dependencies
```bash
pip install ultralytics flask flask-cors torch pillow
```

#### Step 2: Train the Model
```bash
# Basic training with defaults (100 epochs)
python train.py

# Custom training
python train.py --epochs 50 --model yolo11n --batch 8

# Prepare dataset only (without training)
python train.py --prepare-only
```

#### Step 3: Start the Flask Server
```bash
python server.py
```

The server will start at `http://localhost:5000`

---

## API Endpoints

### 1. Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "runs/train/exp/weights/best.pt",
  "device": "cuda:0"
}
```

### 2. Start Training
```bash
POST /train
Content-Type: application/json

{
  "epochs": 100,
  "model": "yolo11n",
  "img_size": 640,
  "batch_size": 16
}
```

Response:
```json
{
  "status": "started",
  "message": "Training started in background",
  "config": {
    "epochs": 100,
    "model": "yolo11n",
    "img_size": 640,
    "batch_size": 16
  }
}
```

### 3. Get Status
```bash
GET /status
```

Response:
```json
{
  "training": {
    "is_training": false,
    "results": { ... }
  },
  "model": {
    "loaded": true,
    "path": "runs/train/exp/weights/best.pt",
    "device": "cuda:0"
  }
}
```

### 4. Predict Image
```bash
POST /predict
Content-Type: multipart/form-data

file: <image_file>
confidence: 0.25 (optional)
```

Response:
```json
{
  "detections": [
    {
      "class": "Merokok",
      "confidence": 0.87,
      "bbox": [120.5, 340.2, 450.8, 720.0]
    },
    {
      "class": "Rokok",
      "confidence": 0.92,
      "bbox": [380.1, 450.3, 420.5, 480.7]
    }
  ],
  "compliance": {
    "level": "tidak_patuh_berat",
    "status": "Major Violation / Tidak Patuh Berat",
    "description": "Smoking activity detected",
    "color": "red"
  },
  "summary": {
    "has_merokok": true,
    "has_rokok": true,
    "total_detections": 2
  }
}
```

### 5. Predict from Base64
```bash
POST /predict/base64
Content-Type: application/json

{
  "image": "base64_encoded_image_string",
  "confidence": 0.25
}
```

### 6. Get Classes
```bash
GET /classes
```

---

## Python Usage Examples

### Training
```python
from train import train_model, prepare_dataset

# Prepare dataset
prepare_dataset()

# Train model
results = train_model(
    epochs=50,
    model_variant='yolo11n',
    image_size=640,
    batch_size=16
)
print(results)
```

### Prediction
```python
from server import predict_image, load_model

# Load model
load_model('runs/train/exp/weights/best.pt')

# Predict
result = predict_image('test_image.jpg', confidence=0.25)
print(result)
```

---

## Training Configuration

### Model Variants
| Model   | Size  | Speed | Accuracy |
|---------|-------|-------|----------|
| yolo11n | 6.2MB | Fastest| Lower   |
| yolo11s | 12.5MB| Fast  | Medium   |
| yolo11m | 25.9MB| Medium| High     |
| yolo11l | 55.1MB| Slow  | Highest |

### Recommended Settings
- **GPU with 4GB+ VRAM**: batch=16, img_size=640
- **GPU with 8GB+ VRAM**: batch=32, img_size=640
- **CPU Only**: batch=4, img_size=416

---

## Troubleshooting

### No GPU Detected
The system automatically falls back to CPU if no GPU is available. Training on CPU is slower but will still work.

### Model Not Found Error
1. Run training first: `python train.py`
2. Or manually load model via API: `POST /model/load`

### Out of Memory Error
Reduce batch size:
```bash
python train.py --batch 4
```

### Port Already in Use
Change port in `server.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## Integration with Frontend

The frontend (HTML + JS + Leaflet) connects to this API:

```javascript
// Predict
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:5000/predict', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.compliance);
```

---

## Model Files

After training, the model files are saved in:
- `runs/train/exp/weights/best.pt` - Best model based on validation
- `runs/train/exp/weights/last.pt` - Last checkpoint

---

## License

This project is for educational and research purposes.

---

## Support

For issues and questions, please check:
1. Training logs in `runs/train/exp/`
2. Console output for error messages
3. Ensure all dependencies are installed correctly
