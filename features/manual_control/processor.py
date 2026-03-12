class ManualControl:
    def __init__(self, motor_controller):
        self.motors = motor_controller
        self._active = False

    def start(self):
        self._active = True
        self.motors.send_command('S')  # Initial stop

    def stop(self):
        self._active = False
        self.motors.send_command('S')

    def send(self, cmd):
        if self._active:
            self.motors.send_command(cmd)
