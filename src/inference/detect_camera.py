import os
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

from src.location_provider import format_location, get_current_location


CONFIDENCE_THRESHOLD = float(os.getenv("PLASTIC_CONF", "0.35"))
IOU_THRESHOLD = 0.5
MODEL_IMAGE_SIZE = int(os.getenv("PLASTIC_IMGSZ", "960"))
REQUIRED_CONFIRMATION_FRAMES = int(os.getenv("PLASTIC_CONFIRM_FRAMES", "2"))
LOCATION_REFRESH_SECONDS = float(os.getenv("LOCATION_REFRESH_SECONDS", "1"))


def open_camera(max_index=3):
    backends = (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY)
    for backend in backends:
        for index in range(max_index):
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                print(f"[INFO] Camera opened (index={index}, backend={backend})")
                return cap
            cap.release()
    return None


def main():
    project_root = Path(__file__).resolve().parents[2]
    model_path = project_root / "models" / "best_model.pt"

    if not model_path.exists():
        print("[ERROR] Model not found")
        return

    print("[INFO] Loading model...")
    model = YOLO(str(model_path))

    print(
        f"[INFO] Detection settings: conf={CONFIDENCE_THRESHOLD}, "
        f"imgsz={MODEL_IMAGE_SIZE}, confirm_frames={REQUIRED_CONFIRMATION_FRAMES}"
    )

    location = None
    last_location_refresh_time = 0
    consecutive_detection_frames = 0

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

        results = model(
            frame,
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            imgsz=MODEL_IMAGE_SIZE,
            verbose=False,
        )

        detected_count = 0
        max_confidence = 0
        result = results[0] if results else None
        if result is not None and result.boxes is not None:
            detected_count = len(result.boxes)
            if detected_count > 0:
                max_confidence = float(result.boxes.conf.max())

        if detected_count > 0:
            consecutive_detection_frames += 1
        else:
            consecutive_detection_frames = 0

        confirmed_detection = consecutive_detection_frames >= REQUIRED_CONFIRMATION_FRAMES

        annotated_frame = result.plot() if result is not None else frame

        if confirmed_detection:
            now = time.time()
            if now - last_location_refresh_time >= LOCATION_REFRESH_SECONDS:
                latest_location = get_current_location()
                last_location_refresh_time = now
                if latest_location:
                    location = latest_location
                    print(f"[INFO] Live location source: {location['source']}")
                elif location is None:
                    print("[WARN] Could not get an accurate location.")
                    print("[WARN] Open http://127.0.0.1:8765/location-page and allow location permission.")
                    print("[WARN] Approximate IP location is disabled because it can be hundreds of kilometers wrong.")

            print(
                f"[INFO] Plastic confirmed: {detected_count} object(s), "
                f"max_conf={max_confidence:.2f}, {format_location(location)}"
            )
            cv2.putText(
                annotated_frame,
                format_location(location),
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

        cv2.imshow("Plastic Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Camera closed.")


if __name__ == "__main__":
    main()
