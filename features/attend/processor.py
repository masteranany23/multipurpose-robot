import subprocess
import sys
import os
import threading
import time
import logging

class Attend:
    def __init__(self):
        self.process = None
        self.running = False
        self.thread = None
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("AttendFeature")
    
    def start(self):
        """Start the attendance system in a virtual environment"""
        self.running = True
    
        # Define the path to the attendance script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        attend_script = os.path.join(script_dir, "attend.py")
    
        # Define virtual environment path
        venv_path = os.path.join(script_dir, "env")
    
        # Create command to activate virtual environment and run script
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Linux/Mac
            python_exe = os.path.join(venv_path, 'bin', 'python')
    
        self.logger.info(f"Starting attendance system using {python_exe}")
    
        try:
            # Create environment with proper PATH to include the system libraries
            env = os.environ.copy()
        
            # Add the virtual environment's library paths to PATH
            if 'PATH' in env:
                env['PATH'] = os.path.join(venv_path, 'bin') + os.pathsep + env['PATH']
        
            # Run the attendance script in the virtual environment with the enhanced environment
            self.process = subprocess.Popen(
                [python_exe, attend_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=script_dir,  # Set current working directory explicitly
                env=env          # Pass the enhanced environment
            )
        
            # Rest of the code remains the same
        
            
        except Exception as e:
            self.logger.error(f"Failed to start attendance system: {str(e)}")
            self.running = False
    
    def _monitor_output(self):
        """Monitor and log output from the attendance process"""
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read output line by line
                stdout_line = self.process.stdout.readline()
                if stdout_line:
                    self.logger.info(f"Attend output: {stdout_line.strip()}")
                
                stderr_line = self.process.stderr.readline()
                if stderr_line:
                    self.logger.error(f"Attend error: {stderr_line.strip()}")
                    
                # If both are empty, process might be done
                if not stdout_line and not stderr_line:
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error monitoring attendance process: {str(e)}")
                break
    
    def stop(self):
        """Stop the attendance system"""
        self.logger.info("Stopping attendance system...")
        self.running = False
        
        # Terminate the process if it's still running
        if self.process and self.process.poll() is None:
            try:
                # Try graceful termination first
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if termination doesn't work
                self.logger.warning("Forcing attendance process to stop")
                self.process.kill()
            
        # Wait for monitoring thread to complete
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        self.logger.info("Attendance system stopped")

# For testing standalone execution
if __name__ == "__main__":
    attend = Attend()
    try:
        attend.start()
    except KeyboardInterrupt:
        attend.stop()
