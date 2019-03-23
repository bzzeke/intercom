import RPi.GPIO as GPIO
import time

DOOR_PIN = 13
CALL_BUTTON_PIN  = 21

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR_PIN, GPIO.OUT)
    GPIO.output(DOOR_PIN, 0)
    GPIO.setup(CALL_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def pulse_relay(pulse_pin, delay=2):
    GPIO.output(pulse_pin, True)
    time.sleep(delay)
    GPIO.output(pulse_pin, False)

def read(pin):
    return GPIO.input(pin)

def cleanup():
    GPIO.cleanup()

setup()
