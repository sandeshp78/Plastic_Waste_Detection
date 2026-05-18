import os
import sys
import subprocess
import threading
from pathlib import Path

from src.phone_location_server import create_location_server


def start_location_server():
    try:
        server = create_location_server()
    except OSError as error:
        print(f"[WARN] Location server could not start: {error}")
        print("[WARN] If it is already running, this is okay.")
        return None

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print("[INFO] Location permission page: http://127.0.0.1:8765/location-page")
    return server


def main():
    project_root = Path(__file__).resolve().parent
    model_path = project_root / "models" / "best_model.pt"
    train_script = project_root / "src" / "train_model.py"
    detect_script = project_root / "src" / "inference" / "detect_camera.py"

    print("==========================================")
    print("   Plastic Waste Detection System v1.0    ")
    print("==========================================\n")
    location_server = start_location_server()

    env = os.environ.copy()
    current_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + current_path if current_path else "")

    if not model_path.exists():
        print(f"[INFO] Model not found at: {model_path}")
        print("[INFO] Starting automatic training process...")
        print("------------------------------------------")

        try:
            subprocess.run([sys.executable, str(train_script)], check=True, env=env)
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Training failed with exit code {e.returncode}.")
            print("Please check the error messages above.")
            sys.exit(e.returncode)
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred during training: {e}")
            sys.exit(1)

        print("\n[INFO] Training completed successfully.")

        if not model_path.exists():
            print(f"[ERROR] Training finished, but model is still missing: {model_path}")
            sys.exit(1)
    else:
        print(f"[INFO] Found trained model at: {model_path}")

    print("\n[INFO] Starting Real-Time Detection System...")
    print("[INFO] Open the location page above in your laptop browser and allow location permission.")
    print("------------------------------------------")

    try:
        subprocess.run([sys.executable, str(detect_script)], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Detection system crashed with exit code {e.returncode}.")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if location_server is not None:
            location_server.shutdown()
            location_server.server_close()


if __name__ == "__main__":
    main()
