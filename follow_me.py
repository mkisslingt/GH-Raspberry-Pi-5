import cv2
import time
import serial
import json
import sys
import os
import numpy as np
import subprocess
import argparse
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from adafruit_servokit import ServoKit
from hailo_platform import VDevice

# FORZAR VISUALIZACION (Headless web mode)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# --- CONFIGURACION DE HARDWARE ---
SERIAL_PORT = '/dev/ttyUSB0'
HEF_PATH = '/usr/share/hailo-models/yolov8m_h10.hef'

# --- CALIBRACION FINAL ---
PAN_OFFSET = 72  
TILT_OFFSET = 10  

# Global for web streaming
latest_frame = None

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                if latest_frame is not None:
                    try:
                        _, jpeg = cv2.imencode('.jpg', latest_frame)
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', len(jpeg))
                        self.end_headers()
                        self.wfile.write(jpeg.tobytes())
                        self.wfile.write(b'\r\n')
                    except: break
                time.sleep(0.1)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class WaveRoverAI:
    def __init__(self, pan_offset=72, tilt_offset=10, no_motors=False, no_tracking=False):
        self.pan_offset = pan_offset
        self.tilt_offset = tilt_offset
        self.no_motors = no_motors
        self.no_tracking = no_tracking
        self.start_time = time.time()
        
        try:
            self.ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)
            self.kit = ServoKit(channels=16)
            print("Hardware: OK")
        except Exception as e:
            print(f"Error hardware: {e}"); sys.exit(1)

        self.pan_min, self.pan_max = -90, 90
        self.pan_rel, self.tilt_rel = 0, 0
        self.curr_l, self.curr_r = 0, 0
        self.lost_frames = 0
        
        self.set_neck(0, 0)
        time.sleep(1.0) 

    def send_motor_cmd(self, left, right):
        if self.no_motors: return
        if time.time() - self.start_time < 5.0: return 
        cmd = {"T":1, "L": int(left), "R": int(right)}
        try: self.ser.write((json.dumps(cmd) + '\n').encode())
        except: pass

    def set_neck(self, pan, tilt):
        self.pan_rel = max(self.pan_min, min(self.pan_max, pan))
        self.tilt_rel = max(-90, min(75, tilt))
        self._apply_servos()

    def move_neck(self, p_delta, t_delta):
        self.pan_rel = max(self.pan_min, min(self.pan_max, self.pan_rel + p_delta))
        self.tilt_rel = max(-90, min(75, self.tilt_rel + t_delta))
        self._apply_servos()

    def _apply_servos(self):
        p_abs = max(0, min(180, self.pan_rel + 90 + self.pan_offset))
        t_abs = max(0, min(180, self.tilt_rel + 90 + self.tilt_offset))
        self.kit.servo[0].angle = p_abs
        self.kit.servo[1].angle = t_abs

    def run(self):
        global latest_frame
        cmd_cam = ['rpicam-vid', '-t', '0', '--width', '640', '--height', '480', '--inline', '--nopreview', '--codec', 'yuv420', '-o', '-']
        proc = subprocess.Popen(cmd_cam, stdout=subprocess.PIPE, bufsize=10**8)
        
        try:
            with VDevice() as vdevice:
                im = vdevice.create_infer_model(HEF_PATH)
                input_name, output_name = im.input_names[0], im.output_names[0]
                with im.configure() as configured:
                    bindings = configured.create_bindings()
                    output_buffer = np.empty(im.output().shape, dtype=np.float32)
                    
                    while True:
                        raw = proc.stdout.read(640 * 480 * 3 // 2)
                        if not raw: continue
                        yuv = np.frombuffer(raw, dtype=np.uint8).reshape((720, 640))
                        frame = cv2.rotate(cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420), cv2.ROTATE_180)
                        
                        resized = cv2.resize(frame, (640, 640))
                        bindings.input(input_name).set_buffer(np.expand_dims(resized, axis=0).astype(np.uint8))
                        bindings.output(output_name).set_buffer(output_buffer)
                        configured.run([bindings], 1000)
                        
                        data = output_buffer.reshape(-1, 6)
                        found, max_score, best_det = False, 0, None
                        for det in data:
                            if det[4] > 0.25 and det[4] > max_score: # Person detection
                                max_score, best_det = det[4], det[:4]

                        if best_det:
                            self.lost_frames, found = 0, True
                            ymin, xmin, ymax, xmax = best_det
                            cx, fy = (xmin + xmax) / 2.0, ymin + (ymax - ymin) * 0.15
                            
                            # Web Stream Visuals
                            cv2.rectangle(frame, (int(xmin*640), int(ymin*480)), (int(xmax*640), int(ymax*480)), (0,255,0), 3)
                            cv2.circle(frame, (int(cx*640), int(fy*480)), 10, (0,0,255), -1)
                            
                            # ULTRA-SMOOTH PAN (Gain 10)
                            pm, tm = int((cx - 0.5) * 10), int((fy - 0.5) * -8)
                            if not self.no_tracking: self.move_neck(pm, tm)

                            # MOTORS: FORWARD/BACKWARD ONLY FOR NOW
                            box_height = ymax - ymin
                            target_base = 0
                            if box_height < 0.20: target_base = 10 # Forward
                            elif box_height > 0.85: target_base = -10 # Backward
                            
                            l_target, r_target = -target_base, target_base # Golden Forward logic
                        else:
                            self.lost_frames += 1
                            l_target, r_target = 0, 0
                            if self.lost_frames > 40:
                                p_drift = -1 if self.pan_rel > 2 else 1 if self.pan_rel < -2 else 0
                                if not self.no_tracking: self.move_neck(p_drift, 0)

                        cv2.putText(frame, f"CONF: {max_score:.2f} | H: {box_height if best_det else 0:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        latest_frame = frame
                        
                        self.curr_l = (0.5 * self.curr_l) + (0.5 * l_target)
                        self.curr_r = (0.5 * self.curr_r) + (0.5 * r_target)
                        self.send_motor_cmd(self.curr_l, self.curr_r)
                        
                        print(f"{'FOLLOW' if found else 'WAIT'} | L:{int(self.curr_l):2} | R:{int(self.curr_r):2} | Pan:{int(self.pan_rel):3}°", end="\r")

        except Exception as e: print(f"\nError: {e}")
        finally:
            self.no_motors = False; self.send_motor_cmd(0, 0); self.set_neck(0, 0)
            proc.terminate(); self.ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pan-offset", type=int, default=72)
    parser.add_argument("--tilt-offset", type=int, default=10)
    parser.add_argument("--no-motors", action="store_true")
    parser.add_argument("--no-tracking", action="store_true")
    args = parser.parse_args()

    server = ThreadedHTTPServer(('0.0.0.0', 8080), StreamingHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(">>> STREAM: http://192.168.50.230:8080")

    WaveRoverAI(args.pan_offset, args.tilt_offset, args.no_motors, args.no_tracking).run()
