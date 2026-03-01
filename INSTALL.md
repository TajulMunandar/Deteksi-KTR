# Citra KTR Map - Installation Guide
## YOLOv11 Smoking Detection System with Virtual Environment (venv)

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Installation Steps](#installation-steps)
4. [How to Run](#how-to-run)
5. [Training the Model](#training-the-model)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| RAM | 4GB | 8GB+ |
| Disk Space | 5GB | 10GB+ |
| GPU | Optional | NVIDIA with 4GB+ VRAM |

### Required Software
- **Python 3.8 or higher** - Download from https://www.python.org/
- **Windows 10/11** (this guide is for Windows)

---

## Project Structure

```
Citra KTR Map/
├── requirements.txt      # Python dependencies
├── INSTALL.md           # This file
├── README.md            # Project overview
├── run.bat              # Quick start script
├── setup_venv.bat       # Virtual environment setup
├── server.py            # Flask API server
├── train.py             # YOLOv11 training script
├── data.yaml            # YOLO dataset configuration
├── index.html           # Web interface
├── style.css            # Styling
├── script.js            # Frontend JavaScript
├── yolo11n.pt           # Pre-trained YOLOv11 model
├── train/               # Training dataset
│   ├── images/          # Training images
│   └── labels/          # YOLO format labels
├── val/                 # Validation dataset (auto-created)
├── runs/                # Training outputs
│   └── train/exp/weights/
│       ├── best.pt      # Trained model (best)
│       └── last.pt      # Trained model (last checkpoint)
└── uploads/             # Temporary upload folder
```

---

## Installation Steps

### Method 1: Using Automated Script (Recommended)

1. **Extract/Copy the project** to your desired location

2. **Run the setup script** by double-clicking `setup_venv.bat`

3. **Run the application** by double-clicking `run.bat`

---

### Method 2: Manual Installation

#### Step 1: Create Virtual Environment

Open Command Prompt (cmd) in the project folder:

```cmd
cd "d:\kerja\tesis\Citra KTR Map"
```

Create virtual environment:

```cmd
python -m venv venv
```

#### Step 2: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your command prompt.

#### Step 3: Install Dependencies

```cmd
pip install -r requirements.txt
```

> **Note:** If you have NVIDIA GPU with CUDA, torch will automatically use it. For CPU-only systems, installation will take longer.

#### Step 4: Verify Installation

```cmd
python -c "import ultralytics; import flask; print('OK')"
```

---

## How to Run

### Option 1: Using run.bat (Easiest)

1. Make sure you've completed the installation steps
2. Double-click `run.bat`
3. The server will start and open in your browser at `http://localhost:5000`

### Option 2: Using Command Line

1. **Activate the virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

2. **Start the server:**
   ```cmd
   python server.py
   ```

3. **Open in browser:**
   Navigate to `http://localhost:5000`

### Option 3: Using Python Directly

```cmd
venv\Scripts\python.exe server.py
```

---

## Training the Model

### Quick Training (Default Settings)

```cmd
venv\Scripts\python.exe train.py
```

### Custom Training

```cmd
venv\Scripts\python.exe train.py --epochs 50 --batch 8 --model yolo11n
```

### Training Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--epochs` | 15 | Number of training epochs |
| `--batch` | 16 | Batch size |
| `--model` | yolo11n | Model variant (yolo11n, yolo11s, yolo11m) |
| `--imgsz` | 640 | Image size |
| `--data` | data.yaml | Dataset config file |

### Training with GPU

If you have NVIDIA GPU, training will automatically use it. To force CPU:

```cmd
venv\Scripts\python.exe train.py --epochs 30
```

---

## API Endpoints

The server provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/health` | GET | Health check |
| `/predict` | POST | Image prediction |
| `/classes` | GET | List detection classes |

### Example: Using Prediction API

```cmd
curl -X POST -F "file=@test.jpg" http://localhost:5000/predict
```

---

## Troubleshooting

### Issue: "python is not recognized"

**Solution:** Add Python to PATH or use full path:
```cmd
"C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe"
```

### Issue: "No module named 'ultralytics'"

**Solution:** Activate venv and reinstall:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Port 5000 is already in use"

**Solution:** Change port in `server.py` line 162:
```python
app.run(host='0.0.0.0', port=5001, threaded=True)
```

### Issue: Out of Memory during training

**Solution:** Reduce batch size:
```cmd
venv\Scripts\python.exe train.py --batch 4
```

### Issue: Model not found

**Solution:** Train the model first:
```cmd
venv\Scripts\python.exe train.py
```

### Issue: "DLL load failed" on Windows

**Solution:** Install Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Deactivating Virtual Environment

When done, you can deactivate the virtual environment:

```cmd
deactivate
```

---

## Quick Reference Commands

| Action | Command |
|--------|---------|
| Create venv | `python -m venv venv` |
| Activate venv | `venv\Scripts\activate` |
| Install deps | `pip install -r requirements.txt` |
| Run server | `python server.py` |
| Train model | `python train.py` |
| Deactivate | `deactivate` |

---

## Additional Information

### Detection Classes
- **Rokok** - Cigarette
- **Merokok** - Smoking (person)
- **Asbak** - Ashtray

### Compliance Rules
- **Patuh (Green)** - No smoking detected
- **Tidak Patuh Ringan (Yellow)** - Cigarette detected but no person smoking
- **Tidak Patuh Berat (Red)** - Person smoking detected

### Model Files
After training, models are saved in:
- `runs/train/exp/weights/best.pt` - Best model
- `runs/train/exp/weights/last.pt` - Last checkpoint

---

**For more details, see README.md**
