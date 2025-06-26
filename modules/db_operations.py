import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "device_states.db"
)


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                state TEXT NOT NULL
            )
        """
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        if conn:
            conn.close()


def initialize_device_states(device_ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for device_id in device_ids:
        cursor.execute(
            "INSERT OR IGNORE INTO devices (id, state) VALUES (?, ?)",
            (device_id, "low"),
        )
    conn.commit()
    conn.close()


def update_device_state(device_id, state):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE devices SET state = ? WHERE id = ?", (state, device_id))
    conn.commit()
    conn.close()


def get_device_states():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, state FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return {device_id: state for device_id, state in devices}
