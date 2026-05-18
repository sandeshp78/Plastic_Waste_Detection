# Plastic Waste Detection Robot

Real-time plastic waste detection using a YOLOv8 model, OpenCV camera input, and optional live location capture from the laptop browser or GPS environment variables.

## Features

- Detects plastic waste from a live camera feed.
- Uses `models/best_model.pt` as the production model.
- Automatically trains a model when `models/best_model.pt` is missing.
- Builds a clean YOLO dataset from the available raw datasets when needed.
- Shows detected objects with bounding boxes in an OpenCV window.
- Prints confirmed detections with latitude and longitude when location is available.

## Project Structure

```text
.
|-- Dataset/                         # Source and prepared YOLO datasets
|-- Dataset2/                        # Additional raw images, masks, and labels
|-- models/
|   `-- best_model.pt                # Production model used for inference
|-- src/
|   |-- build_clean_dataset.py       # Builds Dataset/robot_clean
|   |-- evaluate.py                  # Evaluates models/best_model.pt
|   |-- location_provider.py         # Reads manual, browser, or Windows location
|   |-- phone_location_server.py     # Local browser location server
|   |-- train_model.py               # Trains and exports best_model.pt
|   `-- inference/
|       `-- detect_camera.py         # Live camera detection
|-- main.py                          # Main application entry point
|-- requirements.txt                 # Python dependencies
|-- How_To_Run.txt                   # Short run commands
`-- system_workflow.md               # Workflow notes
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv myenv
myenv\Scripts\Activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## How To Run

Run the complete application:

```powershell
python main.py
```

`main.py` starts the local location server, checks for `models/best_model.pt`, trains if the model is missing, and then starts live camera detection.

When the project starts, the terminal prints:

```text
Location permission page: http://127.0.0.1:8765/location-page
```

Open this URL on the laptop browser:

```text
http://127.0.0.1:8765/location-page
```

Click `Allow Location` on the page. When the browser asks for permission, click `Allow`. The project will then use that laptop browser location when plastic is detected.

Important: open the location page on the laptop browser, not on the phone.

Run only live detection:

```powershell
python -m src.inference.detect_camera
```

Run only training:

```powershell
python -m src.train_model
```

Evaluate the current model:

```powershell
python -m src.evaluate
```

## Location Options

The detector checks location sources in this order:

1. Manual environment variables:

   ```powershell
   $env:GPS_LATITUDE="16.7147381"
   $env:GPS_LONGITUDE="74.4357617"
   python main.py
   ```

2. Browser location from the local page:

   ```text
   http://127.0.0.1:8765/location-page
   ```

   Run `python main.py`, open this URL on the laptop browser, click `Allow Location`, and approve the browser permission prompt.

3. Windows Location Services, when available.

Approximate IP location is disabled by default because it can be very inaccurate. To allow it:

```powershell
$env:ALLOW_APPROX_IP_LOCATION="1"
python main.py
```

## Runtime Settings

You can tune detection without editing code:

```powershell
$env:PLASTIC_CONF="0.35"
$env:PLASTIC_IMGSZ="960"
$env:PLASTIC_CONFIRM_FRAMES="2"
$env:LOCATION_REFRESH_SECONDS="1"
python main.py
```

## Notes

- Press `q` in the camera window to stop detection.
- Keep `models/best_model.pt` for normal inference.
- `runs/` and YOLO `.cache` files are generated outputs and can be recreated.
