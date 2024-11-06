# DEWHOME: Raspberry Pi Zero W Home Automation System

DEWHOME is a lightweight home automation system designed to run on a Raspberry Pi Zero W. It allows you to control devices connected to the Raspberry Pi's GPIO pins through a web interface. The application uses Flask for the web server, Gunicorn as the WSGI server, and Nginx as a reverse proxy to handle client requests efficiently.

## Table of Contents

- [DEWHOME: Raspberry Pi Zero W Home Automation System](#dewhome-raspberry-pi-zero-w-home-automation-system)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Set Up the Virtual Environment](#2-set-up-the-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Configure the Application](#4-configure-the-application)
  - [Setting Up Gunicorn](#setting-up-gunicorn)
  - [Setting Up Nginx](#setting-up-nginx)
  - [Configuring Systemd Service](#configuring-systemd-service)
  - [Running the Application](#running-the-application)
  - [Accessing the Web Interface](#accessing-the-web-interface)
  - [Project Structure](#project-structure)
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
PIN_MAPPING = {
    1: 17,  # GPIO pin connected to Device 1
    2: 27,  # GPIO pin connected to Device 2
    3: 22,  # GPIO pin connected to Device 3
    4: 23   # GPIO pin connected to Device 4
}
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

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
