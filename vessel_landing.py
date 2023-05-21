# This file contains the algorithm that lands a vessel on the moon in KSP.
# The algorithm used a PID controller to improve the robustness of the landing.

import krpc
import time
from helper_functions import decouple_and_deorbit, plot_results
from PID_controller import PIDController
    
def target_vs_function(alt):
    if alt > 12500:
        return 99999
    if alt > 7500:
        return 180
    # if alt > 10:
    return 0.023898531375166888*alt+0.3
    # return math.e**(alt - 3)
    # elif alt <= 10:
    #     return 0.25*math.log(alt)+0.25

if __name__ == "__main__":
    conn = krpc.connect()
    vessel = conn.space_center.active_vessel

    vessel, engine, body_frame = decouple_and_deorbit(vessel, conn)
    
    # set up PID controller
    pidcontroller = PIDController(0.4, 0.00, 0.2) # pretty good moon values
    NN = 0
    times = []
    speeds = []
    alts = []
    thrusts = []
    timeStart = time.time()
    while vessel.situation != vessel.situation.landed:
        time.sleep(0.1)
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
        print()

        # handle direction of vessel
        if vs < 0:
            vessel.control.throttle = 0
            try:
                print("SAS PROGRADE")
                vessel.control.sas_mode = vessel.control.sas_mode.prograde
            except:
                print("SAS ERROR")
            continue
        elif vessel.control.sas_mode != vessel.control.sas_mode.retrograde:
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
    print("landed!")
    plot_results(times, speeds, alts, thrusts)