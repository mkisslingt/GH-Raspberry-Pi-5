import cv2
import time
import serial
import json
import sys
import os
import numpy as np
import subprocess
from adafruit_servokit import ServoKit
from hailo_platform import VDevice

# FORZAR VISUALIZACION
os.environ["QT_QPA_PLATFORM"] = "xcb"

# --- CONFIGURACION DE HARDWARE ---
SERIAL_PORT = '/dev/ttyUSB0'
HEF_PATH = '/usr/share/hailo-models/yolov8m_h10.hef'

# --- CALIBRACION FINAL ---
PAN_OFFSET = -44  
TILT_OFFSET = 49  

class WaveRoverAI:
    def __init__(self):
        print(f"Modelo IA: {HEF_PATH}")
        print("Iniciando Hardware...")
        
        try:
            self.ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)
            self.kit = ServoKit(channels=16)
            print("Conexion Hardware: OK")
        except Exception as e:
            print(f"Error hardware: {e}")
            sys.exit(1)

        # --- LÍMITES FÍSICOS DETECTADOS ---
        # Como el centro esta en 46 abs, el limite derecho es -46 rel.
        self.pan_min = -46  # Límite derecho real
        self.pan_max = 90   # Límite izquierdo (podría ser hasta 134, pero dejamos 90)
        
        self.pan_rel = 0   
        self.tilt_rel = 0  
        self.update_neck(0, 0)

    def send_motor_cmd(self, left, right):
        cmd = {"T":1, "L": 0, "R": 0}
        try:
            self.ser.write((json.dumps(cmd) + '\n').encode())
        except: pass

    def update_neck(self, p_delta, t_delta):
        # Aplicamos los limites fisicos detectados para evitar "zonas muertas"
        self.pan_rel = max(self.pan_min, min(self.pan_max, self.pan_rel + p_delta))
        self.tilt_rel = max(-90, min(75, self.tilt_rel + t_delta))
        
        pan_abs = self.pan_rel + 90 + PAN_OFFSET
        tilt_abs = self.tilt_rel + 90 + TILT_OFFSET
        
        # Proteccion electronica
        pan_abs = max(0, min(180, pan_abs))
        tilt_abs = max(0, min(180, tilt_abs))
        
        self.kit.servo[0].angle = pan_abs
        self.kit.servo[1].angle = tilt_abs

    def run(self):
        print("Lanzando camara...")
        cmd_cam = [
            'rpicam-vid', '-t', '0', '--width', '640', '--height', '480',
            '--inline', '--nopreview', '--codec', 'yuv420', '-o', '-'
        ]
        proc = subprocess.Popen(cmd_cam, stdout=subprocess.PIPE, bufsize=10**8)
        
        print(f"\n>>> LÍMITES AJUSTADOS: Pan {self.pan_min}° a {self.pan_max}° <<<")
        
        try:
            with VDevice() as vdevice:
                im = vdevice.create_infer_model(HEF_PATH)
                input_name = im.input_names[0]
                output_name = im.output_names[0]
                
                with im.configure() as configured:
                    bindings = configured.create_bindings()
                    output_shape = im.output().shape 
                    output_buffer = np.empty(output_shape, dtype=np.float32)
                    
                    try:
                        while True:
                            raw = proc.stdout.read(640 * 480 * 3 // 2)
                            if not raw: continue
                            
                            yuv = np.frombuffer(raw, dtype=np.uint8).reshape((720, 640))
                            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
                            frame = cv2.rotate(frame, cv2.ROTATE_180) 
                            
                            resized = cv2.resize(frame, (640, 640))
                            bindings.input(input_name).set_buffer(np.expand_dims(resized, axis=0).astype(np.uint8))
                            bindings.output(output_name).set_buffer(output_buffer)
                            configured.run([bindings], 1000)
                            
                            data = output_buffer.reshape(-1, 6)
                            found = False
                            max_score = 0
                            best_det = None
                            
                            for i in range(10):
                                base = 1 + (i * 5)
                                ymin, xmin, ymax, xmax, score = output_buffer[base:base+5]
                                if score > 0.5 and score > max_score:
                                    max_score = score
                                    best_det = (ymin, xmin, ymax, xmax)

                            if best_det:
                                found = True
                                ymin, xmin, ymax, xmax = best_det
                                cx = (xmin + xmax) / 2.0
                                fy = ymin + (ymax - ymin) * 0.15
                                
                                # Dibujar
                                cv2.circle(frame, (int(cx*640), int(fy*480)), 8, (0,0,255), -1)
                                
                                # Movimiento suave
                                pm, tm = 0, 0
                                if cx < 0.44: pm = -1
                                elif cx > 0.56: pm = 1
                                if fy < 0.44: tm = 1
                                elif fy > 0.56: tm = -1
                                
                                self.update_neck(pm, tm)
                                print(f"Pan:{int(self.pan_rel):3}° | Tilt:{int(self.tilt_rel):3}° | Conf:{max_score:.2f}", end="\r")

                            cv2.imshow('WaveRover Final Calibration', frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'): break
                            
                    except KeyboardInterrupt:
                        print("\nSaliendo...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            self.send_motor_cmd(0, 0)
            proc.terminate()
            cv2.destroyAllWindows()
            self.ser.close()

if __name__ == "__main__":
    WaveRoverAI().run()
