import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
DEVICE_PINS = {
    1: 17,  # GPIO pin for Device 1
    2: 18,  # GPIO pin for Device 2
    3: 27,  # GPIO pin for Device 3
    4: 22   # GPIO pin for Device 4
}

def setup_pins():
    for pin in DEVICE_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Default to OFF

def control_device(device_id, action):
    if device_id not in DEVICE_PINS:
        raise ValueError("Invalid device ID")
    pin = DEVICE_PINS[device_id]
    print(action, device_id)
    if action == 'high':
        GPIO.output(pin, GPIO.LOW) # for dealing with wrong wiring
    elif action == 'low':
        GPIO.output(pin, GPIO.HIGH) # for dealing with wrong wiring
    else:
        raise ValueError("Invalid action")

def set_device_states(device_states):
    """
    Set GPIO pins based on the device states dictionary.
    device_states: dict with keys as device IDs and values as 'high' or 'low'
    """
    for device_id, state in device_states.items():
        if device_id in DEVICE_PINS:
            control_device(device_id, state)

def cleanup():
    GPIO.cleanup()
