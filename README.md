# 🤖 Multipurpose Robot

A modular, Raspberry Pi-powered robot with swappable features — voice assistant, face-recognition attendance, real-time object detection, autonomous line following, and manual remote control. Each feature runs as a plug-in managed by a central Flask controller that hot-swaps Arduino sketches at runtime.

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
  - [MAYA — Voice Assistant](#1--maya--voice-assistant)
  - [Attendance System](#2--attendance-system)
  - [Object Detection](#3--object-detection-yolov8)
  - [Line Following](#4--line-following)
  - [Manual Control](#5--manual-control)
- [Hardware Requirements](#hardware-requirements)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Notes](#notes)

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│              main_controller.py                  │
│         Flask Server (port 5001)                 │
│  ┌────────────────┐  ┌────────────────────────┐  │
│  │MotorController │  │SketchUploader          │  │
│  └──────┬─────────┘  └──────────┬─────────────┘  │
│         │ Serial /dev/ttyACM0   │ arduino-cli    │
│         ▼                       ▼                │
│  ┌──────────────────────────────────────┐        │
│  │         FeatureManager               │        │
│  │  ┌──────┐┌───────┐┌─────┐┌────────┐  │        │
│  │  │ MAYA ││Attend ││ObjDt││LineFol │  │        │
│  │  └──────┘└───────┘└─────┘└────────┘  │        │
│  └──────────────────────────────────────┘        │
└──────────────────────────────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  Arduino Uno │
              │  (Motors/IR) │
              └──────────────┘
```

The **FeatureManager** ensures only one feature runs at a time. When a new feature is requested via the REST API, it:
1. Stops the current feature gracefully
2. Uploads the matching Arduino sketch (`arduino_sketches/<feature>/`)
3. Starts the new feature's Python processor

---

## Features

### 1. 🗣️ MAYA — Voice Assistant

A hands-free, Indian-personality voice assistant that listens, speaks, and controls the robot.

| Capability | Details |
|---|---|
| **Wake Words** | "Maya", "Hey Maya", "Maya ji" |
| **Speech Recognition** | Google Speech Recognition via `speech_recognition` library |
| **Voice Output** | Google TTS with Indian English accent (`en`, `co.in`) via `gTTS` + `pygame` |
| **Movement Control** | "Move forward", "turn left", "go back", "stop" — sends serial commands to Arduino |
| **AI Queries** | Powered by **Google Gemini 1.5 Flash** — ask anything ("Maya, explain quantum computing") |
| **Utilities** | Current time, date, random jokes (`pyjokes`) |
| **Audio Input** | Optimized for TWS / Bluetooth headphones via PulseAudio |

**Example commands:**
```
"Maya, move forward"
"Maya, what time is it?"
"Maya, tell me a joke"
"Maya, what is machine learning?"
```

### 2. 📸 Attendance System

Face-recognition based automatic attendance using **dlib** and Pi Camera.

| Component | Purpose |
|---|---|
| `face.py` / `get_faces_from_camera_tkinter.py` | Register new faces via Tkinter GUI — captures and stores face images |
| `features_extraction_to_csv.py` | Extracts 128D face descriptors using dlib ResNet model → `features_all.csv` |
| `attend.py` / `attendance_taker.py` | Real-time face recognition — matches faces against stored descriptors |
| `attendance.db` | SQLite database storing name, time, and date (unique per person per day) |
| `app.py` | Flask web interface to view attendance records |

**How it works:**
1. **Register faces** → GUI captures 5+ images per person
2. **Extract features** → generates 128D embeddings via dlib ResNet50
3. **Run attendance** → Pi Camera detects and recognizes faces in real-time, logs to SQLite
4. **View records** → open web dashboard

**Models used:**
- `shape_predictor_68_face_landmarks.dat` — dlib 68-point facial landmark predictor
- `dlib_face_recognition_resnet_model_v1.dat` — dlib ResNet face encoder (128D output)

### 3. 🎯 Object Detection (YOLOv8)

Real-time object detection using **YOLOv8s** (TFLite float16) on Raspberry Pi with Pi Camera.

| Detail | Value |
|---|---|
| **Model** | YOLOv8s (float16 TFLite) |
| **Input Size** | 640 x 640 |
| **Classes** | 80 COCO classes (person, car, dog, chair, etc.) |
| **Inference** | TFLite Runtime (optimized for ARM / RPi) |
| **Output** | Live MJPEG video stream with bounding boxes |
| **Stream URL** | `http://<pi-ip>:5000/video_feed` |

**Pipeline:** Capture frame → Resize to 640x640 → TFLite inference → NMS post-processing → Draw bounding boxes → Stream via Flask MJPEG

### 4. 📏 Line Following

Autonomous line-following using IR sensors connected to Arduino.

| Detail | Value |
|---|---|
| **Sensors** | IR sensor array (connected to Arduino analog/digital pins) |
| **Logic** | Runs entirely on Arduino (`arduino_sketches/line_following/`) |
| **Python side** | Monitoring thread keeps the feature alive; all real-time control is on the Arduino |

The Arduino sketch reads IR sensors and adjusts motor speeds to keep the robot centered on a line. The Python processor simply manages the start/stop lifecycle.

### 5. 🎮 Manual Control

Direct motor control via REST API — designed for mobile app or web dashboard integration.

| Command | Serial Code | Action |
|---|---|---|
| Forward | `F` | Both motors forward |
| Backward | `B` | Both motors reverse |
| Left | `L` | Differential turn left |
| Right | `R` | Differential turn right |
| Stop | `S` | All motors stop |

Manual control is the **default mode** — it initializes on startup and resumes whenever another feature is stopped.

---

## Hardware Requirements

| Component | Purpose |
|---|---|
| Raspberry Pi 4B | Main compute board |
| Arduino Uno | Motor driver + sensor interface |
| Pi Camera Module | Vision (attendance, object detection) |
| L298N / Motor Driver | DC motor control |
| 2x DC Motors + Wheels | Locomotion |
| IR Sensor Array | Line following |
| USB Cable (Pi to Arduino) | Serial communication (`/dev/ttyACM0`, 9600 baud) |
| TWS / Bluetooth Headphones | Audio I/O for MAYA (mic + speaker) |
| Power Supply / Battery Pack | 5V for Pi, 7-12V for motors |

---

## Project Structure

```
Robot/
├── main_controller.py          # Flask server + FeatureManager (entry point)
├── start_robot.sh              # One-click startup script
├── requirements.txt            # Python dependencies
├── .gitignore
│
├── features/
│   ├── maya/                   # Voice assistant
│   │   ├── maya.py             # MAYAAssistant class (speech, AI, movement)
│   │   ├── config.py           # API keys, mic settings, voice config
│   │   ├── movement_helper.py  # HTTP fallback for motor commands
│   │   └── processor.py        # FeatureManager integration wrapper
│   │
│   ├── attend/                 # Face-recognition attendance
│   │   ├── attend.py           # Real-time face recognizer (Pi Camera)
│   │   ├── attendance_taker.py # Alternate attendance script
│   │   ├── face.py             # Face registration GUI (Tkinter)
│   │   ├── get_faces_from_camera_tkinter.py
│   │   ├── features_extraction_to_csv.py  # Extract 128D face features
│   │   ├── app.py              # Web dashboard for records
│   │   └── processor.py        # FeatureManager integration wrapper
│   │
│   ├── object_detection/       # YOLOv8 real-time detection
│   │   ├── object_detection.py # TFLite inference + MJPEG stream
│   │   └── processor.py        # FeatureManager integration wrapper
│   │
│   ├── line_following/         # IR-based line follower
│   │   └── processor.py        # Arduino-driven, Python monitors lifecycle
│   │
│   └── manual_control/         # Direct motor commands via API
│       └── processor.py        # Maps API commands to serial codes
│
├── hardware/
│   ├── motors.py               # MotorController (serial to Arduino)
│   └── sketch_uploader.py      # arduino-cli compile + upload utility
│
├── arduino_sketches/
│   ├── manual_control/         # Default motor control sketch
│   ├── maya/                   # MAYA-specific sketch
│   ├── attend/                 # Attendance feature sketch
│   ├── object_detection/       # Object detection sketch
│   └── line_following/         # Line follower sketch (IR + motors)
│
└── models/
    └── yolov8s_float16.tflite  # YOLOv8s model (not tracked in git)
```

---

## Setup & Installation

### Prerequisites
- Raspberry Pi 4B with Raspberry Pi OS
- Arduino Uno connected via USB
- Pi Camera module enabled
- `arduino-cli` installed and configured
- Python 3.11+

### Installation

```bash
# Clone the repository
git clone https://github.com/masteranany23/multipurpose-robot.git
cd multipurpose-robot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **MAYA (Voice Assistant):** Edit `features/maya/config.py`
   - Set `GEMINI_API_KEY` for AI queries
   - Set `MICROPHONE_DEVICE_INDEX` for your audio device (use `pulse` for Bluetooth)

2. **Attendance:** Download dlib models into `features/attend/data/data_dlib/`
   - `shape_predictor_68_face_landmarks.dat`
   - `dlib_face_recognition_resnet_model_v1.dat`

3. **Object Detection:** Place `yolov8s_float16.tflite` in `models/` and `features/object_detection/`

---

## Usage

### Start the robot system

```bash
./start_robot.sh
```

This activates the virtual environment and starts `main_controller.py` on port **5001**. Manual control is active by default.

### Switch features via API

```bash
# Start MAYA voice assistant
curl -X POST http://<pi-ip>:5001/command \
  -H "Content-Type: application/json" \
  -d '{"type": "feature", "feature": "maya"}'

# Start attendance system
curl -X POST http://<pi-ip>:5001/command \
  -H "Content-Type: application/json" \
  -d '{"type": "feature", "feature": "attend"}'

# Start object detection
curl -X POST http://<pi-ip>:5001/command \
  -H "Content-Type: application/json" \
  -d '{"type": "feature", "feature": "object_detection"}'

# Start line following
curl -X POST http://<pi-ip>:5001/command \
  -H "Content-Type: application/json" \
  -d '{"type": "feature", "feature": "line_following"}'

# Send direct motor command
curl -X POST http://<pi-ip>:5001/command \
  -H "Content-Type: application/json" \
  -d '{"type": "instant", "command": "F"}'

# Stop current feature (reverts to manual control)
curl -X POST http://<pi-ip>:5001/command \
  -H "Content-Type: application/json" \
  -d '{"type": "instant", "command": "stop_feature"}'
```

### Run MAYA standalone (for debugging)

```bash
source .venv/bin/activate
python features/maya/maya.py
```

---

## API Reference

**Endpoint:** `POST /command`

| Field | Type | Values |
|---|---|---|
| `type` | string | `"instant"` or `"feature"` |
| `command` | string | `F`, `B`, `L`, `R`, `S`, `stop_feature` (when type = instant) |
| `feature` | string | `maya`, `attend`, `object_detection`, `line_following` (when type = feature) |

**Responses:**
- `200` — `{"status": "command_sent"}` or `{"status": "started"}`
- `400` — `{"error": "invalid_command"}` or `{"error": "missing_feature"}`

---

## Notes

- **Motor API is shared** — do NOT modify method signatures in `hardware/motors.py` (all features depend on it).
- **One feature at a time** — the FeatureManager stops the current feature before starting a new one.
- **Arduino sketches auto-upload** — each feature has a matching sketch in `arduino_sketches/` that gets compiled and uploaded via `arduino-cli`.
- **Large files excluded** — `.tflite` models, dlib `.dat` files, virtual environments, and databases are in `.gitignore`. Download them separately.
- **Audio device** — MAYA is tuned for PulseAudio / TWS headphones. Adjust `MICROPHONE_DEVICE_INDEX` in `features/maya/config.py` for your setup.

---

## License

This project is for educational and personal use.

---

*Built with ❤️ on Raspberry Pi *
Author - ANANY MISHRA