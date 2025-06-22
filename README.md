# DEWHOME: Raspberry Pi Zero W Home Automation System

DEWHOME is a lightweight home automation system designed to run on a Raspberry Pi Zero W. It allows you to control devices connected to the Raspberry Pi's GPIO pins through a web interface. The application uses Flask for the web server, Gunicorn as the WSGI server, and Nginx as a reverse proxy to handle client requests efficiently.

## Table of Contents

- [DEWHOME: Raspberry Pi Zero W Home Automation System](#dewhome-raspberry-pi-zero-w-home-automation-system)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
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
  - [Project Structure](#project-structure)
  - [Important Notes and Known Issues](#important-notes-and-known-issues)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Control Devices**: Turn devices on and off via a web interface.
- **Responsive Design**: Optimized for both desktop and mobile devices.
- **Dark Mode UI**: Modern dark theme for comfortable use in low-light conditions.
- **Device Icons and Names**: Customize device names and icons for easy identification.
- **Persistent States**: Device states are stored in a SQLite database.
- **Secure and Efficient**: Uses Gunicorn and Nginx for robust performance.

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

### 5. Enable GPIO in app.py

Once GPIO access is properly configured, uncomment the GPIO-related lines in `app.py`:

```python
# Uncomment these lines in app.py:
from modules import gpio_control
gpio_control.setup_pins()
gpio_control.set_device_states(device_states)
gpio_control.control_device(device_id, action)
gpio_control.cleanup()
```

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

**Note**: The `requirements.txt` file should include all necessary packages, such as:

```
Flask
gunicorn
RPi.GPIO
```

### 4. Configure the Application

Ensure that your GPIO pins and device configurations are set up correctly.

- **Enable GPIO Functionality**: Uncomment the GPIO-related lines in `app.py` to enable hardware control:

```python
# In app.py, uncomment these lines:
from modules import gpio_control
gpio_control.setup_pins()
gpio_control.set_device_states(device_states)
gpio_control.control_device(device_id, action)
gpio_control.cleanup()
```

- **Edit `app.py`**: Verify that the `DEVICES` list matches your connected devices.

```python
# app.py snippet
DEVICES = [
    {'id': 1, 'name': 'Bulb 1', 'icon': 'fa-lightbulb'},
    {'id': 2, 'name': 'Bulb 2', 'icon': 'fa-lightbulb'},
    {'id': 3, 'name': 'Fan', 'icon': 'fa-fan'},
    {'id': 4, 'name': 'Device 4', 'icon': 'fa-plug'}
]
```

- **Edit `gpio_control.py`**: Ensure the GPIO pins correspond to the device IDs.

```python
# gpio_control.py snippet
DEVICE_PINS = {
    1: 17,  # GPIO pin connected to Device 1
    2: 27,  # GPIO pin connected to Device 2
    3: 18,  # GPIO pin connected to Device 3
    4: 22   # GPIO pin connected to Device 4
}
```

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

**Explanation:**

- **User and Group**: Set to `pi` and `gpio` to ensure access to GPIO pins.
- **WorkingDirectory**: Points to the project directory.
- **Environment**: Specifies the path to the virtual environment.
- **ExecStart**: Command to start Gunicorn with the application.

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

## Project Structure

```
dewhome/
├── app.py
├── modules/
│   ├── gpio_control.py
│   └── db_operations.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── favicon.ico
├── device_states.db
├── requirements.txt
└── README.md
```

- **app.py**: Main Flask application.
- **modules/**: Contains modules for GPIO control and database operations.
- **templates/**: HTML templates.
- **static/**: Static files like CSS, JavaScript, and images.
- **device_states.db**: SQLite database file storing device states.
- **requirements.txt**: Python dependencies.
- **README.md**: Project documentation.

## Important Notes and Known Issues

### GPIO Pin Mapping

**Important**: The GPIO pin mapping in `gpio_control.py` uses the following pins:

- Device 1: GPIO 17
- Device 2: GPIO 27
- Device 3: GPIO 18
- Device 4: GPIO 22

Ensure your hardware connections match these pins exactly.

### User Path Configuration

**Note**: This installation guide assumes the default Raspberry Pi user (`pi`) and installation path (`/home/pi/dewhome`). If you're using a different user or installation path, update the following files:

1. **Nginx configuration** (`/etc/nginx/sites-available/dewhome`):

   ```nginx
   # Update these paths:
   alias /home/YOUR_USER/dewhome/static/favicon.ico;
   alias /home/YOUR_USER/dewhome/static/;
   ```

2. **Systemd service** (`/etc/systemd/system/dewhome.service`):
   ```ini
   # Update these paths:
   User=YOUR_USER
   WorkingDirectory=/home/YOUR_USER/dewhome
   Environment="PATH=/home/YOUR_USER/dewhome/venv/bin"
   ExecStart=/home/YOUR_USER/dewhome/venv/bin/gunicorn --workers 1 --bind 127.0.0.1:5000 app:app
   ```

### Database Permissions

The SQLite database (`device_states.db`) is created in the project directory. Ensure proper permissions:

```bash
# Set correct ownership and permissions
sudo chown pi:gpio /home/pi/dewhome/device_states.db
chmod 664 /home/pi/dewhome/device_states.db
```

### GPIO Logic Note

The GPIO control uses inverted logic (active-low) to handle common relay wiring issues:

- `action='high'` → GPIO.LOW (device ON)
- `action='low'` → GPIO.HIGH (device OFF)

If your relays work with normal logic, you may need to modify `gpio_control.py`.

## Troubleshooting

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

4. **Check if GPIO is enabled**:
   ```bash
   sudo raspi-config nonint get_gpio
   ```
   Should return `0` if enabled.

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

### Hardware Issues

**Problem**: Devices don't respond to GPIO control.

**Solutions**:

1. **Verify wiring**: Check that GPIO pins are correctly connected to relays/switches.
2. **Test with simple script**:
   ```bash
   python3 -c "
   import RPi.GPIO as GPIO
   import time
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(17, GPIO.OUT)
   GPIO.output(17, GPIO.HIGH)
   time.sleep(1)
   GPIO.output(17, GPIO.LOW)
   print('GPIO test completed')
   "
   ```
3. **Check relay logic**: Some relays are active-low (inverted logic).

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
