"""
YOLOv11 Training Script - Citra KTR Map
=======================================
Optimized training script for smoking detection.
GPU/CPU auto-fallback supported.
"""

import os
import shutil
import random
import argparse
import torch
from pathlib import Path
from ultralytics import YOLO


def get_device():
    """Auto-detect and return best available device."""
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB)")
        return "0"
    print("Using CPU")
    return "cpu"


def get_optimal_workers():
    """Detect optimal number of dataloader workers."""
    cpu_count = os.cpu_count() or 1
    # Leave 2 cores free for main process
    return max(1, min(cpu_count - 2, 8))


def prepare_dataset(val_split: float = 0.15):
    """Create validation split from training data."""
    train_img_dir = Path("train/images")
    train_lbl_dir = Path("train/labels")
    val_img_dir = Path("val/images")
    val_lbl_dir = Path("val/labels")
    
    # Get all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    images = [f for f in train_img_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    if not images:
        print("No images found in train/images")
        return False
    
    # Shuffle and split
    random.seed(42)
    random.shuffle(images)
    n_val = int(len(images) * val_split)
    val_images = images[:n_val]
    
    print(f"Dataset: {len(images)} train, {len(val_images)} val")
    
    # Create val directory only if not exists or empty
    val_images_exist = list(val_img_dir.glob("*")) if val_img_dir.exists() else []
    
    if not val_images_exist:
        val_img_dir.mkdir(parents=True, exist_ok=True)
        val_lbl_dir.mkdir(parents=True, exist_ok=True)
        
        for img in val_images:
            # Copy image
            shutil.copy2(img, val_img_dir / img.name)
            # Copy label if exists
            lbl = train_lbl_dir / (img.stem + '.txt')
            if lbl.exists():
                shutil.copy2(lbl, val_lbl_dir / lbl.name)
        print(f"Created val/ with {len(val_images)} images")
    else:
        print(f"Using existing val/ with {len(val_images_exist)} images")
    
    return True


def train(
    model: str = "yolo11n",
    epochs: int = 30,
    imgsz: int = 640,
    batch: int = 16,
    data: str = "data.yaml",
    workers: int = None,
    patience: int = 10,
    val_split: float = 0.15,
    project: str = None,
    name: str = "exp",
):
    """
    Train YOLOv11 model with optimized settings.
    """
    device = get_device()
    workers = workers or get_optimal_workers()
    
    # Default project to current directory
    if project is None:
        project = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", "train")
    
    print(f"\n{'='*50}")
    print(f"Training YOLOv11 ({model})")
    print(f"{'='*50}")
    print(f"Epochs: {epochs} | ImgSize: {imgsz} | Batch: {batch}")
    print(f"Workers: {workers} | Device: {device}")
    print(f"Data: {data} | ValSplit: {val_split*100:.0f}%")
    print(f"{'='*50}\n")
    
    # Prepare validation split (only copies files once)
    prepare_dataset(val_split)
    
    # Initialize model
    model = YOLO(f"{model}.pt")
    
    # Train with optimized settings
    results = model.train(
        data=data,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        workers=workers,
        
        # Optimizer settings
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        
        # Training schedule
        warmup_epochs=3.0,
        
        # Loss weights
        box=7.5,
        cls=0.5,
        dfl=1.5,
        
        # Performance
        amp=True,
        cache=False,
        patience=patience,
        plots=True,
        verbose=True,
        
        # Output
        project=project,
        name=name,
    )
    
    print(f"\nTraining complete!")
    if results and hasattr(results, 'results_dict'):
        print(f"Results: {results.results_dict}")
    
    return results


def evaluate(model_path: str = "runs/train/exp/weights/best.pt"):
    """Evaluate trained model."""
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return None
    
    device = get_device()
    model = YOLO(model_path)
    
    metrics = model.val(device=device)
    print(f"\nmAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    
    return metrics


def export_model(model_path: str = "runs/train/exp/weights/best.pt", format: str = "onnx"):
    """Export model to specified format."""
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return None
    
    model = YOLO(model_path)
    export_path = model.export(format=format)
    print(f"Exported: {export_path}")
    return export_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv11")
    parser.add_argument("--model", type=str, default="yolo11n", 
                        choices=["yolo11n", "yolo11s", "yolo11m", "yolo11l"],
                        help="Model variant")
    parser.add_argument("--epochs", type=int, default=15, help="Epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--data", type=str, default="data.yaml", help="Data YAML")
    parser.add_argument("--workers", type=int, default=None, help="DataLoader workers")
    parser.add_argument("--val-split", type=float, default=0.15, help="Val split ratio")
    parser.add_argument("--project", type=str, default=None, help="Output dir")
    parser.add_argument("--name", type=str, default="exp", help="Experiment name")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate after training")
    parser.add_argument("--export", type=str, default=None, help="Export format")
    
    args = parser.parse_args()
    
    # Train
    results = train(
        model=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        data=args.data,
        workers=args.workers,
        val_split=args.val_split,
        project=args.project,
        name=args.name,
    )
    
    # Evaluate
    if args.evaluate:
        evaluate()
    
    # Export
    if args.export:
        export_model(format=args.export)
