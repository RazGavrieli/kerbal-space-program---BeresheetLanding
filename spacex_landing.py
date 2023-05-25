import krpc
import time
from helper_functions import plot_results
from PID_controller import PIDController

def target_vs_function(alt):
    if alt > 475:
        return 9999
    if alt > 15:
        return 4
    else:
        return 0

if __name__ == "__main__":
    conn = krpc.connect()

    vessel = conn.space_center.active_vessel
    # Get a reference to the vessel's engines
    engines = vessel.parts.engines
    engine = engines[0]
    engine.active = True
    vessel.control.throttle = 0

    # Set SAS to retrograde
    body_frame = conn.space_center.ReferenceFrame.create_relative(vessel.orbit.body.non_rotating_reference_frame, (0,0,0))
    vessel.auto_pilot.engage()
    vessel.control.sas = True

    # set up PID controller
    pidcontroller = PIDController(0.05, 0.00, 0.025) # rough earth values
    NN = 0
    times = []
    speeds = []
    alts = []
    thrusts = []
    timeStart = time.time()
    while vessel.situation != vessel.situation.landed:
        time.sleep(0.01)
        times.append(time.time()-timeStart)
        # get current info
        vs = vessel.flight(body_frame).vertical_speed*-1
        hs = vessel.flight(body_frame).horizontal_speed
        alt = vessel.flight().surface_altitude
        # save info for matplotlib
        thrusts.append(NN)
        speeds.append(vs)
        alts.append(alt)
        # print all info
        print(str(time.time())+"-:-", "VS: " + str(vs), "HS: " + str(hs),"ALT: " + str(alt))

        # handle direction of rocket
        if vessel.control.sas_mode != vessel.control.sas_mode.retrograde:
            try:
                print("SAS RETROGRADE")
                vessel.control.sas_mode = vessel.control.sas_mode.retrograde
            except:
                print("SAS ERROR")

        # retract legs
        if alt < 100 and not vessel.control.legs:
            vessel.control.legs = True


        target_vs = target_vs_function(alt)
        NN = pidcontroller.compute(vs-target_vs, time.time())
        print("THRUST: " + str(NN), "TARGET VS: " + str(target_vs))
        vessel.control.throttle = NN

    vessel.control.throttle = 0
    vessel.control.sas = False
    print("landed!")
    plot_results(times, speeds, alts, thrusts)