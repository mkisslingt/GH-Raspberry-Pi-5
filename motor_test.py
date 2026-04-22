import serial
import json
import time

SERIAL_PORT = '/dev/ttyUSB0'

def test_motors():
    try:
        ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)
        print("Conectado al WaveRover. Iniciando test de motores (MODO LENTO)...")
        
        def send(l, r, msg):
            print(f"Testing: {msg} (L:{l}, R:{r})")
            cmd = {"T":1, "L": l, "R": r}
            ser.write((json.dumps(cmd) + '\n').encode())
            time.sleep(4)
            ser.write((json.dumps({"T":1, "L":0, "R":0}) + '\n').encode())
            time.sleep(1.5)

        # 1. Test LADO IZQUIERDO
        send(25, 0, "SOLO IZQUIERDA ADELANTE")
        send(-25, 0, "SOLO IZQUIERDA ATRAS")

        # 2. Test LADO DERECHO
        send(0, 25, "SOLO DERECHA ADELANTE")
        send(0, -25, "SOLO DERECHA ATRAS")

        print("\nTest completado. ¿Se movieron todos en la direccion correcta?")
        ser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_motors()
