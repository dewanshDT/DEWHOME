# DEWHOME: Raspberry Pi Zero W Home Automation System

DEWHOME is a lightweight home automation system designed to run on a Raspberry Pi Zero W. It allows you to control devices connected to the Raspberry Pi's GPIO pins through a web interface with **dynamic device management**. The application uses Flask for the web server, Gunicorn as the WSGI server, and Nginx as a reverse proxy to handle client requests efficiently.

## 🚀 New Features (v2.0)

- **Dynamic Device Management**: Add and remove devices through the web interface
- **Smart GPIO Pin Selection**: Automatic pin categorization with warnings for special pins
- **Real-time Pin Validation**: Prevents conflicts and provides usage warnings
- **Modern Modal Interface**: Clean, responsive modals for device management
- **Database-Driven Configuration**: All device and pin data stored in SQLite
- **Pin Category System**: GPIO, I2C, UART, SPI pins with appropriate warnings

## Table of Contents

- [DEWHOME: Raspberry Pi Zero W Home Automation System](#dewhome-raspberry-pi-zero-w-home-automation-system)
  - [🚀 New Features (v2.0)](#-new-features-v20)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [GPIO Pin Categories](#gpio-pin-categories)
  - [Prerequisites](#prerequisites)
  - [GPIO Access Setup](#gpio-access-setup)
  - [Installation](#installation)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Set Up the Virtual Environment](#2-set-up-the-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Configure the Application](#4-configure-the-application)
    - [5. Set Database Permissions](#5-set-database-permissions)
  - [Setting Up Gunicorn](#setting-up-gunicorn)
  - [Setting Up Nginx](#setting-up-nginx)
  - [Configuring Systemd Service](#configuring-systemd-service)
  - [Running the Application](#running-the-application)
  - [Accessing the Web Interface](#accessing-the-web-interface)
  - [Using the Device Management Interface](#using-the-device-management-interface)
  - [Project Structure](#project-structure)
  - [Important Notes and Known Issues](#important-notes-and-known-issues)
  - [Troubleshooting](#troubleshooting)
  - [API Endpoints](#api-endpoints)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Dynamic Device Control**: Add, remove, and control devices through the web interface
- **Smart Pin Management**: Automatic GPIO pin categorization and conflict prevention
- **Responsive Design**: Optimized for both desktop and mobile devices
- **Dark Mode UI**: Modern dark theme for comfortable use in low-light conditions
- **Device Icons and Names**: Customize device names and icons for easy identification
- **Persistent States**: Device states are stored in a SQLite database
- **Real-time Validation**: Pin usage validation with warnings for special pins
- **Secure and Efficient**: Uses Gunicorn and Nginx for robust performance

## GPIO Pin Categories

The system automatically categorizes all 40 GPIO pins:

- **GPIO Pins** (Recommended): Standard GPIO pins safe for general use
- **I2C Pins** (Pin 3, 5): Used for I2C communication - warns if not needed
- **UART Pins** (Pin 8, 10): Used for serial communication - warns if console disabled
- **SPI Pins** (Pin 19, 21, 23, 24, 26): Used for SPI communication - warns if not needed
- **Power/Ground Pins**: Automatically excluded from device selection

## Prerequisites

- **Hardware**: Raspberry Pi Zero W (or compatible model) with GPIO-accessible devices connected.
- **Operating System**: Raspberry Pi OS Lite (or a similar Debian-based distribution).
- **Internet Connection**: Required for installing packages and dependencies.
- **Python**: Version 3.7 or higher installed on the Raspberry Pi.

## GPIO Access Setup

**Important**: Before installing DEWHOME, you need to ensure proper GPIO access permissions. This is crucial for the application to control GPIO pins.

### 1. Add User to GPIO Group

Add your user (typically `pi`) to the `gpio` group to grant GPIO access:

```bash
sudo usermod -a -G gpio pi
```

### 2. Create GPIO Rules (Optional but Recommended)

Create a udev rule to ensure GPIO access without requiring sudo:

```bash
sudo nano /etc/udev/rules.d/99-gpio.rules
```

Add the following content:

```
SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
```

### 3. Enable GPIO Interface

Enable the GPIO interface in Raspberry Pi configuration:

```bash
sudo raspi-config
```

Navigate to:

- **Interface Options** → **GPIO** → **Yes** to enable GPIO

Alternatively, you can enable it via command line:

```bash
sudo raspi-config nonint do_gpio 0
```

### 4. Reboot and Verify

Reboot your Raspberry Pi to apply the changes:

```bash
sudo reboot
```

After reboot, verify GPIO access:

```bash
# Test GPIO access (should not require sudo)
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO access successful')"
```

If you see "GPIO access successful", the setup is correct. If you get a permission error, double-check the group membership and udev rules.

## Installation

Follow these steps to set up the DEWHOME application on your Raspberry Pi Zero W.

### 1. Clone the Repository

```bash
# Navigate to your home directory
cd /home/pi

# Clone the repository
git clone https://github.com/dewanshDT/dewhome.git

# Navigate into the project directory
cd dewhome
```

### 2. Set Up the Virtual Environment

Install `virtualenv` if you haven't already:

```bash
sudo apt update
sudo apt install -y python3-venv
```

Create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Update `pip` and install the required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Application

The application now uses dynamic device management, so no manual configuration is needed. On first run, it will:

- Create the database with GPIO pin definitions
- Set up one default device on the first available GPIO pin
- Allow you to add more devices through the web interface

### 5. Set Database Permissions

Ensure the database file has proper permissions:

```bash
# Set correct ownership and permissions for the database
sudo chown pi:gpio /home/pi/dewhome/device_states.db
chmod 664 /home/pi/dewhome/device_states.db
```

## Setting Up Gunicorn

Install Gunicorn in your virtual environment if not already installed:

```bash
pip install gunicorn
```

Test the application with Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

Press `Ctrl+C` to stop the server after confirming it's running.

## Setting Up Nginx

Install Nginx:

```bash
sudo apt install -y nginx
```

Create a new Nginx server block configuration:

```bash
sudo nano /etc/nginx/sites-available/dewhome
```

Add the following content:

```nginx
server {
    listen 80;
    server_name _;

    location = /favicon.ico {
        alias /home/pi/dewhome/static/favicon.ico;
    }

    location /static/ {
        alias /home/pi/dewhome/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the new server block and disable the default:

```bash
sudo ln -s /etc/nginx/sites-available/dewhome /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
```

Test the Nginx configuration and restart the service:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Configuring Systemd Service

Create a systemd service file to manage the Gunicorn application:

```bash
sudo nano /etc/systemd/system/dewhome.service
```

Add the following content:

```ini
[Unit]
Description=Gunicorn instance to serve DEWHOME Flask app
After=network.target syslog.target multi-user.target systemd-udev-settle.service
Wants=network.target

[Service]
User=pi
Group=gpio
WorkingDirectory=/home/pi/dewhome
Environment="PATH=/home/pi/dewhome/venv/bin"
ExecStart=/home/pi/dewhome/venv/bin/gunicorn --workers 1 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Reload systemd, enable the service, and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dewhome.service
sudo systemctl start dewhome.service
```

Check the status of the service:

```bash
sudo systemctl status dewhome.service
```

## Running the Application

After setting up the systemd service and Nginx, the application should start automatically on boot and run continuously.

To manually restart the service:

```bash
sudo systemctl restart dewhome.service
```

## Accessing the Web Interface

- Open a web browser on a device connected to the same network.
- Navigate to `http://[Raspberry_Pi_IP_Address]/`
- You should see the DEWHOME interface with your devices listed.

## Using the Device Management Interface

### Adding New Devices

1. Click the **"Add Device"** button in the top navigation
2. Fill in the device information:
   - **Device Name**: Choose a descriptive name (e.g., "Living Room Light")
   - **Icon**: Select from available Font Awesome icons
   - **GPIO Pin**: Choose from available pins with automatic validation
3. The system will show warnings for special pins (I2C, UART, SPI)
4. Click **"Add Device"** to create the device

### Managing Existing Devices

- **Toggle Devices**: Click the toggle button to turn devices on/off
- **Delete Devices**: Click the trash icon to remove devices (with confirmation)
- **View Pin Information**: Each device shows its GPIO pin and category

### Pin Selection Guidelines

- **Prefer GPIO pins** (green badge) for general devices
- **Avoid I2C pins** (yellow badge) unless I2C is not needed
- **Avoid UART pins** (orange badge) unless serial console is disabled
- **Avoid SPI pins** (purple badge) unless SPI is not needed

## Project Structure

```
dewhome/
├── app.py                 # Main Flask application with dynamic device management
├── modules/
│   ├── gpio_control.py    # Dynamic GPIO pin management
│   └── db_operations.py   # Database operations with GPIO pin definitions
├── templates/
│   └── index.html         # Web interface with device management modals
├── static/
│   ├── css/style.css      # Enhanced styling with modal support
│   ├── js/main.js         # JavaScript for device management
│   └── favicon.ico        # App icon
├── device_states.db       # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── install.sh            # Automated installation script
└── README.md             # This documentation
```

## Important Notes and Known Issues

### Database Schema

The new version uses a relational database schema:

- **gpio_pins table**: Stores all 40 GPIO pin definitions with categories
- **devices table**: Stores user-created devices with pin assignments
- **Foreign key relationships**: Ensures data integrity

### Default Device

- On first run, the system creates one default device on the first available GPIO pin
- Users can delete this device and create their own custom devices
- The system prevents creating devices without any GPIO pins available

### Pin Validation

- Real-time validation prevents pin conflicts
- Warnings are shown for special-purpose pins
- Only pins with output capability are available for device creation

## Troubleshooting

### Device Management Issues

**Problem**: Cannot add new devices or pins not showing.

**Solutions**:

1. **Check database initialization**:

   ```bash
   # Check if database exists and has data
   sqlite3 device_states.db "SELECT COUNT(*) FROM gpio_pins;"
   # Should return 40
   ```

2. **Verify pin availability**:

   ```bash
   # Check available pins via API
   curl http://localhost:5000/pins/usable
   ```

3. **Reset database** (if needed):
   ```bash
   # Backup existing devices first!
   rm device_states.db
   # Restart the application to recreate database
   sudo systemctl restart dewhome.service
   ```

### GPIO Access Issues

**Problem**: Application cannot control GPIO pins or shows permission errors.

**Solutions**:

1. **Check GPIO group membership**:

   ```bash
   groups pi
   ```

   Ensure `gpio` is listed in the output.

2. **Verify GPIO permissions**:

   ```bash
   ls -la /dev/gpiomem
   ls -la /sys/class/gpio/
   ```

   Should show group `gpio` with read/write permissions.

3. **Test GPIO access manually**:
   ```bash
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); print('GPIO test successful')"
   ```

### Service Issues

**Problem**: DEWHOME service fails to start.

**Solutions**:

1. **Check service status**:

   ```bash
   sudo systemctl status dewhome.service
   sudo journalctl -u dewhome.service -f
   ```

2. **Verify file paths**:

   ```bash
   ls -la /home/pi/dewhome/
   ls -la /home/pi/dewhome/venv/bin/gunicorn
   ```

3. **Check permissions**:
   ```bash
   sudo chown -R pi:gpio /home/pi/dewhome/
   chmod +x /home/pi/dewhome/venv/bin/gunicorn
   ```

### Web Interface Issues

**Problem**: Cannot access the web interface.

**Solutions**:

1. **Check if services are running**:

   ```bash
   sudo systemctl status nginx
   sudo systemctl status dewhome.service
   ```

2. **Verify port access**:

   ```bash
   netstat -tlnp | grep :80
   netstat -tlnp | grep :5000
   ```

3. **Check firewall settings**:
   ```bash
   sudo ufw status
   sudo ufw allow 80
   ```

## API Endpoints

The application provides RESTful API endpoints:

### Device Management

- `GET /devices` - List all devices
- `POST /devices` - Create new device
- `DELETE /devices/<id>` - Delete device
- `POST /device` - Control device (toggle on/off)

### Pin Management

- `GET /pins` - List all GPIO pins with status
- `GET /pins/usable` - List available pins for new devices

### Example API Usage

```bash
# List all devices
curl http://localhost:5000/devices

# Add new device
curl -X POST http://localhost:5000/devices \
  -H "Content-Type: application/json" \
  -d '{"name": "LED Strip", "icon": "fa-lightbulb", "pin_number": 18}'

# Control device
curl -X POST http://localhost:5000/device \
  -H "Content-Type: application/json" \
  -d '{"device_id": 1, "action": "high"}'
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
