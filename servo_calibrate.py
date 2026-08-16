import RPi.GPIO as GPIO
import time

PIN = 17  # change to test a different finger

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
pwm = GPIO.PWM(PIN, 50)
pwm.start(0)

print("Sweeping duty cycle. Watch the finger.")
print("Note the duty value where it stops moving or starts buzzing.\n")

try:
    for duty in [2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 12.5]:
        print(f"Duty: {duty}")
        pwm.ChangeDutyCycle(duty)
        time.sleep(1.5)
    pwm.ChangeDutyCycle(0)
except KeyboardInterrupt:
    pass
finally:
    try:
        pwm.stop()
        GPIO.cleanup()
    except:
        pass
