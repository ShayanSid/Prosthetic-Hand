import RPi.GPIO as GPIO
import time

BUTTON_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Press the button (Ctrl+C to stop)...")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Button pressed!")
            time.sleep(0.3)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Done")
