# features/object_detection/processor.py
import os
import subprocess
import threading
import time
import signal
from pathlib import Path

class ObjectDetection:
    def __init__(self):
        self.running = False
        self.process = None
        self.thread = None
        self.feature_dir = Path("/home/pragyan/Robot/features/object_detection")
        self.script_path = self.feature_dir / "object_detection.py"
        self.venv_python = self.feature_dir / "venv/bin/python"

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_detection)
        self.thread.daemon = True
        self.thread.start()

    def _run_detection(self):
        try:
            env = self._get_environment()
            self.process = subprocess.Popen(
                [str(self.venv_python), str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Capture stderr
                text=True,
                env=env,
                cwd=str(self.feature_dir))  # Critical for path resolution
                
            # Real-time output logging
            while self.running:
                output = self.process.stdout.readline()
                if output:
                    print(f"[ObjectDetection] {output.strip()}")
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Detection error: {str(e)}")

    def _get_environment(self):
        env = os.environ.copy()
        env.update({
            "LD_LIBRARY_PATH": f"/usr/lib/{os.uname().machine}-linux-gnu/",
            "PYTHONPATH": f"{self.feature_dir}/venv/lib/python3.11/site-packages:/usr/lib/python3/dist-packages",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "LIBCAMERA_RPI_TUNING_FILE": "/usr/share/libcamera/ipa/raspberrypi/ov5647.json"
        })
        return env

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.thread:
            self.thread.join(timeout=1)
