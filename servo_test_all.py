import RPi.GPIO as GPIO
import time

SERVO_PINS = [17, 18, 27, 22, 23]

GPIO.setmode(GPIO.BCM)

pwms = []
for pin in SERVO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 50)
    pwm.start(0)
    pwms.append(pwm)

def set_angle(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

print("Testing all 5 servos one at a time...")

for i, pwm in enumerate(pwms):
    print(f"Servo {i+1} (GPIO {SERVO_PINS[i]})")
    set_angle(pwm, 0)
    time.sleep(0.5)
    set_angle(pwm, 90)
    time.sleep(0.5)
    set_angle(pwm, 180)
    time.sleep(0.5)

try:
    for pwm in pwms:
        pwm.stop()
    GPIO.cleanup()
except:
    pass

print("Done")
