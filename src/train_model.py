import shutil
import subprocess
import sys
from pathlib import Path
import torch
from ultralytics import YOLO


def main():
    # Project root
    project_root = Path(__file__).resolve().parent.parent

    build_dataset_script = project_root / "src" / "build_clean_dataset.py"
    data_yaml = project_root / "Dataset" / "robot_clean" / "data.yaml"
    models_dir = project_root / "models"
    runs_dir = project_root / "runs"

    if not data_yaml.exists():
        print("[INFO] Clean dataset not found. Building it now...")
        subprocess.run([sys.executable, str(build_dataset_script)], check=True)

    if not data_yaml.exists():
        print(f"[ERROR] Clean dataset not found: {data_yaml}")
        print("[ERROR] Run: python src/build_clean_dataset.py")
        return

    print(f"[INFO] Using dataset: {data_yaml}")

    existing_weights = models_dir / "best_model.pt"
    base_weights = existing_weights if existing_weights.exists() else project_root / "yolov8s.pt"

    print(f"[INFO] Loading base weights: {base_weights}")
    model = YOLO(str(base_weights))

    # Train model
    print("[INFO] Starting training...")
    has_cuda = torch.cuda.is_available()
    device = 0 if has_cuda else "cpu"
    epochs = 150 if has_cuda else 30
    image_size = 768 if has_cuda else 640
    batch_size = 8 if has_cuda else 4
    print(f"[INFO] Training device: {device}")
    model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=image_size,
        project=str(runs_dir),
        name="plastic_model_robot",
        exist_ok=True,
        workers=4,
        batch=batch_size,
        patience=35,
        optimizer="AdamW",
        lr0=0.0005 if existing_weights.exists() else 0.001,
        cos_lr=True,
        close_mosaic=15,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.35,
        degrees=5,
        translate=0.1,
        scale=0.4,
        fliplr=0.5,
        mosaic=0.7,
        mixup=0.05,
        cache=True,
        device=device,
    )

    print("[INFO] Training completed.")

    best_weights_path = runs_dir / "plastic_model_robot" / "weights" / "best.pt"

    target_weights_path = models_dir / "best_model.pt"

    if not best_weights_path.exists():
        print("[WARNING] Default path not found. Searching...")

        found_models = list(runs_dir.rglob("best.pt"))

        if found_models:
            best_weights_path = found_models[0]
            print(f"[INFO] Found best.pt at: {best_weights_path}")
        else:
            print("[ERROR] No best.pt found.")
            return

    models_dir.mkdir(exist_ok=True)
    shutil.copy(best_weights_path, target_weights_path)

    print(f"[SUCCESS] Model saved at: {target_weights_path}")


if __name__ == "__main__":
    main()
