# DEWHOME Installation Guide

This guide explains how to install DEWHOME on your Raspberry Pi Zero W using the automated installation script.

## 🚀 Quick Installation

### Method 1: Direct Transfer and Install

```bash
# On your development machine, transfer files to your Pi
scp -r . pi@PI_IP_ADDRESS:~/dewhome-setup/

# SSH into your Pi
ssh pi@PI_IP_ADDRESS

# Navigate to the setup directory and run installation
cd ~/dewhome-setup
chmod +x install.sh
./install.sh
```

### Method 2: One-Command Installation

```bash
# Transfer and install in one command (replace PI_IP_ADDRESS with your Pi's IP)
scp -r . pi@PI_IP_ADDRESS:~/dewhome-setup/ && ssh pi@PI_IP_ADDRESS 'cd ~/dewhome-setup && chmod +x install.sh && ./install.sh'
```

## ⚙️ Installation Options

The installation script is flexible and works with any username (not just 'pi'):

### Basic Usage

```bash
# Install for current user
./install.sh

# Install for specific user
./install.sh -u username

# Install using environment variable
INSTALL_USER=username ./install.sh

# Show help
./install.sh --help
```

### Examples

```bash
# Install for user 'pi' (traditional)
./install.sh -u pi

# Install for user 'dewansh'
./install.sh -u dewansh

# Install for user 'admin'
./install.sh -u admin

# Install for current user (auto-detect)
./install.sh
```

## 🔧 What the Script Does

The installation script performs these steps automatically:

1. **User Configuration**: Detects or uses specified username
2. **WiFi Power Management**: Disables power saving to prevent disconnections
3. **System Updates**: Updates all packages
4. **Dependencies**: Installs Python3, Nginx, Git, and required tools
5. **GPIO Setup**: Configures proper GPIO permissions for the specified user
6. **Project Setup**: Downloads/copies DEWHOME project files
7. **Python Environment**: Creates virtual environment and installs dependencies
8. **Application Config**: Enables GPIO functionality in the application
9. **Database Setup**: Initializes SQLite database with proper permissions
10. **Nginx Configuration**: Sets up reverse proxy with security headers
11. **Systemd Service**: Creates auto-starting service
12. **Final Testing**: Runs system tests to verify installation

## 📋 Prerequisites

- Raspberry Pi Zero W with fresh Raspbian installation
- SSH access to your Pi
- Internet connection on your Pi
- Sufficient disk space (minimum 500MB free)

## 🌐 After Installation

Once installation completes, you can access DEWHOME at:

- `http://YOUR_PI_IP_ADDRESS`
- `http://YOUR_PI_HOSTNAME.local` (if mDNS is enabled)

## 🔌 GPIO Pin Mapping

The application uses these GPIO pins by default:

- **Device 1 (Bulb 1)**: GPIO 17
- **Device 2 (Bulb 2)**: GPIO 27
- **Device 3 (Fan)**: GPIO 18
- **Device 4 (Generic Device)**: GPIO 22

## 🛠️ Management Commands

After installation, use these commands to manage DEWHOME:

```bash
# Check service status
sudo systemctl status dewhome

# Restart the service
sudo systemctl restart dewhome

# View live logs
sudo journalctl -u dewhome -f

# Restart web server
sudo systemctl restart nginx

# Check what's running on port 5000
sudo netstat -tulpn | grep :5000
```

## 🐛 Troubleshooting

### Installation Fails

- Check the log file: `/tmp/dewhome_install.log`
- Ensure you have internet connection
- Verify sufficient disk space: `df -h`
- Try running the script again

### GPIO Permission Issues

```bash
# Check if user is in gpio group
groups $USER

# Test GPIO access
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"
```

### Service Not Starting

```bash
# Check detailed logs
sudo journalctl -u dewhome -n 50

# Check if port 5000 is available
sudo lsof -i :5000
```

### Web Interface Not Accessible

```bash
# Check nginx status
sudo systemctl status nginx

# Test local access
curl -I http://localhost

# Check firewall (if enabled)
sudo ufw status
```

## 🔄 Reinstallation

To reinstall or update:

```bash
# The script automatically backs up existing installations
./install.sh

# Manual cleanup if needed
sudo systemctl stop dewhome
sudo rm -rf ~/dewhome_backup_*
```

## 📝 Logs and Debugging

Important log locations:

- **Installation Log**: `/tmp/dewhome_install.log`
- **Application Logs**: `sudo journalctl -u dewhome -f`
- **Nginx Logs**: `/var/log/nginx/error.log`
- **System Logs**: `sudo journalctl -f`

## 🔒 Security Notes

The installation script:

- Creates proper file permissions
- Sets up user groups correctly
- Configures secure Nginx headers
- Uses non-root user for the application
- Enables systemd service isolation

For production use, consider:

- Setting up SSL/HTTPS
- Configuring firewall rules
- Regular security updates
- Changing default device names/pins
