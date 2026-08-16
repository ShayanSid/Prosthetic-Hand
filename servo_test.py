import RPi.GPIO as GPIO
import time

SERVO_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM signal at 50Hz (standard for servos)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    # Convert angle to duty cycle
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

print("Testing servo...")
set_angle(0)    # Full one way
time.sleep(1)
set_angle(90)   # Middle
time.sleep(1)
set_angle(180)  # Full other way
time.sleep(1)

try:
    pwm.stop()
    GPIO.cleanup()
except:
    pass
print("Done")
