# This file will contain the algorithm that lands a vessel on the moon in KSP.
# The algorithm will be a naive one, and will not use a PID controller to improve the robustness of the landing.

import krpc
import time
from helper_functions import decouple_and_deorbit, plot_results

if __name__ == "__main__":
    conn = krpc.connect()
    vessel = conn.space_center.active_vessel
    print(vessel.name)
    vessel, engine, body_frame = decouple_and_deorbit(vessel)
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
        # print info
        print(str(time.time())+"-:-", "VS: " + str(vs), "HS: " + str(hs),"ALT: " + str(alt))

        # over 2 km above the ground
        if alt > 15000:
            continue
        elif 15000 > alt > 2000:  # maintain a vertical speed of [20-25] m/s
            if vs > 25: 
                NN += 0.003  # more power for braking
            if vs < 20: 
                NN -= 0.003  # less power for braking
            if vs < 17:
                NN = 0.1
            if NN < 0:
                NN = 0
            if NN > 1:
                NN = 1
        # lower than 2 km - horizontal speed should be close to zero
        else: # if alt < 2000
            # different NN for different vertical speeds
            if vs > 15:
                NN = 0.7
            elif vs > 8:
                NN = 0.4
            elif vs > 5:
                NN = 0.2
            else:
                NN = 0.05
            if alt < 125:  # very close to the ground!
                NN = 1  # maximum braking!
                if vs < 3: 
                    NN = 0.05  # if it is slow enough - go easy on the brakes 

        if alt < 5:  # no need to stop
            NN = 0.4

        # retract legs
        if alt < 100 and not vessel.control.legs:
            vessel.control.legs = True
        
        print("THRUST: " + str(NN))
        vessel.control.throttle = NN

    vessel.control.throttle = 0
    print("landed!")
    plot_results(times, speeds, alts, thrusts)
