import shutil
from pathlib import Path
from ultralytics import YOLO


def main():
    # Project root
    project_root = Path(__file__).resolve().parent.parent

    data_yaml = project_root / "Dataset" / "final" / "data.yaml"
    models_dir = project_root / "models"
    runs_dir = project_root / "runs"

    if not data_yaml.exists():
        print(f"[ERROR] Dataset not found: {data_yaml}")
        return

    print(f"[INFO] Using dataset: {data_yaml}")

    # Load base model
    print("[INFO] Loading YOLOv8n...")
    model = YOLO("yolov8s.pt")

    # Train model
    print("[INFO] Starting training...")
    model.train(
        data=str(data_yaml),
        epochs=100,
        imgsz=640,
        project=str(runs_dir),
        name="plastic_model",
        exist_ok=True,
        workers=4,
        batch=8,
        patience=20,
        device=0
    )

    print("[INFO] Training completed.")

    best_weights_path = runs_dir / "detect" / "weights" / "best.pt"

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