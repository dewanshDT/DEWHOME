import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "device_states.db"
)

# GPIO Pin definitions with categories
GPIO_PINS = {
    1: {
        "type": "3.3V",
        "category": "power",
        "capabilities": ["power"],
        "description": "3.3V Power",
    },
    2: {
        "type": "5V",
        "category": "power",
        "capabilities": ["power"],
        "description": "5V Power",
    },
    3: {
        "type": "GPIO2",
        "category": "i2c",
        "capabilities": ["input", "output", "i2c"],
        "description": "GPIO2 (SDA1)",
    },
    4: {
        "type": "5V",
        "category": "power",
        "capabilities": ["power"],
        "description": "5V Power",
    },
    5: {
        "type": "GPIO3",
        "category": "i2c",
        "capabilities": ["input", "output", "i2c"],
        "description": "GPIO3 (SCL1)",
    },
    6: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    7: {
        "type": "GPIO4",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO4",
    },
    8: {
        "type": "GPIO14",
        "category": "uart",
        "capabilities": ["input", "output", "uart"],
        "description": "GPIO14 (TXD0)",
    },
    9: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    10: {
        "type": "GPIO15",
        "category": "uart",
        "capabilities": ["input", "output", "uart"],
        "description": "GPIO15 (RXD0)",
    },
    11: {
        "type": "GPIO17",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO17",
    },
    12: {
        "type": "GPIO18",
        "category": "gpio",
        "capabilities": ["input", "output", "pwm"],
        "description": "GPIO18 (PWM0)",
    },
    13: {
        "type": "GPIO27",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO27",
    },
    14: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    15: {
        "type": "GPIO22",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO22",
    },
    16: {
        "type": "GPIO23",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO23",
    },
    17: {
        "type": "3.3V",
        "category": "power",
        "capabilities": ["power"],
        "description": "3.3V Power",
    },
    18: {
        "type": "GPIO24",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO24",
    },
    19: {
        "type": "GPIO10",
        "category": "spi",
        "capabilities": ["input", "output", "spi"],
        "description": "GPIO10 (MOSI)",
    },
    20: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    21: {
        "type": "GPIO9",
        "category": "spi",
        "capabilities": ["input", "output", "spi"],
        "description": "GPIO9 (MISO)",
    },
    22: {
        "type": "GPIO25",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO25",
    },
    23: {
        "type": "GPIO11",
        "category": "spi",
        "capabilities": ["input", "output", "spi"],
        "description": "GPIO11 (SCLK)",
    },
    24: {
        "type": "GPIO8",
        "category": "spi",
        "capabilities": ["input", "output", "spi"],
        "description": "GPIO8 (CE0)",
    },
    25: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    26: {
        "type": "GPIO7",
        "category": "spi",
        "capabilities": ["input", "output", "spi"],
        "description": "GPIO7 (CE1)",
    },
    27: {
        "type": "ID_SD",
        "category": "special",
        "capabilities": ["i2c"],
        "description": "ID_SD (EEPROM)",
    },
    28: {
        "type": "ID_SC",
        "category": "special",
        "capabilities": ["i2c"],
        "description": "ID_SC (EEPROM)",
    },
    29: {
        "type": "GPIO5",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO5",
    },
    30: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    31: {
        "type": "GPIO6",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO6",
    },
    32: {
        "type": "GPIO12",
        "category": "gpio",
        "capabilities": ["input", "output", "pwm"],
        "description": "GPIO12 (PWM0)",
    },
    33: {
        "type": "GPIO13",
        "category": "gpio",
        "capabilities": ["input", "output", "pwm"],
        "description": "GPIO13 (PWM1)",
    },
    34: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    35: {
        "type": "GPIO19",
        "category": "gpio",
        "capabilities": ["input", "output", "pwm"],
        "description": "GPIO19 (PWM1)",
    },
    36: {
        "type": "GPIO16",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO16",
    },
    37: {
        "type": "GPIO26",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO26",
    },
    38: {
        "type": "GPIO20",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO20",
    },
    39: {
        "type": "GND",
        "category": "ground",
        "capabilities": ["ground"],
        "description": "Ground",
    },
    40: {
        "type": "GPIO21",
        "category": "gpio",
        "capabilities": ["input", "output"],
        "description": "GPIO21",
    },
}


def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create GPIO pins table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gpio_pins (
                pin_number INTEGER PRIMARY KEY,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                description TEXT NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create devices table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icon TEXT NOT NULL DEFAULT 'fa-plug',
                pin_number INTEGER NOT NULL,
                state TEXT NOT NULL DEFAULT 'low',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pin_number) REFERENCES gpio_pins (pin_number)
            )
        """
        )

        # Create actions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'timer',
                schedule TEXT NOT NULL,
                parameters TEXT DEFAULT '{}',
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                next_run TIMESTAMP
            )
        """
        )

        # Create action_devices table (many-to-many relationship)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                action_type TEXT NOT NULL DEFAULT 'toggle',
                delay_seconds INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (action_id) REFERENCES actions (id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
            )
        """
        )

        # Create action_logs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'success',
                message TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (action_id) REFERENCES actions (id) ON DELETE CASCADE
            )
        """
        )

        # Insert GPIO pins data
        for pin_number, pin_data in GPIO_PINS.items():
            cursor.execute(
                """
                INSERT OR IGNORE INTO gpio_pins 
                (pin_number, type, category, capabilities, description) 
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    pin_number,
                    pin_data["type"],
                    pin_data["category"],
                    ",".join(pin_data["capabilities"]),
                    pin_data["description"],
                ),
            )

        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        if conn:
            conn.close()


def get_available_pins():
    """Get all available GPIO pins with their information"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT pin_number, type, category, capabilities, description, is_used 
        FROM gpio_pins 
        ORDER BY pin_number
    """
    )
    pins = cursor.fetchall()
    conn.close()

    return [
        {
            "pin_number": pin[0],
            "type": pin[1],
            "category": pin[2],
            "capabilities": pin[3].split(","),
            "description": pin[4],
            "is_used": bool(pin[5]),
        }
        for pin in pins
    ]


def get_usable_pins():
    """Get pins that can be used for devices"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT pin_number, type, category, capabilities, description 
        FROM gpio_pins 
        WHERE (category = 'gpio' OR category = 'spi' OR category = 'uart' OR category = 'i2c') 
        AND is_used = FALSE
        AND capabilities LIKE '%output%'
        ORDER BY 
            CASE category 
                WHEN 'gpio' THEN 1 
                WHEN 'spi' THEN 2 
                WHEN 'uart' THEN 3 
                WHEN 'i2c' THEN 4 
            END, pin_number
    """
    )
    pins = cursor.fetchall()
    conn.close()

    return [
        {
            "pin_number": pin[0],
            "type": pin[1],
            "category": pin[2],
            "capabilities": pin[3].split(","),
            "description": pin[4],
        }
        for pin in pins
    ]


def add_device(name, icon, pin_number):
    """Add a new device"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if pin is available
        cursor.execute(
            "SELECT is_used FROM gpio_pins WHERE pin_number = ?", (pin_number,)
        )
        pin_status = cursor.fetchone()

        if not pin_status:
            raise ValueError(f"Pin {pin_number} does not exist")

        if pin_status[0]:
            raise ValueError(f"Pin {pin_number} is already in use")

        # Insert device
        cursor.execute(
            """
            INSERT INTO devices (name, icon, pin_number, state) 
            VALUES (?, ?, ?, 'low')
        """,
            (name, icon, pin_number),
        )

        # Mark pin as used
        cursor.execute(
            """
            UPDATE gpio_pins SET is_used = TRUE WHERE pin_number = ?
        """,
            (pin_number,),
        )

        device_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return device_id

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def remove_device(device_id):
    """Remove a device and free its pin"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get the pin number before deleting
        cursor.execute("SELECT pin_number FROM devices WHERE id = ?", (device_id,))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Device {device_id} does not exist")

        pin_number = result[0]

        # Delete device
        cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))

        # Mark pin as unused
        cursor.execute(
            """
            UPDATE gpio_pins SET is_used = FALSE WHERE pin_number = ?
        """,
            (pin_number,),
        )

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def get_all_devices():
    """Get all devices with their pin information"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT d.id, d.name, d.icon, d.pin_number, d.state, d.created_at,
               p.type, p.category, p.description
        FROM devices d
        JOIN gpio_pins p ON d.pin_number = p.pin_number
        ORDER BY d.id
    """
    )
    devices = cursor.fetchall()
    conn.close()

    return [
        {
            "id": device[0],
            "name": device[1],
            "icon": device[2],
            "pin_number": device[3],
            "state": device[4],
            "created_at": device[5],
            "pin_type": device[6],
            "pin_category": device[7],
            "pin_description": device[8],
        }
        for device in devices
    ]


def get_device_states():
    """Get device states for GPIO control"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, pin_number, state FROM devices")
    devices = cursor.fetchall()
    conn.close()

    return {device[0]: {"pin": device[1], "state": device[2]} for device in devices}


def update_device_state(device_id, state):
    """Update device state"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE devices 
        SET state = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """,
        (state, device_id),
    )
    conn.commit()
    conn.close()


def create_default_device():
    """Create a default device if no devices exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if any devices exist
    cursor.execute("SELECT COUNT(*) FROM devices")
    device_count = cursor.fetchone()[0]

    if device_count == 0:
        # Find first available GPIO pin
        cursor.execute(
            """
            SELECT pin_number FROM gpio_pins 
            WHERE category = 'gpio' AND is_used = FALSE 
            ORDER BY pin_number LIMIT 1
        """
        )
        available_pin = cursor.fetchone()

        if available_pin:
            pin_number = available_pin[0]
            cursor.execute(
                """
                INSERT INTO devices (name, icon, pin_number, state) 
                VALUES (?, ?, ?, 'low')
            """,
                ("Default Device", "fa-plug", pin_number),
            )

            cursor.execute(
                """
                UPDATE gpio_pins SET is_used = TRUE WHERE pin_number = ?
            """,
                (pin_number,),
            )

            conn.commit()
            print(f"Created default device on pin {pin_number}")

    conn.close()


# === ACTION MANAGEMENT FUNCTIONS ===


def add_action(name, action_type, schedule, parameters, device_actions):
    """Add a new action with associated devices"""
    import json

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insert action
        cursor.execute(
            """
            INSERT INTO actions (name, type, schedule, parameters, enabled) 
            VALUES (?, ?, ?, ?, TRUE)
            """,
            (name, action_type, schedule, json.dumps(parameters)),
        )

        action_id = cursor.lastrowid

        # Insert action_devices
        for device_action in device_actions:
            cursor.execute(
                """
                INSERT INTO action_devices (action_id, device_id, action_type, delay_seconds)
                VALUES (?, ?, ?, ?)
                """,
                (
                    action_id,
                    device_action["device_id"],
                    device_action["action_type"],
                    device_action.get("delay_seconds", 0),
                ),
            )

        conn.commit()
        conn.close()

        return action_id

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def get_all_actions():
    """Get all actions with their devices"""
    import json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all actions
    cursor.execute(
        """
        SELECT id, name, type, schedule, parameters, enabled, created_at, last_run, next_run
        FROM actions
        ORDER BY created_at DESC
        """
    )
    actions = cursor.fetchall()

    result = []
    for action in actions:
        action_id = action[0]

        # Get devices for this action
        cursor.execute(
            """
            SELECT ad.device_id, ad.action_type, ad.delay_seconds, d.name, d.icon
            FROM action_devices ad
            JOIN devices d ON ad.device_id = d.id
            WHERE ad.action_id = ?
            ORDER BY ad.delay_seconds
            """,
            (action_id,),
        )
        devices = cursor.fetchall()

        result.append(
            {
                "id": action[0],
                "name": action[1],
                "type": action[2],
                "schedule": action[3],
                "parameters": json.loads(action[4]) if action[4] else {},
                "enabled": bool(action[5]),
                "created_at": action[6],
                "last_run": action[7],
                "next_run": action[8],
                "devices": [
                    {
                        "device_id": device[0],
                        "action_type": device[1],
                        "delay_seconds": device[2],
                        "device_name": device[3],
                        "device_icon": device[4],
                    }
                    for device in devices
                ],
            }
        )

    conn.close()
    return result


def get_action_by_id(action_id):
    """Get a specific action by ID"""
    import json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, type, schedule, parameters, enabled, created_at, last_run, next_run
        FROM actions
        WHERE id = ?
        """,
        (action_id,),
    )
    action = cursor.fetchone()

    if not action:
        conn.close()
        return None

    # Get devices for this action
    cursor.execute(
        """
        SELECT ad.device_id, ad.action_type, ad.delay_seconds, d.name, d.icon
        FROM action_devices ad
        JOIN devices d ON ad.device_id = d.id
        WHERE ad.action_id = ?
        ORDER BY ad.delay_seconds
        """,
        (action_id,),
    )
    devices = cursor.fetchall()

    result = {
        "id": action[0],
        "name": action[1],
        "type": action[2],
        "schedule": action[3],
        "parameters": json.loads(action[4]) if action[4] else {},
        "enabled": bool(action[5]),
        "created_at": action[6],
        "last_run": action[7],
        "next_run": action[8],
        "devices": [
            {
                "device_id": device[0],
                "action_type": device[1],
                "delay_seconds": device[2],
                "device_name": device[3],
                "device_icon": device[4],
            }
            for device in devices
        ],
    }

    conn.close()
    return result


def remove_action(action_id):
    """Remove an action and all its associated devices"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if action exists
        cursor.execute("SELECT id FROM actions WHERE id = ?", (action_id,))
        if not cursor.fetchone():
            raise ValueError(f"Action {action_id} does not exist")

        # Delete action (CASCADE will handle action_devices and action_logs)
        cursor.execute("DELETE FROM actions WHERE id = ?", (action_id,))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def toggle_action_enabled(action_id):
    """Toggle action enabled state"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get current state
        cursor.execute("SELECT enabled FROM actions WHERE id = ?", (action_id,))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Action {action_id} does not exist")

        new_state = not bool(result[0])

        # Update state
        cursor.execute(
            """
            UPDATE actions 
            SET enabled = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (new_state, action_id),
        )

        conn.commit()
        conn.close()

        return new_state

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def update_action_schedule(action_id, next_run):
    """Update action's next run time"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE actions 
            SET next_run = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (next_run, action_id),
        )

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def log_action_execution(action_id, status, message=None):
    """Log action execution"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO action_logs (action_id, status, message)
            VALUES (?, ?, ?)
            """,
            (action_id, status, message),
        )

        # Update action's last_run time
        cursor.execute(
            """
            UPDATE actions 
            SET last_run = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (action_id,),
        )

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise


def get_enabled_actions():
    """Get all enabled actions for scheduler"""
    import json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, type, schedule, parameters
        FROM actions
        WHERE enabled = TRUE
        ORDER BY id
        """
    )
    actions = cursor.fetchall()

    result = []
    for action in actions:
        action_id = action[0]

        # Get devices for this action
        cursor.execute(
            """
            SELECT device_id, action_type, delay_seconds
            FROM action_devices
            WHERE action_id = ?
            ORDER BY delay_seconds
            """,
            (action_id,),
        )
        devices = cursor.fetchall()

        result.append(
            {
                "id": action[0],
                "name": action[1],
                "type": action[2],
                "schedule": action[3],
                "parameters": json.loads(action[4]) if action[4] else {},
                "devices": [
                    {
                        "device_id": device[0],
                        "action_type": device[1],
                        "delay_seconds": device[2],
                    }
                    for device in devices
                ],
            }
        )

    conn.close()
    return result
