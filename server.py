"""
Flask API Server for Citra KTR Map
===================================
YOLOv11-based smoking detection API.
"""

import os
import csv
import threading
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import torch
import piexif

# Configuration
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(PROJECT_DIR, "runs", "train", "exp", "weights")
BEST_MODEL = os.path.join(MODEL_DIR, "best.pt")
UPLOAD_FOLDER = "uploads"
DATABASE_FILE = "database_detections.csv"

# CSV Database header fields
DB_FIELDS = [
    'id', 'timestamp', 'latitude', 'longitude', 
    'location_name', 'status', 'level', 'total_detections', 
    'has_merokok', 'has_rokok', 'filename', 'bbox_filename'
]

CLASS_NAMES = {0: 'Merokok', 1: 'Rokok'}
CONFIDENCE_THRESHOLD = 0.25

# App state
model = None
model_loaded = False
device = None
is_predicting = False

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Initialize CSV Database
def init_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
            writer.writeheader()

def save_to_database(result, filename=None):
    init_database()
    
    # Get next ID
    row_count = 0
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        row_count = sum(1 for line in f) - 1  # minus header
    
    gps = result.get('gps', {})
    summary = result.get('summary', {})
    compliance = result.get('compliance', {})
    
    record = {
        'id': row_count + 1,
        'timestamp': datetime.now().isoformat(),
        'latitude': gps.get('latitude', ''),
        'longitude': gps.get('longitude', ''),
        'location_name': result.get('location_name', ''),
        'status': compliance.get('status', ''),
        'level': compliance.get('level', ''),
        'total_detections': summary.get('total', 0),
        'has_merokok': summary.get('has_merokok', False),
        'has_rokok': summary.get('has_rokok', False),
        'filename': filename or '',
        'bbox_filename': result.get('bbox_filename', '')
    }
    
    with open(DATABASE_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
        writer.writerow(record)

def get_all_detections():
    init_database()
    detections = []
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['id'] = int(row['id'])
            row['total_detections'] = int(row['total_detections'])
            row['has_merokok'] = row['has_merokok'] == 'True'
            row['has_rokok'] = row['has_rokok'] == 'True'
            if row['latitude']:
                row['latitude'] = float(row['latitude'])
            if row['longitude']:
                row['longitude'] = float(row['longitude'])
            detections.append(row)
    return detections

init_database()

app = Flask(__name__, template_folder=PROJECT_DIR, static_folder=PROJECT_DIR, static_url_path='')
CORS(app, supports_credentials=True, origins="*")

# Serve upload folder static
@app.route('/uploads/<filename>')
def serve_upload(filename):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200


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


def extract_gps_data(image_path):
    """Extract latitude and longitude from image EXIF metadata."""
    try:
        exif_dict = piexif.load(image_path)
        gps_data = exif_dict.get('GPS', {})

        if not gps_data:
            return None

        # Extract latitude
        lat_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef)
        lat = gps_data.get(piexif.GPSIFD.GPSLatitude)
        if lat:
            lat_deg = lat[0][0] / lat[0][1]
            lat_min = lat[1][0] / lat[1][1]
            lat_sec = lat[2][0] / lat[2][1]
            latitude = lat_deg + (lat_min / 60.0) + (lat_sec / 3600.0)
            if lat_ref == 'S':
                latitude = -latitude
        else:
            latitude = None

        # Extract longitude
        lon_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef)
        lon = gps_data.get(piexif.GPSIFD.GPSLongitude)
        if lon:
            lon_deg = lon[0][0] / lon[0][1]
            lon_min = lon[1][0] / lon[1][1]
            lon_sec = lon[2][0] / lon[2][1]
            longitude = lon_deg + (lon_min / 60.0) + (lon_sec / 3600.0)
            if lon_ref == 'W':
                longitude = -longitude
        else:
            longitude = None

        if latitude is not None and longitude is not None:
            return {'latitude': latitude, 'longitude': longitude}
        return None
    except Exception as e:
        print(f"Error extracting GPS data: {e}")
        return None


def predict_image(image_path, confidence=CONFIDENCE_THRESHOLD, gps_data=None, return_bbox_base64=False):
    is_predicting = True
    results = model.predict(image_path, conf=confidence, imgsz=640, device=device, verbose=False)
    is_predicting = False
    
    detections = []
    detected_classes = []
    has_merokok = False
    has_rokok = False
    
    bbox_base64 = None
    # Generate base64 gambar dengan bbox untuk preview di FE
    if return_bbox_base64 and results and len(results) > 0:
        import io
        import base64
        from PIL import Image
        
        # Plot hasil deteksi ke memory
        img_array = results[0].plot()
        img = Image.fromarray(img_array[..., ::-1])  # BGR ke RGB
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        bbox_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    if results and len(results[0].boxes) > 0:
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            # Gunakan nama class asli dari model bukan mapping manual
            class_name = results[0].names[class_id]
            print("Label:", class_name)
            print("Confidence:", conf)
            
            detections.append({
                'class': class_name,
                'confidence': round(conf, 2),
                'bbox': [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
            })
            detected_classes.append(class_name)
            print(detected_classes)
            print(class_name)
            
            if 'merokok' in class_name.lower():
                has_merokok = True
            elif 'rokok' in class_name.lower():
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
    
    result = {
        'detections': detections,
        'has_detections': len(detections) > 0,
        'detected_classes': detected_classes,
        'compliance': compliance,
        'summary': {'has_merokok': has_merokok, 'has_rokok': has_rokok, 'total': len(detections)},
        'bbox_preview': bbox_base64
    }

    if gps_data:
        result['gps'] = gps_data

    return result


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model_loaded})

@app.route('/history', methods=['GET'])
def get_history():
    data = get_all_detections()
    return jsonify({
        'count': len(data),
        'detections': data
    })

@app.route('/clear-all', methods=['DELETE', 'OPTIONS'])
def clear_all_data():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
    
    try:
        init_database()
        
        # Hapus SEMUA file foto di folder uploads
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except:
                pass
        
        # Kosongkan database CSV
        with open(DATABASE_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
            writer.writeheader()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Clear all error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_detection(id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
    
    try:
        init_database()
        rows = []
        deleted_filename = None
        
        # Baca semua baris
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['id']) == id:
                    deleted_filename = row['filename']
                else:
                    rows.append(row)
        
        # Tulis ulang tanpa baris yang dihapus
        with open(DATABASE_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        
        # Hapus file foto juga jika ada
        if deleted_filename:
            photo_path = os.path.join(UPLOAD_FOLDER, deleted_filename)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/save', methods=['POST', 'OPTIONS'])
def save_manual():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
        
    try:
        location_name = request.form.get('location_name')
        category = request.form.get('category')
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        if not all([location_name, category, latitude, longitude]):
            return jsonify({'success': False, 'error': 'Data tidak lengkap'}), 400
        
        bbox_filename = ''
        
        # Hanya simpan file jika ada upload foto
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                # Buat nama file
                safe_location = location_name.replace(' ', '_') if location_name else 'unknown'
                bbox_filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_location}_bbox.jpg")
                temp_filepath = os.path.join(UPLOAD_FOLDER, f"temp_{bbox_filename}")
                
                # Simpan file sementara untuk deteksi
                photo.save(temp_filepath)
                
                # Lakukan deteksi dan generate bounding box
                results = model.predict(temp_filepath, conf=CONFIDENCE_THRESHOLD, imgsz=640, device=device, verbose=False)
                
                # Simpan hanya gambar dengan bounding box
                bbox_filepath = os.path.join(UPLOAD_FOLDER, bbox_filename)
                results[0].save(filename=bbox_filepath)
                
                # Hapus file asli, yang disimpan hanya bbox saja
                os.unlink(temp_filepath)
        
        # Mapping category ke compliance status
        compliance_map = {
            'patuh': {'status': 'Patuh', 'level': 'patuh'},
            'ringan': {'status': 'Tidak Patuh Ringan', 'level': 'tidak_patuh_ringan'},
            'berat': {'status': 'Tidak Patuh Berat', 'level': 'tidak_patuh_berat'}
        }
        
        compliance = compliance_map.get(category, compliance_map['berat'])
        
        # Buat result format untuk disimpan ke database
        result = {
            'gps': {'latitude': latitude, 'longitude': longitude},
            'location_name': location_name,
            'summary': {
                'total': 1,
                'has_merokok': category == 'berat',
                'has_rokok': category == 'ringan'
            },
            'compliance': compliance,
            'bbox_filename': bbox_filename
        }
        
        # Simpan ke database
        save_to_database(result, bbox_filename)
        
        return jsonify({'success': True, 'message': 'Data tersimpan', 'bbox_filename': bbox_filename})
        
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    import tempfile
    if 'file' not in request.files:
        return jsonify({'error': 'No file', 'detections': []}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file', 'detections': []}), 400
    
    confidence = request.args.get('confidence', type=float, default=CONFIDENCE_THRESHOLD)
    
    # Buat file sementara saja, tidak simpan permanen
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        file.save(temp_file.name)
        temp_filepath = temp_file.name

    # Extract GPS data from image
    gps_data = extract_gps_data(temp_filepath)
    if gps_data:
        print(f"GPS data extracted: {gps_data}")

    result = predict_image(temp_filepath, confidence, gps_data, return_bbox_base64=True)
    
    # Hapus file sementara setelah deteksi
    import os
    os.unlink(temp_filepath)
    
    return jsonify({
        **result
    })


if __name__ == '__main__':
    print("Loading model...")
    load_model()
    print("Server ready: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
