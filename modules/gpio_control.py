import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
DEVICE_PINS = {
    1: 17,  # GPIO pin for Device 1
    2: 18,  # GPIO pin for Device 2
    3: 27,  # GPIO pin for Device 3
    4: 22   # GPIO pin for Device 4
}

def setup_pins():
    for pin in DEVICE_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Initialize all devices to OFF

def control_device(device_id, action):
    if device_id not in DEVICE_PINS:
        raise ValueError("Invalid device ID")
    pin = DEVICE_PINS[device_id]
    if action == 'high':
        GPIO.output(pin, GPIO.HIGH)
    elif action == 'low':
        GPIO.output(pin, GPIO.LOW)
    else:
        raise ValueError("Invalid action")

def cleanup():
    GPIO.cleanup()
