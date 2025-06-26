from flask import Flask, render_template, request, jsonify
import os

# Import custom modules
from modules import gpio_control
from modules import db_operations

app = Flask(__name__)

# Initialize GPIO and Database
db_operations.init_db()  # Initialize the database
db_operations.create_default_device()  # Create default device if none exist
gpio_control.setup_pins()  # Set up GPIO pins

# Retrieve device states from the database and set GPIO pins accordingly
device_states = db_operations.get_device_states()
gpio_control.set_device_states(device_states)


@app.route("/")
def index():
    devices = db_operations.get_all_devices()
    return render_template("index.html", devices=devices)


@app.route("/device", methods=["POST"])
def control_device():
    data = request.get_json()
    device_id = data.get("device_id")
    action = data.get("action")  # 'high' or 'low'

    try:
        device_id = int(device_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid device ID"}), 400

    if action not in ["high", "low"]:
        return jsonify({"error": "Invalid action"}), 400

    try:
        gpio_control.control_device(device_id, action)
        db_operations.update_device_state(device_id, action)
        return jsonify({"message": f"Device {device_id} turned {action}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/devices", methods=["GET"])
def get_device_states():
    devices = db_operations.get_all_devices()
    return jsonify(devices), 200


@app.route("/devices", methods=["POST"])
def add_device():
    data = request.get_json()
    name = data.get("name")
    icon = data.get("icon", "fa-plug")
    pin_number = data.get("pin_number")

    if not name or not pin_number:
        return jsonify({"error": "Name and pin number are required"}), 400

    try:
        pin_number = int(pin_number)
        device_id = db_operations.add_device(name, icon, pin_number)

        # Refresh GPIO setup to include new device
        gpio_control.setup_pins()

        return (
            jsonify(
                {
                    "message": f"Device '{name}' added successfully",
                    "device_id": device_id,
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/devices/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    try:
        db_operations.remove_device(device_id)

        # Refresh GPIO setup to remove deleted device
        gpio_control.setup_pins()

        return jsonify({"message": f"Device {device_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/pins", methods=["GET"])
def get_pins():
    pins = db_operations.get_available_pins()
    return jsonify(pins), 200


@app.route("/pins/usable", methods=["GET"])
def get_usable_pins():
    pins = db_operations.get_usable_pins()
    return jsonify(pins), 200


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001, debug=True)
    finally:
        gpio_control.cleanup()
