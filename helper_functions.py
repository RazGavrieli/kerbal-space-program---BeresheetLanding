import time

def decouple_and_deorbit(vessel, conn):
    if vessel.parts.docking_ports[0].state == vessel.parts.docking_ports[0].state.docked:
        vessel = vessel.parts.docking_ports[0].undock()
        vessel = conn.space_center.active_vessel
        # wait 5 seconds for undocking, then activate engines
        print("undocking..")
        if vessel.crew_count == 0:
            print("Did you transfer crew to the lander?, restart, transfer crew and try again.")
            exit(1)
        vessel.control.sas = True
        vessel.control.legs = False
        time.sleep(10)

    # Get a referencea to the vessel's engine, body frame, and control
    body_frame = conn.space_center.ReferenceFrame.create_relative(vessel.orbit.body.non_rotating_reference_frame, (0,0,0))
    engine = vessel.parts.engines[0]
    engine.active = True
    vessel.control.throttle = 0
    vessel.auto_pilot.engage()

    if vessel.control.sas_mode != vessel.control.sas_mode.retrograde:
        vessel.control.sas_mode = vessel.control.sas_mode.retrograde
        print("rotating..")
        time.sleep(3)

    hs = vessel.flight(body_frame).horizontal_speed
    if hs > 500:
        # burn for 60 seconds to stop orbital horizontal velocity
        vessel.control.throttle = 1
        print("breaking from orbit..")
        time.sleep(60)
        vessel.control.throttle = 0

    return vessel, engine, body_frame
    
def plot_results(times, speeds, alts, thrusts):
    import matplotlib.pyplot as plt
    # Create a figure with two subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

    # Plot the speed vs time data on the first subplot
    ax1.plot(times, speeds)
    ax1.set_ylabel('Speed')
    ax1.set_title('(Speed, alt and NN) vs Time')

    # Plot the altitude vs time data on the second subplot
    ax2.plot(times, alts)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Altitude')

    # Plot the altitude vs time data on the second subplot
    ax3.plot(times, thrusts)
    ax3.set_xlabel('Time')
    ax3.set_ylabel('NN')

    # Show the plot
    plt.show()
