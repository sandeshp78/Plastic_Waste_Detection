import os
import sys
import subprocess
from pathlib import Path

def main():
    # 1. Define paths
    project_root = Path(__file__).resolve().parent
    model_path = project_root / "models" / "best_model.pt"
    train_script = project_root / "src" / "train_model.py"
    detect_script = project_root / "src" / "inference" / "detect_camera.py"

    print("==========================================")
    print("   Plastic Waste Detection System v1.0    ")
    print("==========================================\n")

    # Add project root to PYTHONPATH so sub-scripts can import 'utils'
    env = os.environ.copy()
    current_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + current_path if current_path else "")

    # 2. Check if model exists
    if not model_path.exists():
        print(f"[INFO] Model not found at: {model_path}")
        print("[INFO] Starting automatic training process...")
        print("------------------------------------------")
        
        try:
            # Run training script
            # Passing sys.executable ensures we use the same python interpreter
            subprocess.run([sys.executable, str(train_script)], check=True, env=env)
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Training failed with exit code {e.returncode}.")
            print("Please check the error messages above.")
            sys.exit(e.returncode)
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred during training: {e}")
            sys.exit(1)
            
        print("\n[INFO] Training completed successfully.")
        
        # Verify model was actually created
        if not model_path.exists():
            print(f"[ERROR] Training finished, but model is still missing: {model_path}")
            sys.exit(1)
    else:
        print(f"[INFO] Found trained model at: {model_path}")

    # 3. Run Inference
    print("\n[INFO] Starting Real-Time Detection System...")
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

if __name__ == "__main__":
    main()
