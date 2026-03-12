import sys
import os

# Ensure virtual environment packages are available
venv_site_packages = "/home/pragyan/Robot/.venv/lib/python3.11/site-packages"
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import importlib
import atexit
from hardware.motors import MotorController
from hardware.sketch_uploader import SketchUploader

# Initialize Flask and hardware FIRST
app = Flask(__name__)
motors = MotorController()  # Instantiate before FeatureManager

class FeatureManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.current_feature = None
        self.current_future = None
        self.manual_control = None
        # Initialize sketch uploader
        self.sketch_uploader = SketchUploader()
        self._init_manual_control()
    
    def _init_manual_control(self):
        """Initialize manual control on startup"""
        try:
            # Upload manual control sketch
            self.sketch_uploader.upload_sketch("manual_control")
            
            # Start manual control feature
            module = importlib.import_module("features.manual_control.processor")
            self.manual_control = module.ManualControl(motors)
            self.manual_control.start()
            print("Manual control initialized")
        except Exception as e:
            print(f"Manual control init failed: {str(e)}")
    
    def start_feature(self, feature_name):
        """Stop current feature and start requested feature"""
        self._stop_current_feature()
        
        # For MAYA, we keep manual control running
        if feature_name != "maya":
            self.manual_control.stop()
        
        # Upload appropriate Arduino sketch
        try:
            self.sketch_uploader.upload_sketch(feature_name)
        except Exception as e:
            print(f"Failed to upload sketch for {feature_name}: {str(e)}")
        
        try:
            # Import and start the feature module
            if feature_name == "maya":
                # Special handling for MAYA with virtual environment
                module = importlib.import_module(f"features.{feature_name}.processor")
                feature_class = getattr(module, feature_name.title())
                self.current_feature = feature_class()
                self.current_future = self.executor.submit(self.current_feature.start)
                return True
            else:
                # Regular feature handling
                module = importlib.import_module(f"features.{feature_name}.processor")
                feature_class = getattr(module, feature_name.title().replace("_", ""))
                self.current_feature = feature_class()
                self.current_future = self.executor.submit(self.current_feature.start)
                return True
        except Exception as e:
            print(f"Feature error: {str(e)}")
            # Revert to manual control on error
            self._stop_current_feature()
            return False
    
    def _stop_current_feature(self):
        """Cleanup any running feature"""
        if self.current_feature:
            print("Stopping current feature")
            try:
                self.current_feature.stop()
                # Wait for feature to actually stop
                if self.current_future:
                    try:
                        self.current_future.result(timeout=10)  # Wait up to 10 seconds
                    except Exception as e:
                        print(f"Error waiting for feature to stop: {str(e)}")
                        # The feature thread might still be running but we continue anyway
            
                self.current_feature = None
                self.current_future = None
            
                # Upload manual control sketch
                self.sketch_uploader.upload_sketch("manual_control")
            
                # Re-enable manual control
                self.manual_control.start()
                return True
            except Exception as e:
                print(f"Exception during feature stop: {str(e)}")
                # Even if there was an error, reset our state
                self.current_feature = None
                self.current_future = None
            
                # Try to recover with manual control
                try:
                    self.sketch_uploader.upload_sketch("manual_control")
                    self.manual_control.start()
                except Exception as inner_e:
                    print(f"Failed to recover with manual control: {str(inner_e)}")
            
                return False
        return False
# Initialize feature manager AFTER hardware
feature_manager = FeatureManager()
@app.route('/command', methods=['POST'])
def handle_control():
    data = request.json
    if not data or 'type' not in data:
        return jsonify({"error": "invalid_request"}), 400
    
    cmd_type = data['type']
    
    if cmd_type == "instant":
        cmd = data.get('command', '')
        if cmd in ['F', 'B', 'L', 'R', 'S']:
            motors.send_command(cmd)
            return jsonify({"status": "command_sent"})
        elif cmd == "stop_feature":
            feature_manager._stop_current_feature()
            return jsonify({"status": "feature_stopped"})
        return jsonify({"error": "invalid_command"}), 400
    
    elif cmd_type == "feature":
        feature = data.get('feature', '')
        if feature:
            success = feature_manager.start_feature(feature)
            return jsonify({"status": "started" if success else "failed"})
        return jsonify({"error": "missing_feature"}), 400
    
    return jsonify({"error": "invalid_type"}), 400
@atexit.register
def cleanup():
    """Ensure proper shutdown"""
    motors.cleanup()
    feature_manager._stop_current_feature()
    print("System cleaned up")

if __name__ == '__main__':
    try:
        print("Starting robot controller...")
        app.run(host='0.0.0.0', port=5001, threaded=True)
    except KeyboardInterrupt:
        print("Server stopped by user")
