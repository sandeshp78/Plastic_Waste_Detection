# Plastic Waste Detection System v1.0

## Overview
The Plastic Waste Detection System is an end-to-end computer vision project designed to detect plastic waste in water bodies using the YOLOv8 object detection model. It provides capabilities for both training a custom model and running real-time inferences on live camera feeds.

The system is robust and automated: if a trained model is missing, it will automatically initiate the training phase using your dataset before preceding to live inference. 

## Features
- **Automated Workflow**: Smart detection of existing models; automatically runs training if no model is found.
- **YOLOv8 Powered**: Uses state-of-the-art YOLOv8 architecture for fast and precise object detection.
- **Real-Time Inference**: Processes live video feeds from a webcam to identify plastic anomalies.
- **Auto Data Prep**: Splits datasets into Training/Validation sets and generates YAML configurations automatically.
- **Pseudo-GPS tracking**: Computes and logs coordinates based on bounding boxes on the screen frame. 

## Project Architecture
The system consists of three main components:
1. `main.py`: The master script setting up the project environment and orchestrating the Train/Inference logic.
2. `src/train_model.py`: Automates the processing of the dataset, training the YOLO model, and exporting `models/best_model.pt`.
3. `src/inference/detect_camera.py`: Captures webcam feeds and performs real-time detection, filtering detections with a >50% confidence threshold.

## File Structure
```
├── Dataset/                   # Directory containing raw images and labels
├── models/                    # Directory where trained models (best_model.pt) are saved
├── runs/                      # Training metrics output (Loss, mAP, Precision, Recall)
├── src/
│   ├── train_model.py         # Script to train the model
│   └── inference/
│       └── detect_camera.py   # Script for real-time live detection
├── main.py                    # Master execution script
├── requirements.txt           # Project dependencies
├── How_To_Run.txt             # Quick execution commands guide
└── system_workflow.md         # Detailed Dataflow & System Architecture diagram
```

## Setup & Installation
1. **Create a virtual environment:**
   ```bash
   python -m venv myenv
   ```
2. **Activate the virtual environment:**
   - Windows:
     ```bash
     myenv\Scripts\Activate
     ```
   - Linux/Mac:
     ```bash
     source myenv/bin/activate
     ```
3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Requirements
The core dependencies used by this project:
- ultralytics >= 8.3.0
- torch & torchvision
- opencv-python >= 4.8.0
- numpy >= 1.23
- matplotlib >= 3.7
- pyyaml >= 6.0
- tqdm >= 4.66

## How to Run

To run the whole system (triggers training if no model is present, then jumps to inference):
```bash
python main.py
```

To strictly run the inference script directly:
```bash
python -m src.inference.detect_camera
```

## System Workflow Description
- Start the application by invoking `main.py`.
- The system checks for the presence of `models/best_model.pt`.
- If missing, the model will train using the labeled data in `Dataset/`, dividing the data into an 80/20 train/validation split. Upon completion, the model is saved to `models/best_model.pt`.
- If found (or newly trained), Real-Time detection using OpenCV initializes on your default camera feed. Detected plastic items are marked with bounding boxes and "Pseudo-GPS" details in the console.

---
*Created as part of the Plastic Waste Detection System project.*
