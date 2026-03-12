#!/usr/bin/env python3
"""
Arduino sketch uploader utility for Modular Robot Control System
"""
import subprocess
import time
import os
from pathlib import Path

class SketchUploader:
    def __init__(self):
        # Arduino CLI path - adjust if necessary
        self.arduino_cli_path = "arduino-cli"  # Assuming arduino-cli is in PATH
        
        # Board configuration - adjust for your Arduino board
        self.board_type = "arduino:avr:uno"  # Change as needed for your board
        
        # Serial port - adjust if your Arduino connects on a different port
        self.port = "/dev/ttyACM0"  # Common port for Arduino Uno on Linux
        
        # Path to sketches directory
        robot_dir = Path("/home/pragyan/Robot")
        self.sketches_dir = robot_dir / "arduino_sketches"
        
    def upload_sketch(self, feature_name):
        """Upload the Arduino sketch for the specified feature"""
        sketch_path = os.path.join(self.sketches_dir, feature_name, f"{feature_name}.ino")
        
        # Check if sketch exists
        if not os.path.exists(sketch_path):
            print(f"Sketch not found: {sketch_path}")
            return False
            
        try:
            # Give Arduino time to reset if needed
            time.sleep(1)
            
            # Compile and upload in one step
            cmd = [
                self.arduino_cli_path, "compile",
                "--upload",
                "--port", self.port,
                "--fqbn", self.board_type,
                sketch_path
            ]
            
            print(f"Uploading sketch: {sketch_path}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Give Arduino time to initialize after upload
            time.sleep(2)
            
            print(f"Upload success: {sketch_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Upload failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return False
            
    def list_ports(self):
        """List available serial ports for debugging"""
        try:
            cmd = [self.arduino_cli_path, "board", "list"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            print(f"Error listing ports: {str(e)}")
            return "Error listing ports"
