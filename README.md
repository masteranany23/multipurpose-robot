# Multipurpose Robot — MAYA

Clean, minimal README for the multipurpose-robot repository. This project runs MAYA — an Indian-personality voice assistant that controls a Raspberry Pi robot (movement, questions, jokes, date/time, and AI queries).

## Highlights
# Multipurpose Robot — MAYA

A compact, interactive README for the MAYA voice-assistant robot. Designed to be short, clear, and ready to push to GitHub.

## What this repo contains
- `features/maya/` — main assistant implementation (speech, AI, movement glue)
- `hardware/` — motor and sketch uploader utilities (do not change public APIs)
- `arduino_sketches/` — Arduino sketches used by features

## Quick start (copy-paste)
1. Create and activate a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure keys in `features/maya/config.py` (set `GEMINI_API_KEY` if you want AI).

3. Start the robot controller (recommended):

```bash
./start_robot.sh
```

Or run the assistant directly for debugging:

```bash
source .venv/bin/activate && python features/maya/maya.py
```

## Quick usage examples
- Wake word: “Maya”, “Hey Maya”, “Maya ji”
- Movement: “Maya, move forward” / “Maya, turn left” / “Maya, stop”
- Info: “Maya, what time is it?” / “Maya, tell me a joke”
- AI questions (needs Gemini key): “Maya, what is artificial intelligence?”

## Notes & Safety
- The project is tuned for TWS / PulseAudio (device `pulse`) — change `MICROPHONE_DEVICE_INDEX` in `features/maya/config.py` or allow auto-detection.
- Do NOT change `hardware/motors.py` method signatures (used across the codebase).
- Keep large model files out of Git (see `.gitignore`).

## Want this repo cleaned further?
- I removed most top-level test scripts to keep the repo tidy. If you want, I can:
	- Trim `requirements.txt` to exact pinned versions
	- Add a short contribution guide
	- Add CI basics (lint/test)

---
Push-ready. Tell me if you want the `README` worded differently or to add a `CONTRIBUTING.md` or license.