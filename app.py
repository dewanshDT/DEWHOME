from flask import Flask, render_template, request, jsonify
import os

# Import custom modules
from modules import gpio_control
from modules import db_operations
from modules import action_scheduler

app = Flask(__name__)

# Initialize GPIO and Database
db_operations.init_db()  # Initialize the database
db_operations.create_default_device()  # Create default device if none exist
gpio_control.setup_pins()  # Set up GPIO pins

# Retrieve device states from the database and set GPIO pins accordingly
device_states = db_operations.get_device_states()
gpio_control.set_device_states(device_states)

# Start the action scheduler
action_scheduler.start_scheduler()


@app.route("/")
def index():
    devices = db_operations.get_all_devices()
    return render_template("index.html", devices=devices)


@app.route("/actions")
def actions_page():
    actions = db_operations.get_all_actions()
    return render_template("actions.html", actions=actions)


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


# === ACTION ROUTES ===


@app.route("/actions", methods=["GET"])
def get_actions():
    """Get all actions"""
    try:
        actions = db_operations.get_all_actions()
        return jsonify(actions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/actions", methods=["POST"])
def create_action():
    """Create a new action"""
    try:
        data = request.get_json()

        # Validate required fields
        name = data.get("name")
        action_type = data.get("type", "timer")
        schedule = data.get("schedule")
        parameters = data.get("parameters", {})
        device_actions = data.get("device_actions", [])

        if not name:
            return jsonify({"error": "Name is required"}), 400
        if not schedule:
            return jsonify({"error": "Schedule is required"}), 400
        if not device_actions:
            return jsonify({"error": "At least one device action is required"}), 400

        # Validate device actions
        for device_action in device_actions:
            if not device_action.get("device_id"):
                return (
                    jsonify({"error": "Device ID is required for all device actions"}),
                    400,
                )
            if not device_action.get("action_type"):
                return (
                    jsonify(
                        {"error": "Action type is required for all device actions"}
                    ),
                    400,
                )

        # Create action in database
        action_id = db_operations.add_action(
            name=name,
            action_type=action_type,
            schedule=schedule,
            parameters=parameters,
            device_actions=device_actions,
        )

        # Add to scheduler
        action = db_operations.get_action_by_id(action_id)
        action_scheduler.get_scheduler().add_action(action)

        return (
            jsonify(
                {
                    "message": f"Action '{name}' created successfully",
                    "action_id": action_id,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/actions/<int:action_id>", methods=["GET"])
def get_action(action_id):
    """Get a specific action"""
    try:
        action = db_operations.get_action_by_id(action_id)
        if not action:
            return jsonify({"error": "Action not found"}), 404
        return jsonify(action), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/actions/<int:action_id>", methods=["DELETE"])
def delete_action(action_id):
    """Delete an action"""
    try:
        # Remove from scheduler
        action_scheduler.get_scheduler().remove_action(action_id)

        # Remove from database
        db_operations.remove_action(action_id)

        return jsonify({"message": f"Action {action_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/actions/<int:action_id>/toggle", methods=["POST"])
def toggle_action(action_id):
    """Toggle action enabled/disabled state"""
    try:
        new_state = db_operations.toggle_action_enabled(action_id)

        # Update scheduler
        if new_state:
            action = db_operations.get_action_by_id(action_id)
            action_scheduler.get_scheduler().add_action(action)
        else:
            action_scheduler.get_scheduler().remove_action(action_id)

        status = "enabled" if new_state else "disabled"
        return (
            jsonify({"message": f"Action {action_id} {status}", "enabled": new_state}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/actions/<int:action_id>/execute", methods=["POST"])
def execute_action(action_id):
    """Execute an action immediately"""
    try:
        action_scheduler.get_scheduler().execute_action_now(action_id)
        return jsonify({"message": f"Action {action_id} executed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/actions/scheduler/status", methods=["GET"])
def get_scheduler_status():
    """Get scheduler status and jobs"""
    try:
        scheduler_instance = action_scheduler.get_scheduler()
        jobs = scheduler_instance.get_jobs()

        job_info = []
        for job in jobs:
            job_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                    "trigger": str(job.trigger),
                }
            )

        return jsonify({"running": scheduler_instance.running, "jobs": job_info}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001, debug=True)
    finally:
        action_scheduler.stop_scheduler()
        gpio_control.cleanup()
