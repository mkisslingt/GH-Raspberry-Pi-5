# Next Steps: WaveRover AI Mobility & GenAI

This document outlines the roadmap for transitioning from a stationary tracker to a fully autonomous mobile robot.

## 📍 Phase 1: Connectivity & Workflow
- [x] **Setup SSHFS:** Mount the Pi's directory to the Mac for direct file editing.
- [x] **SSH Alias:** Create `rover` alias in `~/.ssh/config`.
- [x] **GitHub Sync:** Push this local repo to `GH-Raspberry-Pi-5`.

## 🏎 Phase 2: Full Mobility (The Move)
- [x] **Motor Logic:** Enable `send_motor_cmd` in `follow_me.py`.
- [x] **Distance Scaling:** Proportional scaling based on bounding box height.
- [x] **Turning:** Proportional chassis rotation with coordinate compensation.
- [x] **Golden Mix Derived:** Left side inversion handled (`L: -base + turn`).
- [x] **Mechanical Alignment:** Center fixed at `Pan 72, Tilt 10`.

## 🧠 Phase 3: Hailo-10H Power Play
- [ ] **Local LLM:** Install `hailo-genai` and run a local model.
- [ ] **VLM Integration:** Use Vision-Language Models to describe the robot's surroundings.
- [ ] **Voice Control:** Add a microphone for natural language commands.

## ⚠️ Notes
- **Power Critical:** Pi 5 reports `Undervoltage` during mobility. Ensure batteries are full or use the official 27W (5A) supply.
- **Web Stream:** Integrated into `follow_me.py` at `http://<pi-ip>:8080` for debugging.
- **Safety:** Motor speeds are currently set to a 'Crawl' (12) for low-power stability.
