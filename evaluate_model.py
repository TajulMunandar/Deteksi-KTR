"""
Script untuk evaluasi model YOLO
Menampilkan akurasi (mAP dalam %), confusion matrix, dan label kelas
"""

import os
import numpy as np
from ultralytics import YOLO

def evaluate_model():
    # Path ke model terbaik
    model_path = os.path.join("runs", "train", "exp", "weights", "best.pt")

    # Cek apakah model ada
    if not os.path.exists(model_path):
        print(f"Model tidak ditemukan di: {model_path}")
        return

    # Load model
    print("Loading model...")
    model = YOLO(model_path)

    # Tampilkan informasi model
    print("\n=== INFORMASI MODEL ===")
    print(f"Model path: {model_path}")
    print(f"Jumlah kelas: {len(model.names)}")
    print("Label kelas:")
    for idx, name in model.names.items():
        print(f"  {idx}: {name}")

    # Baca hasil training dari results.csv
    results_csv = os.path.join("runs", "train", "exp", "results.csv")
    if os.path.exists(results_csv):
        print("\n=== RIWAYAT TRAINING ===")
        with open(results_csv, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                header = lines[0].strip()
                last_line = lines[-1].strip()
                print(f"Header: {header}")
                print(f"Epoch terakhir: {last_line}")
                # Parse epoch dan mAP
                parts = last_line.split(',')
                if len(parts) >= 8:
                    epoch = parts[0]
                    map50 = float(parts[7]) * 100
                    map5095 = float(parts[8]) * 100 if len(parts) > 8 else 0
                    print(f"Epoch ke-{epoch}: mAP50 = {map50:.2f}%, mAP50-95 = {map5095:.2f}%")
                    print("Angka akurasi berasal dari hasil training di results.csv")

    # Jalankan validasi
    print("\n=== MENJALANKAN VALIDASI ===")
    print("Mengevaluasi model pada dataset validasi...")

    # Jalankan validasi dengan confusion matrix
    results = model.val(
        data='data.yaml',
        split='val',
        conf=0.25,  # confidence threshold
        iou=0.45,   # IoU threshold
        imgsz=640,  # image size
        save_json=True,  # simpan hasil dalam format JSON
        save_conf=True,  # simpan confidence
        plots=True,      # generate plots termasuk confusion matrix
        verbose=True     # tampilkan detail
    )

    # Tampilkan hasil evaluasi
    print("\n=== HASIL EVALUASI ===")
    map50 = results.results_dict.get('metrics/mAP50(B)', 0) * 100
    map5095 = results.results_dict.get('metrics/mAP50-95(B)', 0) * 100
    precision = results.results_dict.get('metrics/precision(B)', 0) * 100
    recall = results.results_dict.get('metrics/recall(B)', 0) * 100

    print("=== METRIK AKURASI ===")
    print(".2f")
    print(".2f")
    print(".2f")
    print(".2f")
    print(".2f")
    # Hitung akurasi dari confusion matrix jika tersedia
    if hasattr(results, 'confusion_matrix') and results.confusion_matrix is not None:
        cm = results.confusion_matrix.matrix
        if cm.sum() > 0:
            accuracy_cm = np.diag(cm).sum() / cm.sum() * 100
            print("Confusion Matrix:")
            print(cm)
        else:
            print("Confusion Matrix tidak tersedia atau kosong")

    # Tampilkan per-class metrics jika ada
    if hasattr(results, 'ap_class_index') and results.ap_class_index is not None:
        print("\n=== METRIK PER KELAS ===")
        for i, ap in enumerate(results.ap_class_index):
            class_name = model.names.get(i, f"Class {i}")
            print(".2f")

    print("\n=== FILE YANG DIHASILKAN ===")
    print("- Confusion matrix tersimpan sebagai: runs/train/exp/confusion_matrix.png")
    print("- Confusion matrix normalized: runs/train/exp/confusion_matrix_normalized.png")
    print("- Kurva Precision-Recall: runs/train/exp/BoxPR_curve.png")
    print("- Kurva F1: runs/train/exp/BoxF1_curve.png")
    print("- Kurva Precision: runs/train/exp/BoxP_curve.png")
    print("- Kurva Recall: runs/train/exp/BoxR_curve.png")
    print("- Hasil validasi batch: runs/train/exp/val_batch*.jpg")

    print("\nEvaluasi selesai!")

if __name__ == "__main__":
    evaluate_model()