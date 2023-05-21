# This file contains the PIDController class, which is used in all advanced landing algorithms.

class PIDController:
    def __init__(self, kp, ki, kd):
        """
        initializes the PID controller.
        args:
            kp: the proportional gain
            ki: the integral gain
            kd: the derivative gain
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.last_error = 0
        self.last_time = 0
        self.integral_error = 0

    def compute(self, error, time):
        """
        Computes the output of the PID controller.
        args:
            error: the error of the system (difference between current and target value)
            time: the current time
        returns:
            the output of the PID controller
        """
        dt = time - self.last_time
        de = error - self.last_error
        self.integral_error += error * dt
        self.last_error = error
        self.last_time = time

        proportional = self.kp * error
        derivative = self.kd * de / dt
        integral = self.ki * self.integral_error
        output = proportional + derivative + integral

        if output > 1:
            output = 1
        elif output < 0:
            output = 0

        return output