# WaveRover AI - Raspberry Pi 5 + Hailo-10H

Autonomous AI Robot built on the WaveRover platform, powered by Raspberry Pi 5 and accelerated by the Hailo-10H AI HAT+.

## 🚀 Project Overview
- **Brain:** Raspberry Pi 5 (8GB)
- **AI Accelerator:** Hailo-10H (GenAI capable)
- **Vision:** Arducam IMX708 (HDR, Autofocus)
- **Platform:** WaveRover (4WD, ESP32 Serial Control)
- **Tracking:** Pan/Tilt servo mechanism for face/object tracking.

## 🛠 Current Progress
- [x] Hardware Assembly & Wiring.
- [x] Hailo Zen API Integration (YOLOv8 face detection).
- [x] Pan/Tilt Calibration & Physical Centering.
- [x] Camera Pipe setup (rpicam-vid to OpenCV).

## 📡 Remote Brain Workflow
This project uses a "Remote Brain" setup:
1. **Development:** Gemini CLI on Host Mac.
2. **Execution:** Raspberry Pi 5 (via SSH/SSHFS).
3. **Storage:** GitHub (Sync & Version Control).

## 📄 License
MIT
