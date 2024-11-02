from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import sqlite3
import os

app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
DEVICE_PINS = {
    1: 2,  # GPIO pin for Device 1
    2: 3,  # GPIO pin for Device 2
    3: 4,  # GPIO pin for Device 3
    4: 14   # GPIO pin for Device 4
}

for pin in DEVICE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Initialize all devices to OFF

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'device_states.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY,
            state TEXT NOT NULL
        )
    ''')
    # Initialize device states in the database
    for device_id in DEVICE_PINS.keys():
        cursor.execute('INSERT OR IGNORE INTO devices (id, state) VALUES (?, ?)', (device_id, 'low'))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    device_ids = DEVICE_PINS.keys()
    return render_template('index.html', device_ids=device_ids)

@app.route('/device', methods=['POST'])
def control_device():
    data = request.get_json()
    device_id = data.get('device_id')
    action = data.get('action')  # 'high' or 'low'

    if device_id not in DEVICE_PINS:
        return jsonify({'error': 'Invalid device ID'}), 400

    if action not in ['high', 'low']:
        return jsonify({'error': 'Invalid action'}), 400

    pin = DEVICE_PINS[device_id]

    # Control GPIO pin
    if action == 'high':
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)

    # Update device state in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE devices SET state = ? WHERE id = ?', (action, device_id))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Device {device_id} turned {action}'}), 200

@app.route('/devices', methods=['GET'])
def get_device_states():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, state FROM devices')
    devices = cursor.fetchall()
    conn.close()

    device_states = {str(device_id): state for device_id, state in devices}

    return jsonify(device_states), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
