import os
import subprocess
import threading
import time
import signal
import sys
from pathlib import Path

# Add the Robot directory to the Python path
sys.path.append('/home/pragyan/Robot')

# Ensure virtual environment packages are available
venv_site_packages = "/home/pragyan/Robot/.venv/lib/python3.11/site-packages"
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

class Maya:
    def __init__(self):
        self.running = False
        self.maya_instance = None
        self.thread = None
        print("🔧 MAYA processor initialized with enhanced integration")
        
    def start(self):
        """Start Enhanced MAYA assistant"""
        try:
            # Import MAYA with proper environment
            from features.maya.maya import MAYAAssistant
            print("✅ Enhanced MAYA class imported successfully")
            
            self.maya_instance = MAYAAssistant()
            self.running = True
            
            print("🚀 Enhanced MAYA assistant started successfully!")
            print("🎙️ MAYA is now listening with improved speech recognition...")
            print("🤖 Movement commands are integrated with direct motor control")
            print("🧠 Gemini AI is ready for intelligent responses")
            
            # Start MAYA's main loop (blocking call)
            self.maya_instance.start()
                
        except ImportError as e:
            print(f"❌ Failed to import Enhanced MAYA: {e}")
            print("💡 Make sure all required packages are installed in the virtual environment")
        except Exception as e:
            print(f"❌ Failed to start Enhanced MAYA: {e}")
            
    def stop(self):
        """Stop Enhanced MAYA assistant gracefully"""
        print("🛑 Stopping Enhanced MAYA assistant...")
        self.running = False
        
        # Stop MAYA instance
        if self.maya_instance:
            try:
                self.maya_instance.running = False
                self.maya_instance.cleanup()
                print("✅ Enhanced MAYA instance stopped")
            except Exception as e:
                print(f"❌ Error stopping Enhanced MAYA instance: {str(e)}")
                
        print("🏁 Enhanced MAYA stop procedure completed")
