# Using Kerbal Space Program to Simulate Beresheet Landing

By the end of this section, you will be able to write Python code that will land a spacecraft on the surface of the moon in the game KSP - "Kerbal Space Program."

Using KSP as a simulation sandbox, we can observe our code in a 3D simulated environment and learn about how changes in our code affect the landing. This guide covers the installation process of the requirements needed to control a spacecraft in KSP with Python code. Then, it showcases a scenario that represents the Beresheet Landing scenario. After that, we will make changes to the code and observe them in real-time.
<p align="center">
<img width="541" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/36a4a3d6-792a-4a7a-ac6c-669e2cf64eb2">
</p>

## Installation and requirements 

In this tutorial, we assume that you have an installed copy of KSP on your computer. If you don't own a copy, you can acquire one through a popular digital distribution platform.

Download KRPC version 0.5.0, which can be obtained from the official release page of the KRPC project. You can find the download link by visiting the project's GitHub page or by directly accessing the release file at this link:

[https://github.com/krpc/krpc/releases/download/v0.5.0/krpc-0.5.0.zip](https://github.com/krpc/krpc/releases/download/v0.5.0/krpc-0.5.0.zip)

Unzip the downloaded file and copy the contents of the GameData folder.

Paste the copied contents into the GameData folder located in the installation path of the game. The specific installation path may vary depending on your operating system. Here are some examples:

- MacOS path example:
/Users/<username>/Library/Application Support/Steam/steamapps/common/Kerbal Space Program
- Windows path example:
C:\Program Files\Steam\SteamApps\common\Kerbal Space Program

Once you've added the contents of the mod to the GameData folder, your KSP installation should be able to communicate with your code. Let's verify the installation:

1. Launch the game and open a saved game in flight mode. If you don't have a save or are unsure how to do so, you can go into the scenarios section and launch one of the scenarios. You will be controlling a vessel.
2. At this point, the KRPC window should be visible on the screen.
<p align="center">
<img width="280" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/bba8fffb-2cb8-4e9f-99fe-21655a33f813">
</p>

## Moon landing scenario 

In order to land a vessel on the surface of the moon, we first have to reach the moon. Luckily, KSP provides preset scenarios, and one of them is close to what we need. The "Mun Orbit" scenario starts at a low moon orbit. We need to decouple from the main command module, burn in retrograde to slow down, de-orbit, and begin the descent toward the moon.

**Decoupling from main command module**

The first step is to manually decouple from the main command module and take control over the lander module. Right-click on the command module (triangle-looking pod) and click on "Transfer Crew." Then, click "Transfer" next to the first crew member and finally click on the lander module.
<p align="center">
<img width="464" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/dfd88235-758b-4126-9729-ec53d4c64710">
</p>
For convenience, you can save the game after transferring the crew, so you won't have to repeat the process every time. Press the Escape key and select "Save."

The next step is to decouple from the main command module. Right-click on the decoupler and click "Decouple" (this step will be automated in our landing code).

**De-orbiting**

Once you have decoupled the lander module from the command module, you should gain control over it (the camera should be centered on the lander module). Now, we need to slow down the horizontal speed enough to de-orbit the lander module. To do this, we need to rotate 180 degrees (face the other direction) and activate the engine at full thrust for at least 30 seconds (60 seconds is best).

To rotate the vessel, turn on the SAS (Stability Assist System) and set it to retrograde mode. Press 'T' on the keyboard and click on the "Retrograde" mode next to the nav-ball. The vessel should rotate quickly.

To activate the engine, right-click on it and click "Activate." You can use the SHIFT key to increase thrust or the CTRL key to decrease thrust.

After performing these steps, you will start descending toward the moon, losing altitude and gaining vertical speed.

**Landing**

Manually landing the module from this point can be challenging. However, our code will automate this task. For now, let's try to land the module manually once. Make sure the SAS is still set to "Retrograde" mode (explained in the previous section - de-orbiting). Watch the vessel lose altitude for a while, and once you reach 10KM, start reducing speed.

Hold SHIFT at full power when you reach 10KM to slow down the vessel. You can use CTRL to decrease thrust and reduce the braking force. Play around with these parameters to land slowly. This task is not trivial and is very difficult to do manually. As mentioned earlier, we will automate this task using a PID controller.

## Automating moon landing

We will first establish a simple connection and test it by sending the vessel a simple throttle command. 
To connect to KRPC you need to start the server within the game (click “start server”) in KRPC’s window. 

```python
import krpc
# connect to KRPC server and get a reference of the vessel
conn = krpc.connect()
vessel = conn.space_center.active_vessel
# Get a reference to the vessel's engine
engine = vessel.parts.engines[0]
engine.active = True
# Sets the engine power to 0.5 out of range: [0, 1]
vessel.control.throttle = 0.5
```

After running this code, you should see that the vessel’s engine is at 0.5 capacity. 

**Troubleshooting**

If you can’t seem to connect to the server from the Python code, try changing the server’s settings in the KRPC’s window within the game.

## Getting Started
If you’ve successfully controlled the vessel’s engines, it's time to create our algorithm which will land the ship autonomously. 

First, we will use a naive approach, that does not use a PID controller. This method might work, but it won't be as robust, so expect some failures. 

Before applying any algorithm that will land the vessel, we first have to deal with some logistics steps before starting the descent. 

As explained in the last section, we first have to decouple and deorbit. We will use the `decouple_and_deorbit` function definition to deal with these steps: [decouple_and_deorbit function](https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/blob/main/helper_functions.py)

## Naive Approach 
The naive approach simply takes into account the altitude of the vessel, and according to the vertical speed sets the amount of thrust to a constant value. 

The code for the naive approach is available at: [Naive Approach Code](https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/blob/main/vessel_landing_naive.py)

Let's take a look at the results, the results show 3 parameters: Altitude (ALT), Vertical Speed (VS) and Engine Thrust (NN).
<p align="center">
<img width="578" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/a7a818af-6fbd-48bc-b22e-145133a34156">
</p>
Clearly, this approach is not efficient. The speed is jumping around and not constantly going in a downward direction. The engine jumps a lot between low and high values. 

The result of using this approach is consuming more fuel, and, by changing some values such as speed and height, the landing might fail. This landing algorithm is not robust. 

In the next section, we will solve this using a PID and a `target_vs` function.

## Implementing a PID

By using a PID, we can control the desired speed more precisely and get a smoother engine control. 

We will also define a `target_vs_function` that will get altitude and return the desired vertical speed. We will give the PID controller the difference between the current vertical speed and the output of the `target_vs_function`. 

The code for the PID Controller is available at: [PID Controller Code](https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/blob/main/PID_controller.py)

And the complete code that uses this controller and lands the vessel is at: [Complete Landing Code](https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/blob/main/vessel_landing.py)
<p align="center">
<img width="578" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/d3f7555e-86b1-489d-9847-e6f269adbafa">
</p>
We can see that the speed reduces constantly and there are no jumps in speed or thrust. 

This method results in a successful landing with more fuel, and also, we can change starting values and still get successful landings. The PID controller can see the current error and output a thrust value that takes into account the change in error. By that, we get a more robust landing procedure.

# Bonus Section - Land a Rocket SpaceX Style
Kerbal Space Program has provided us with many preset scenarios. One of those scenarios is landing a rocket back onto Earth after it has launched another vessel. This is done so we can refuel the rocket and use it again in the future!
  <p align="center">
<img width="462" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/f1ac4f0e-54bf-4605-bcae-31a21cee3644">
</p>

The landing procedure is similar to the one we practiced in the last session - landing on the moon. Feel free to try it a couple of times manually, go to scenarios and choose the “Powered Landing” scenario. You will be controlling a rocket that is falling back onto earth. Hold SHIFT to increase backward thrust and CTRL to decrease. Notice that the amount of fuel you have available is very small. 

Attempting this a few times manually will quickly show you how challenging this task can be. But don't worry, our Python script will allow the rocket to land quickly and efficiently!

Use this script: [SpaceX Landing Script](https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/blob/main/spacex_landing.py)

Execute the script within the 'Powered Landing' scenario. You will observe that the rocket descends back to Earth with no thrust initially. It's only in the final 500 meters of descent that the engines ignite, providing full thrust to decelerate the rocket. During the last 50 meters, the engine thrust gradually reduces, allowing the rocket to perform a controlled landing.
<p align="center">
<img width="595" alt="image" src="https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/assets/90526270/6d579a39-76d1-447d-ac2f-597c64c02300">
</p>
Despite significant fluctuation in engine thrust (NN) values towards the end, the vessel's speed consistently decreases.

# Bonus Section - PID simulation
In this section, we will showcase a precedure to quickly fine-tune PID parameters. Doing this manually is a fun but time-consuming process. We will use a simulation to quickly find the best parameters for our PID controller. 
Use this script: [PID Simulation Script](https://github.com/RazGavrieli/kerbal-space-program---BeresheetLanding/blob/main/pid_simulation.py)

In this script, we simulate the enviorment, setting a specific gravity value. We then initiate a vessel with Max thrust and a specific mass. Then, a PID controller is used to control the vessel's vertical speed, while the enviorment returns the current vertical speed and altitude.

Brute-forcing the PID parameters is a simple way to find the best parameters. We will use a nested for loop to iterate over the parameters and find the best ones.