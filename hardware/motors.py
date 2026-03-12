# hardware/motors.py
import serial
from threading import Lock

# Global serial connection
_serial_connection = None
_serial_lock = Lock()

def close_serial_connection():
    global _serial_connection
    with _serial_lock:
        if _serial_connection and _serial_connection.is_open:
            _serial_connection.close()
            _serial_connection = None

def reconnect_serial():
    global _serial_connection
    with _serial_lock:
        if not _serial_connection or not _serial_connection.is_open:
            _serial_connection = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    
class MotorController:
    def __init__(self):
        global _serial_connection
        with _serial_lock:
            if not _serial_connection:
                _serial_connection = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.lock = Lock()  # Thread safety
    
    def send_command(self, cmd):
        global _serial_connection
        with _serial_lock:
            if _serial_connection and _serial_connection.is_open:
                _serial_connection.write(cmd.encode())  # Send to Arduino
    
    def move_forward(self):
        """Move robot forward"""
        self.send_command('F')
    
    def move_backward(self):
        """Move robot backward"""
        self.send_command('B')
    
    def turn_left(self):
        """Turn robot left"""
        self.send_command('L')
    
    def turn_right(self):
        """Turn robot right"""
        self.send_command('R')
    
    def stop(self):
        """Stop robot movement"""
        self.send_command('S')
    
    def cleanup(self):
        close_serial_connection()
