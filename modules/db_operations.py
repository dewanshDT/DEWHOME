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
