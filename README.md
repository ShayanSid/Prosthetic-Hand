##### VISION-ASSISTED PROSTHETIC HAND CONTROLLER

A low cost prosthetic hand that uses a camera to identify the object in front of it and automatically select the appropriate grip type. The user triggers the action with a single button press, and the system handles grip selection. 
The goal is to reduce the cognitive and physical effort of operating a prosthetic hand. Rather than requiring the user to manually cycle through grip modes, the camera does the classification and the user only confirms. 

##### HOW IT WORKS

Pi Camera Control (capture) --> YOLOv8 Nano + button press (detect) --> Grip Map (decide) --> Servo

1. The user press the pushbutton, opening a scanning window (up to 3 seconds)
2. The Pi camera captures the frames and YOLOv8 Nano runs inference on each one
3. When a detection clears the confidence threshold, the object class is looked up in GRIP_MAP and mapped to one of five grip types
4. The five servos move to that grip's preset positions and hold under active PWM signal
5. A second button press releases the grip and returns the hand to open.

The key design decision is that the system doesn't need to know what an object is and only what shape of grasp it requires. A bottle detected as a vase still maps to a power grip, so label ambiguity in the model doesn't break the behavior

##### GRIP TYPES

| Object class | Grip | Description |
| --- | --- | --- |
| bottle, vase, scissors | Power | All five fingers wrap |
| cup | Palmar | Four fingers oppose thumb |
| fork, knife, spoon | Lateral | Thumb against side of index |
| cell phone, book , remote | Flat | Fingers extended |
| toothbrush, pen | Pinch | Thumb and index only |

##### HARDWARE

| Component | Notes |
| --- | --- |
| Raspberry Pi 4 (2GB) | Runs detection and servo control, and headless over SSH |
| Pi Camera Module V2 | 8MP, IMX219 sensor, CSI ribbon connection |
| MG90S micro servos x5 | One per finger ~180 degrees range |
| Pushbutton | User trigger |
| Breadboard + jumper wires | Signal routing | 
| 5V 2A + external supply | Dedicated servo power, shared ground with Pi |
| InMoov Hand i2 (3D printed) | PLA, printed on an Anycubic i3 Mega | 

##### GPIO assignments

| Signal | BCM | Physical pin | 
| --- | --- | --- | 
| Servo 1 | GPIO 17 | 11 |
| Servo 2 | GPIO 18 | 12 |
| Servo 3 | GPIO 27 | 13 |
| Servo 4 | GPIO 22 | 15 |
| Servo 5 | GPIO 23 | 16 |
| Button | GPIO 24 | 18 |
| Ground | - | 6 |

Servos are powered from an external 5V supply rather than the Pi's 5V pin. The Pi's regulator also feeds the CPU and camera leaves roughly 1A of headroom, which five servos can exceed under load and cause brownouts. The external supply's ground needs to share the Pi's ground rail so the PWM signal has a common reference. 

##### Setup

On the Pi:

pip install opencv-python ultralytics --break-system-packages --no-cache-dir
sudo apt install -y python3-picamera2

##### Running 

python prosthetic_main.py

| Script | Purpose | 
| --- | --- | 
| prosthetic_main.py | Full integrated system | 
| servo_test.py | Single servo sweep |
| servo_test_all.py | All five servos in sequence |
| servo_calibrate.py | Duty cycle sweep to find real endpoints |
| button_test.py | Verify button wiring |

##### CURRENT STATUS

Working: the detection pipeline, grip mapping, button input, and servo actuation all function end to end. Pressing the button triggers a scan, the correct grip is selected, and the servos execute and hold it. 

Unfinished: the tendon linkage doesn't retract enough line to fully curl the printed fingers

##### Known limitations 

- Detection depends on the background. Cluttered backgrounds split the model's confidence across multiple objects and no single detection clears the threshold. Plain backgrounds work reliably
- ~1 FPS on the Pi, compared to ~35 FPS on a laptop
- Some objects detect poorly. Black phones in black cases and opaque dark bottles are misread. This is a limitation of YOLOv8 Nano's training data
- The confidence threshold is set to 0.50, to improve the hit rate. The grip map absorbs most label ambiguity, so a slightly wrong label usually still yields the right grip 
