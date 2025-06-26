import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Dynamic device pins - will be populated from database
DEVICE_PINS = {}


def setup_pins():
    """Setup GPIO pins for all devices from database"""
    from modules.db_operations import get_device_states

    global DEVICE_PINS
    device_states = get_device_states()

    # Clear existing pin mapping
    DEVICE_PINS.clear()

    # Setup pins for each device
    for device_id, device_info in device_states.items():
        pin_number = device_info["pin"]
        DEVICE_PINS[device_id] = pin_number
        GPIO.setup(pin_number, GPIO.OUT)
        GPIO.output(pin_number, GPIO.HIGH)  # Default to OFF (inverted logic)


def control_device(device_id, action):
    """Control a device by its ID"""
    if device_id not in DEVICE_PINS:
        # Try to refresh pin mapping in case new device was added
        setup_pins()

        if device_id not in DEVICE_PINS:
            raise ValueError(f"Device {device_id} not found")

    pin = DEVICE_PINS[device_id]
    print(f"Controlling device {device_id} on pin {pin}: {action}")

    if action == "high":
        GPIO.output(pin, GPIO.LOW)  # Device ON (inverted logic for relay compatibility)
    elif action == "low":
        GPIO.output(
            pin, GPIO.HIGH
        )  # Device OFF (inverted logic for relay compatibility)
    else:
        raise ValueError("Invalid action")


def set_device_states(device_states):
    """Set GPIO pins based on the device states dictionary"""
    global DEVICE_PINS

    # Update device pins mapping
    for device_id, device_info in device_states.items():
        pin_number = device_info["pin"]
        state = device_info["state"]

        DEVICE_PINS[device_id] = pin_number

        # Setup pin if not already done
        try:
            GPIO.setup(pin_number, GPIO.OUT)
            control_device(device_id, state)
        except Exception as e:
            print(f"Error setting up pin {pin_number} for device {device_id}: {e}")


def get_pin_for_device(device_id):
    """Get the GPIO pin number for a device"""
    return DEVICE_PINS.get(device_id)


def cleanup():
    """Cleanup GPIO resources"""
    GPIO.cleanup()
