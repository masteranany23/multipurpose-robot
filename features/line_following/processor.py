import threading
import time

class LineFollowing:
    def __init__(self):
        """Initialize the line following feature
        
        Note: Arduino sketch upload is now handled by the SketchUploader
        in the main_controller, so we don't need to do it here.
        All line following logic is implemented in the Arduino sketch.
        """
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the line following feature"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()
        print("Line following started")
    
    def stop(self):
        """Stop the line following feature"""
        print("Stopping line following...")
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=5)
                if self.thread.is_alive():
                    print("Warning: Line following thread could not be joined properly")
            except Exception as e:
                print(f"Error joining line following thread: {str(e)}")
        
        print("Line following stopped")
    
    def _monitor(self):
        """Monitor thread to keep feature running"""
        while self.running:
            # This is just a placeholder method to keep the thread alive
            # All actual line following logic is in the Arduino sketch
            time.sleep(0.5)
