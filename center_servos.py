import time
from adafruit_servokit import ServoKit

def center():
    print("Iniciando centrado de servos...")
    try:
        kit = ServoKit(channels=16)
        
        print("Moviendo Pan (Canal 0) a 90 grados...")
        kit.servo[0].angle = 90
        
        print("Moviendo Tilt (Canal 1) a 90 grados...")
        kit.servo[1].angle = 90
        
        print("\n>>> SERVOS EN EL CENTRO ELECTRICO <<<")
        print("Ahora puedes desmontar y volver a montar el cuello mirando al frente.")
        print("Mantén este script abierto o el robot encendido mientras lo haces.")
        
        # Mantener el programa vivo para que el servo mantenga el torque
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    center()
