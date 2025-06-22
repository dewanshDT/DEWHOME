### GPIO Setup Commands

```bash
# Add user to GPIO group
sudo usermod -a -G gpio pi

# Create GPIO udev rules
sudo nano /etc/udev/rules.d/99-gpio.rules
# Add: SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"
# Add: SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"

# Enable GPIO interface
sudo raspi-config nonint do_gpio 0

# Reboot to apply changes
sudo reboot

# Test GPIO access
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO access successful')"
```

### for running in prod

`gunicorn --bind 0.0.0.0:5000 app:app`

### Troubleshooting Commands

```bash
# Check GPIO group membership
groups pi

# Check GPIO permissions
ls -la /dev/gpiomem
ls -la /sys/class/gpio/

# Check if GPIO is enabled
sudo raspi-config nonint get_gpio

# Test GPIO manually
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); GPIO.output(17, GPIO.HIGH); print('GPIO test successful')"

# Check service status
sudo systemctl status dewhome.service
sudo journalctl -u dewhome.service -f
```
