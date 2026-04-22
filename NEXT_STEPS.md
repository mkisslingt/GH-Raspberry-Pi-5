# Next Steps: WaveRover AI Mobility & GenAI

This document outlines the roadmap for transitioning from a stationary tracker to a fully autonomous mobile robot.

## 📍 Phase 1: Connectivity & Workflow
- [ ] **Setup SSHFS:** Mount the Pi's directory to the Mac for direct file editing.
- [ ] **SSH Alias:** Create `rover` alias in `~/.ssh/config`.
- [ ] **GitHub Sync:** Push this local repo to `GH-Raspberry-Pi-5`.

## 🏎 Phase 2: Full Mobility (The Move)
- [ ] **Motor Logic:** Enable `send_motor_cmd` in `follow_me.py`.
- [ ] **Distance Scaling:** Use bounding box size to determine if the robot should move forward/backward.
- [ ] **Turning:** Rotate the chassis if the Pan angle exceeds comfort limits.

## 🧠 Phase 3: Hailo-10H Power Play
- [ ] **Local LLM:** Install `hailo-genai` and run a local model.
- [ ] **VLM Integration:** Use Vision-Language Models to describe the robot's surroundings.
- [ ] **Voice Control:** Add a microphone for natural language commands.

## ⚠️ Notes
- Keep an eye on battery voltage during mobility tests.
- Ensure the USB-C cable to the Pi is secure during movement.
