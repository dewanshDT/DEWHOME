import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Dynamic device pins - will be populated from database
DEVICE_PINS = {}

# Physical pin to BCM GPIO mapping
PHYSICAL_TO_BCM = {
    # Physical pin -> BCM GPIO number
    3: 2,  # GPIO2 (SDA1)
    5: 3,  # GPIO3 (SCL1)
    7: 4,  # GPIO4
    8: 14,  # GPIO14 (TXD0)
    10: 15,  # GPIO15 (RXD0)
    11: 17,  # GPIO17
    12: 18,  # GPIO18 (PWM0)
    13: 27,  # GPIO27
    15: 22,  # GPIO22
    16: 23,  # GPIO23
    18: 24,  # GPIO24
    19: 10,  # GPIO10 (MOSI)
    21: 9,  # GPIO9 (MISO)
    22: 25,  # GPIO25
    23: 11,  # GPIO11 (SCLK)
    24: 8,  # GPIO8 (CE0)
    26: 7,  # GPIO7 (CE1)
    29: 5,  # GPIO5
    31: 6,  # GPIO6
    32: 12,  # GPIO12 (PWM0)
    33: 13,  # GPIO13 (PWM1)
    35: 19,  # GPIO19 (PWM1)
    36: 16,  # GPIO16
    37: 26,  # GPIO26
    38: 20,  # GPIO20
    40: 21,  # GPIO21
}


def physical_to_bcm(physical_pin):
    """Convert physical pin number to BCM GPIO number"""
    return PHYSICAL_TO_BCM.get(physical_pin)


def setup_pins():
    """Setup GPIO pins for all devices from database"""
    from modules.db_operations import get_device_states

    global DEVICE_PINS
    device_states = get_device_states()

    # Clear existing pin mapping
    DEVICE_PINS.clear()

    # Setup pins for each device
    for device_id, device_info in device_states.items():
        physical_pin = device_info["pin"]
        bcm_pin = physical_to_bcm(physical_pin)

        if bcm_pin is None:
            print(f"Warning: Physical pin {physical_pin} cannot be mapped to BCM GPIO")
            continue

        DEVICE_PINS[device_id] = bcm_pin
        GPIO.setup(bcm_pin, GPIO.OUT)
        GPIO.output(bcm_pin, GPIO.HIGH)  # Default to OFF (inverted logic)
        print(
            f"Setup device {device_id}: Physical pin {physical_pin} -> BCM GPIO {bcm_pin}"
        )


def control_device(device_id, action):
    """Control a device by its ID"""
    if device_id not in DEVICE_PINS:
        # Try to refresh pin mapping in case new device was added
        setup_pins()

        if device_id not in DEVICE_PINS:
            raise ValueError(f"Device {device_id} not found")

    bcm_pin = DEVICE_PINS[device_id]
    print(f"Controlling device {device_id} on BCM GPIO {bcm_pin}: {action}")

    if action == "high":
        GPIO.output(
            bcm_pin, GPIO.LOW
        )  # Device ON (inverted logic for relay compatibility)
    elif action == "low":
        GPIO.output(
            bcm_pin, GPIO.HIGH
        )  # Device OFF (inverted logic for relay compatibility)
    else:
        raise ValueError("Invalid action")


def set_device_states(device_states):
    """Set GPIO pins based on the device states dictionary"""
    global DEVICE_PINS

    # Update device pins mapping
    for device_id, device_info in device_states.items():
        physical_pin = device_info["pin"]
        state = device_info["state"]
        bcm_pin = physical_to_bcm(physical_pin)

        if bcm_pin is None:
            print(f"Warning: Physical pin {physical_pin} cannot be mapped to BCM GPIO")
            continue

        DEVICE_PINS[device_id] = bcm_pin

        # Setup pin if not already done
        try:
            GPIO.setup(bcm_pin, GPIO.OUT)
            control_device(device_id, state)
        except Exception as e:
            print(f"Error setting up BCM GPIO {bcm_pin} for device {device_id}: {e}")


def get_pin_for_device(device_id):
    """Get the BCM GPIO pin number for a device"""
    return DEVICE_PINS.get(device_id)


def cleanup():
    """Cleanup GPIO resources"""
    GPIO.cleanup()
