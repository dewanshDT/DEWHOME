from flask import Flask, render_template, request, jsonify
import os

# Import custom modules
from modules import gpio_control
from modules import db_operations

app = Flask(__name__)

# Device list
DEVICES = [
    {'id': 1, 'name': 'Bulb 1', 'icon': 'fa-lightbulb'},
    {'id': 2, 'name': 'Bulb 2', 'icon': 'fa-lightbulb'},
    {'id': 3, 'name': 'Fan', 'icon': 'fa-fan'},
    {'id': 4, 'name': 'Device 4', 'icon': 'fa-plug'}
]

# Extract DEVICE_IDS from DEVICES
DEVICE_IDS = [device['id'] for device in DEVICES]


# Initialize GPIO and Database
gpio_control.setup_pins()                     # Set up GPIO pins
db_operations.init_db()                       # Initialize the database
db_operations.initialize_device_states(DEVICE_IDS)  # Ensure all devices are in the database

# Retrieve device states from the database and set GPIO pins accordingly
device_states = db_operations.get_device_states()
gpio_control.set_device_states(device_states)

@app.route('/')
def index():
     return render_template('index.html', devices=DEVICES)

@app.route('/device', methods=['POST'])
def control_device():
    data = request.get_json()
    device_id = data.get('device_id')
    action = data.get('action')  # 'high' or 'low'

    try:
        device_id = int(device_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid device ID'}), 400

    if device_id not in DEVICE_IDS:
        return jsonify({'error': 'Invalid device ID'}), 400

    if action not in ['high', 'low']:
        return jsonify({'error': 'Invalid action'}), 400

    try:
        gpio_control.control_device(device_id, action)
        db_operations.update_device_state(device_id, action)
        return jsonify({'message': f'Device {device_id} turned {action}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/devices', methods=['GET'])
def get_device_states():
    device_states = db_operations.get_device_states()
    return jsonify(device_states), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        gpio_control.cleanup()
