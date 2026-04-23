# Session Handoff: WaveRover AI

## 🔋 Current Status: Paused for Recharge
The robot logic is implemented and verified, but physical testing was cut short by **battery undervoltage**. The Pi 5 is reporting power drops during motor movement, causing serial port instability.

## 🛠 Hardware Configuration
- **Golden Center:** `Pan 72, Tilt 10` (Manually re-aligned and hardcoded).
- **Motor Wiring (Golden Mix):**
  - **Left Side:** Inverted (`+` is Backward, `-` is Forward).
  - **Right Side:** Standard (`+` is Forward, `-` is Backward).
  - **Final Logic:** `l_target = -target_base + target_turn` | `r_target = target_base + target_turn`.
- **IP Address:** `192.168.50.230`

## 💻 Software Features (follow_me.py)
1.  **Coordinate Compensation:** The camera counter-pans during chassis rotation to keep the subject locked in frame.
2.  **Web Stream:** Live MJPEG feed with AI debug overlays at `http://192.168.50.230:8080`.
3.  **Safe Startup:** 5-second motor lockout at startup to allow time to open the web stream.
4.  **Auto-Center:** Neck slowly drifts back to (0,0) if detection is lost for >2 seconds.
5.  **Crawl Speed:** Currently capped at **12/255** for safety.

## 🚀 How to Resume
1.  **Power Up:** Ensure fresh batteries or a 5A power supply is connected.
2.  **Mount:** `sshfs rover:/home/pi5-mkt ~/WaveRover`
3.  **Run:** `python3 follow_me.py`
4.  **Debug:** Open `http://192.168.50.230:8080` in Chrome/Safari.

## 📍 Next Step
Proceed to **Phase 3: GenAI**. The Hailo-10H is verified working with `Qwen2.5-Coder-1.5B`. The next goal is to let the LLM control the motors via natural language tools.
