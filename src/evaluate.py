import os
from pathlib import Path
from ultralytics import YOLO

def main():
    # Project root (parent of src/)
    project_root = Path(__file__).resolve().parent.parent
    model_path = project_root / "models" / "best_model.pt"
    data_yaml = project_root / "Dataset" / "final" / "data.yaml"
    runs_dir = project_root / "runs"

    if not model_path.exists():
        print(f"[ERROR] Could not find the trained model at {model_path}.")
        print("Please execute train_model.py first to generate the weights.")
        return

    if not data_yaml.exists():
        print(f"[ERROR] Cannot find {data_yaml}. Make sure your dataset is prepared.")
        return

    print(f"\n[INFO] Loading custom plastic detection model from {model_path}...")
    model = YOLO(str(model_path))

    print("\n[INFO] Evaluating accuracy against the validation dataset...")

    # The 'val' routine automatically calculates precision, recall, and mAP!
    metrics = model.val(
        data=str(data_yaml),
        split="val",
        project=str(runs_dir),
        name="plastic_eval",
        exist_ok=True
    )

    print("\n===========================================")
    print("          EVALUATION RESULTS               ")
    print("===========================================")
    # Format and present the technical metrics
    print(f"mAP50-95 (Mean Average Precision) : {metrics.box.map:.4f}")
    print(f"mAP50                             : {metrics.box.map50:.4f}")
    print(f"Precision                         : {metrics.box.mp:.4f}")
    print(f"Recall                            : {metrics.box.mr:.4f}")
    print("===========================================")

    print(f"\n[INFO] A detailed evaluation breakdown has been saved in '{runs_dir / 'plastic_eval'}'.")

if __name__ == "__main__":
    main()
