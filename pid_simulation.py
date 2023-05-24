# We will use this file to simulato world enviorment and the vessel, 
# Then we initiate a PID controller to control the vessel and try to keep it in the air (VS=0). 
# We will brute-force the PID controller parameters to find the best ones for the job.

from PID_controller import PIDController

import numpy as np

class simulatorEnviorment:
    def __init__(self, mass, max_thrust, time_step=0.1, gravity=1.62):
        self.gravity = gravity # Earth's gravity in m/s^2
        self.mass = mass    # mass of spacecraft
        self.max_thrust = max_thrust # maximum thrust of engines
        self.time_step = time_step # time for each step in seconds
        self.height = None # height above the earth's surface
        self.velocity = None # velocity of spacecraft
        self.reset()

    def reset(self, start_height=1000, start_velocity=0):
        """Reset spacecraft to initial conditions."""
        self.height = start_height
        self.velocity = -start_velocity  # upwards velocity is negative

    def step(self, throttle):
        """Perform one time step and return new height and velocity."""
        # Limit throttle to [0, 1]
        throttle = np.clip(throttle, 0, 1)
        
        # Calculate net force (F = ma), note the change in direction
        thrust = -throttle * self.max_thrust
        force = thrust + self.mass * self.gravity  # force of gravity is now positive

        # Update velocity (v = u + at)
        acceleration = force / self.mass
        self.velocity += acceleration * self.time_step

        # Update height (s = ut + 0.5at^2)
        self.height -= self.velocity * self.time_step + 0.5 * acceleration * self.time_step ** 2

        return self.height, self.velocity


if __name__ == "__main__":
    simulation = simulatorEnviorment(mass=500, max_thrust=400, gravity=9.81)

    possibleValues = np.arange(0.00, 1, 0.05)
    bestAverageSpeed = 99999
    bestValues = [0, 0]
    targetVelocity = 10
    for i in possibleValues:
        for j in possibleValues:
            # pid = PIDController(0.4, 0.0, 0.2) # moon
            # print("Testing values: " + str(i) + " " + str(j))
            pid = PIDController(i, 0.0, j) 
            NN = 0
            time = 0

            averageSpeed = 0
            samples = 0
            simulation.reset()
            while simulation.height>0:

                time += 0.1
                samples += 1
                NN = pid.compute(simulation.velocity-targetVelocity, time)
                height, velocity = simulation.step(NN)
                averageSpeed += velocity

            averageSpeed /= samples
            # print("Average speed: " + str(averageSpeed), "Samples: " + str(samples))

            if i == 0.4 and j == 0.2:
                print("Average speed: " + str(averageSpeed), "Samples: " + str(samples))
            if samples == 0:
                continue
            if abs(averageSpeed - targetVelocity) < abs(bestAverageSpeed - targetVelocity):
                bestAverageSpeed = averageSpeed
                bestValues = [i, j]
                print("New best: " + str(bestAverageSpeed) + " with values: " + str(bestValues))

    print("Best average speed: " + str(bestAverageSpeed) + " with values: " + str(bestValues))