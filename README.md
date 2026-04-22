# WaveRover-MKT AI: Raspberry Pi 5 + Hailo-10H

This repository contains the software for an autonomous tracking robot built on the **WaveRover** chassis, powered by a **Raspberry Pi 5** with a **Hailo-10H** M.2 AI accelerator.

## Status: Full Mobility (Phase 2 Complete)
The robot is no longer stationary. It can track a person, move forward to follow, move backward if the person is too close, and rotate its chassis to keep the target centered.

### Core Logic
- **Detection:** YOLOv8 running on Hailo-10H (720p @ 30fps).
- **Neck (Pan-Tilt):** Arducam IMX708 follows the person's upper body.
- **Mobility:**
  - **Distance Scaling:** Uses bounding box height to maintain a constant distance (~0.5-1m).
  - **Chassis Turning:** Rotates the entire chassis when the camera pan exceeds ±20°.
  - **Safety:** Motor speeds are capped at 100/255 for initial testing.

## Phase 3: Hailo-10H Power Play (Coming Soon)
The next stage is to leverage the full 40 TOPS of the Hailo-10H to run:
- **Local LLMs:** Use `hailo-genai` for natural language reasoning.
- **Vision-Language Models (VLM):** Describe surroundings and navigate based on high-level instructions.
- **Voice Commands:** Adding microphone and speaker for interaction.

## Setup & Workflow
- **SSH Alias:** Use `ssh rover` to connect (`WaveRover-MKT.local`).
- **Mount:** `sshfs rover:/home/pi5-mkt ~/WaveRover` to edit files locally.
- **Run:** `python3 follow_me.py`

## 📄 License
MIT
