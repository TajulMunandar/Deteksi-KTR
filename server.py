"""
Flask API Server for Citra KTR Map
===================================
YOLOv11-based smoking detection API.
"""

import os
import threading
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import torch

# Configuration
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(PROJECT_DIR, "runs", "train", "exp", "weights")
BEST_MODEL = os.path.join(MODEL_DIR, "best.pt")
UPLOAD_FOLDER = "uploads"

CLASS_NAMES = {0: 'Merokok', 1: 'Rokok', 2: 'Merokok', 3: 'Rokok'}
CONFIDENCE_THRESHOLD = 0.25

# App state
model = None
model_loaded = False
device = None
is_predicting = False

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

app = Flask(__name__, template_folder=PROJECT_DIR, static_folder=PROJECT_DIR, static_url_path='')
CORS(app)


def get_device():
    if torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


def load_model():
    global model, model_loaded, device
    if not os.path.exists(BEST_MODEL):
        print("No model found!")
        return False
    try:
        device = get_device()
        model = YOLO(BEST_MODEL)
        model_loaded = True
        print(f"Model loaded ({device})")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def predict_image(image_path, confidence=CONFIDENCE_THRESHOLD):
    global is_predicting
    if not model_loaded:
        load_model()
    
    is_predicting = True
    results = model.predict(image_path, conf=confidence, imgsz=640, device=device, verbose=False)
    is_predicting = False
    
    detections = []
    detected_classes = []
    has_merokok = False
    has_rokok = False
    
    
    if results and len(results[0].boxes) > 0:
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = CLASS_NAMES.get(class_id, f'class_{class_id}')
            label = results[0].names[class_id]
            print("Label:", label)
            print("Confidence:", conf)
            
            detections.append({
                'class': class_name,
                'confidence': round(conf, 2),
                'bbox': [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
            })
            detected_classes.append(class_name)
            print(detected_classes)
            print(class_name)
            
            if class_name == 'Merokok':
                has_merokok = True
            elif class_name == 'Rokok':
                has_rokok = True
    
    # Determine compliance
    if not detections:
        compliance = {'level': 'patuh', 'status': 'Patuh', 'color': 'green'}
    elif has_merokok:
        compliance = {'level': 'tidak_patuh_berat', 'status': 'Tidak Patuh Berat', 'color': 'red'}
    elif has_rokok:
        compliance = {'level': 'tidak_patuh_ringan', 'status': 'Tidak Patuh Ringan', 'color': 'yellow'}
    else:
        compliance = {'level': 'patuh', 'status': 'Patuh', 'color': 'green'}
    
    return {
        'detections': detections,
        'has_detections': len(detections) > 0,
        'detected_classes': detected_classes,
        'compliance': compliance,
        'summary': {'has_merokok': has_merokok, 'has_rokok': has_rokok, 'total': len(detections)}
    }


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model_loaded})


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file', 'detections': []}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file', 'detections': []}), 400
    
    confidence = request.args.get('confidence', type=float, default=CONFIDENCE_THRESHOLD)
    print(confidence)
    # Save and predict
    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    result = predict_image(filepath, confidence)
    
    # Cleanup
    try:
        os.remove(filepath)
    except:
        pass
    
    return jsonify(result)


if __name__ == '__main__':
    print("Loading model...")
    load_model()
    print("Server ready: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
