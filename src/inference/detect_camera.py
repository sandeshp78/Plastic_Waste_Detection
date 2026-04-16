import cv2
import time
from pathlib import Path
from ultralytics import YOLO


def open_camera():
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        for index in range(3):
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                print(f"[INFO] Camera opened (index={index}, backend={backend})")
                return cap
    return None


def main():
    project_root = Path(__file__).resolve().parents[2]
    model_path = project_root / "models" / "best_model.pt"

    if not model_path.exists():
        print("[ERROR] Model not found")
        return

    print("[INFO] Loading model...")
    model = YOLO(str(model_path))

    print("[DEBUG] Classes:", model.names)

    cap = open_camera()
    if cap is None:
        print("[ERROR] No camera detected.")
        return

    time.sleep(2)
    print("[INFO] Press 'q' to exit")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("[ERROR] Frame failed")
            break

        # ✅ Better resolution for YOLO
        frame = cv2.resize(frame, (640, 640))

        # 🔥 IMPORTANT: Low confidence
        results = model(frame, conf=0.15, verbose=False)

        # 🔍 Debug: print detections
        if results and results[0].boxes is not None:
            print(f"[DEBUG] Detected: {len(results[0].boxes)} objects")

        # ✅ Use YOLO built-in drawing
        annotated_frame = results[0].plot()

        cv2.imshow("Plastic Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Camera closed.")


if __name__ == "__main__":
    main()