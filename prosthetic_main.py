from ultralytics import YOLO
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time

# ---------- Setup ----------

model = YOLO("yolov8n.pt")

GRIP_MAP = {
    "bottle": "power",
    "vase": "power",
    "cup": "palmar",
    "fork": "lateral",
    "knife": "lateral",
    "spoon": "lateral",
    "cell phone": "flat",
    "book": "flat",
    "scissors": "power",
    "remote": "flat",
    "toothbrush": "pinch",
    "pen": "pinch",
}

CONFIDENCE_THRESHOLD = 0.50
BUTTON_PIN = 24
SERVO_PINS = [17, 18, 27, 22, 23]

# Servo angle presets for each grip type — placeholder values for now,
# will tune these once servos are attached to fingers
GRIP_ANGLES = {
    "power":   [180, 180, 180, 180, 180],
    "palmar":  [150, 150, 150, 150, 90],
    "lateral": [180, 180, 0, 0, 0],
    "flat":    [0, 0, 0, 0, 0],
    "pinch":   [180, 180, 0, 0, 0],
}

SCAN_TIMEOUT = 3.0  # max seconds to keep trying for a confident detection

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwms = []
for pin in SERVO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 50)
    pwm.start(0)
    pwms.append(pwm)

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# ---------- Functions ----------

def angle_to_duty(angle):
    return 2 + (angle / 18)

def execute_grip(grip_name):
    angles = GRIP_ANGLES.get(grip_name)
    if not angles:
        return
    print(f"Executing {grip_name} grip...")
    for pwm, angle in zip(pwms, angles):
        pwm.ChangeDutyCycle(angle_to_duty(angle))
    time.sleep(0.5)
    # Signal stays active — servos hold their position under load

def release_grip():
    print("Releasing grip...")
    for pwm in pwms:
        pwm.ChangeDutyCycle(angle_to_duty(0))
    time.sleep(0.5)
    for pwm in pwms:
        pwm.ChangeDutyCycle(0)

def scan_one_frame():
    frame = picam2.capture_array()
    results = model(frame, verbose=False)

    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls)]
            confidence = float(box.conf)
            print(f"Saw: {label} ({confidence:.0%})")

            if confidence >= CONFIDENCE_THRESHOLD:
                grip = GRIP_MAP.get(label, None)
                if grip:
                    print(f"Detected: {label} ({confidence:.0%}) → {grip} grip")
                    return grip
    return None

def scan_until_confident_or_timeout():
    """
    Keeps scanning frames as long as either:
    - the button is still being held, OR
    - we're still within the timeout window
    Stops early the moment a confident detection is found.
    This lets the user release the button early without stopping the scan.
    """
    start_time = time.time()

    while True:
        grip = scan_one_frame()
        if grip:
            return grip

        elapsed = time.time() - start_time
        button_still_held = (GPIO.input(BUTTON_PIN) == GPIO.LOW)

        if elapsed >= SCAN_TIMEOUT:
            return None
        if not button_still_held and elapsed >= 0.5:
            # Give at least one real chance even if released instantly,
            # but don't scan forever once released past a short grace period
            return None

# ---------- Main loop ----------
# Tap-to-scan (hold briefly if needed), tap-to-release design:
# First press -> scan for up to SCAN_TIMEOUT seconds, can release early once
#                 a detection is found or after a short grace period
# Second press (while holding a grip) -> release grip, reset for next scan

print("System ready. Press the button to scan. Press again to release a grip.")

grip_holding = False
button_was_pressed = False

try:
    while True:
        button_is_pressed = (GPIO.input(BUTTON_PIN) == GPIO.LOW)

        # Detect the moment the button goes from not-pressed to pressed
        if button_is_pressed and not button_was_pressed:
            if not grip_holding:
                print("Button pressed — scanning...")
                grip = scan_until_confident_or_timeout()
                if grip:
                    execute_grip(grip)
                    grip_holding = True
                else:
                    print("No confident detection — try again")
            else:
                release_grip()
                grip_holding = False

        button_was_pressed = button_is_pressed
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Shutting down...")
    for pwm in pwms:
        pwm.stop()
    GPIO.cleanup()
    picam2.stop()
