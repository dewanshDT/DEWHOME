#!/bin/bash

# DEWHOME Installation Script for Raspberry Pi Zero W
# This script automates the complete setup process
# Author: DEWHOME Project
# Version: 1.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Auto-detect username or use provided one
INSTALL_USER="${INSTALL_USER:-$USER}"
USER_HOME=$(eval echo "~$INSTALL_USER")
PROJECT_DIR="$USER_HOME/dewhome"
SERVICE_NAME="dewhome"
LOG_FILE="/tmp/dewhome_install.log"
GITHUB_REPO="https://github.com/dewanshDT/dewhome.git"

# Function to show usage
show_usage() {
    echo "DEWHOME Installation Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -u, --user USERNAME    Install for specific user (default: current user)"
    echo "  -h, --help            Show this help message"
    echo
    echo "Environment Variables:"
    echo "  INSTALL_USER          Username to install for (can be set instead of -u)"
    echo
    echo "Examples:"
    echo "  $0                    # Install for current user"
    echo "  $0 -u pi              # Install for user 'pi'"
    echo "  INSTALL_USER=pi $0    # Install for user 'pi' via environment variable"
    echo
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--user)
                INSTALL_USER="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup and validate user configuration
setup_user_config() {
    print_status "Setting up user configuration..."
    
    # If no user specified, use current user
    if [ -z "$INSTALL_USER" ]; then
        INSTALL_USER="$USER"
    fi
    
    # Verify the user exists
    if ! id "$INSTALL_USER" &>/dev/null; then
        print_error "User '$INSTALL_USER' does not exist on this system"
        exit 1
    fi
    
    # Update variables based on actual user
    USER_HOME=$(eval echo "~$INSTALL_USER")
    PROJECT_DIR="$USER_HOME/dewhome"
    
    print_success "Installation configured for user: $INSTALL_USER"
    print_success "Home directory: $USER_HOME"
    print_success "Project directory: $PROJECT_DIR"
}

# Function to check if running on Raspberry Pi
check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        print_warning "This doesn't appear to be a Raspberry Pi"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to disable WiFi power management
disable_wifi_power_save() {
    print_status "Disabling WiFi power management to prevent disconnections..."
    
    # Method 1: Using iwconfig
    if command_exists iwconfig; then
        sudo iwconfig wlan0 power off 2>/dev/null || true
        print_success "WiFi power management disabled via iwconfig"
    fi
    
    # Method 2: Create systemd service to disable power management at boot
    sudo tee /etc/systemd/system/wifi-powersave-off.service > /dev/null << 'EOF'
[Unit]
Description=Turn off WiFi power management
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/sbin/iwconfig wlan0 power off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl enable wifi-powersave-off.service
    sudo systemctl start wifi-powersave-off.service
    
    # Method 3: Add to NetworkManager if it exists
    if [ -d "/etc/NetworkManager/conf.d" ]; then
        sudo tee /etc/NetworkManager/conf.d/wifi-powersave-off.conf > /dev/null << 'EOF'
[connection]
wifi.powersave = 2
EOF
        print_success "WiFi power management disabled via NetworkManager"
    fi
    
    print_success "WiFi power management configuration completed"
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update -y >> "$LOG_FILE" 2>&1
    sudo apt upgrade -y >> "$LOG_FILE" 2>&1
    print_success "System updated successfully"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing required packages..."
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "git"
        "nginx"
        "sqlite3"
        "build-essential"
        "wireless-tools"
        "net-tools"
    )
    
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            print_status "Installing $package..."
            sudo apt install -y "$package" >> "$LOG_FILE" 2>&1
            print_success "$package installed"
        else
            print_status "$package already installed"
        fi
    done
    
    print_success "All dependencies installed"
}

# Function to setup GPIO permissions
setup_gpio_permissions() {
    print_status "Setting up GPIO permissions..."
    
    # Add user to gpio group
    sudo usermod -a -G gpio "$INSTALL_USER"
    print_success "Added user '$INSTALL_USER' to gpio group"
    
    # Create GPIO udev rules
    sudo tee /etc/udev/rules.d/99-gpio.rules > /dev/null << 'EOF'
SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"
EOF
    print_success "Created GPIO udev rules"
    
    # Enable GPIO interface
    # sudo raspi-config nonint do_gpio 0  # Commented out - function not available
    print_success "GPIO interface enabled (default on modern Raspberry Pi OS)"
    
    # Reload udev rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    print_success "GPIO permissions configured"
}

# Function to clone or update project
setup_project() {
    print_status "Setting up DEWHOME project..."
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Project directory already exists. Backing up..."
        sudo mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Clone the repository
    if [ -n "$GITHUB_REPO" ] && git ls-remote "$GITHUB_REPO" &> /dev/null; then
        print_status "Cloning from repository..."
        git clone "$GITHUB_REPO" "$PROJECT_DIR" >> "$LOG_FILE" 2>&1
    else
        print_status "Creating project directory structure..."
        mkdir -p "$PROJECT_DIR"/{modules,static/{css,js},templates}
        
        # If running from project directory, copy files
        if [ -f "app.py" ]; then
            cp -r . "$PROJECT_DIR/"
        else
            print_error "No project files found and repository not accessible"
            print_error "Please ensure you're running this script from the DEWHOME project directory"
            exit 1
        fi
    fi
    
    cd "$PROJECT_DIR"
    print_success "Project setup completed"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    python3 -m venv venv >> "$LOG_FILE" 2>&1
    print_success "Virtual environment created"
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip >> "$LOG_FILE" 2>&1
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt >> "$LOG_FILE" 2>&1
        print_success "Python dependencies installed from requirements.txt"
    else
        # Install basic dependencies
        pip install Flask gunicorn RPi.GPIO Flask-Cors >> "$LOG_FILE" 2>&1
        print_success "Basic Python dependencies installed"
    fi
    
    deactivate
}

# Function to enable GPIO in application
enable_gpio_in_app() {
    print_status "Enabling GPIO functionality in application..."
    
    cd "$PROJECT_DIR"
    
    if [ -f "app.py" ]; then
        # Create backup
        cp app.py app.py.backup
        
        # Uncomment GPIO lines
        sed -i 's/# from modules import gpio_control/from modules import gpio_control/' app.py
        sed -i 's/# gpio_control\.setup_pins()/gpio_control.setup_pins()/' app.py
        sed -i 's/# gpio_control\.set_device_states(device_states)/gpio_control.set_device_states(device_states)/' app.py
        sed -i 's/# gpio_control\.control_device(device_id, action)/gpio_control.control_device(device_id, action)/' app.py
        sed -i 's/# gpio_control\.cleanup()/gpio_control.cleanup()/' app.py
        
        print_success "GPIO functionality enabled in app.py"
    else
        print_warning "app.py not found, skipping GPIO enablement"
    fi
}

# Function to setup database permissions
setup_database() {
    print_status "Setting up database..."
    
    cd "$PROJECT_DIR"
    
    # Initialize database by running app briefly
    source venv/bin/activate
    timeout 5 python3 -c "
from modules import db_operations
db_operations.init_db()
db_operations.initialize_device_states([1, 2, 3, 4])
print('Database initialized')
" >> "$LOG_FILE" 2>&1 || true
    deactivate
    
    # Set proper permissions
    if [ -f "device_states.db" ]; then
        chmod 664 device_states.db
        chown "$INSTALL_USER:gpio" device_states.db
        print_success "Database permissions set"
    fi
}

# Function to configure Nginx
configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/dewhome > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Favicon
    location = /favicon.ico {
        alias $PROJECT_DIR/static/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # Static files
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

    # Enable site and disable default
    sudo ln -sf /etc/nginx/sites-available/dewhome /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    if sudo nginx -t >> "$LOG_FILE" 2>&1; then
        sudo systemctl enable nginx
        sudo systemctl restart nginx
        print_success "Nginx configured and started"
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Gunicorn instance to serve DEWHOME Flask app
Documentation=https://github.com/dewanshDT/dewhome
After=network.target syslog.target multi-user.target systemd-udev-settle.service
Wants=network.target

[Service]
Type=notify
User=$INSTALL_USER
Group=gpio
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 1 --bind 127.0.0.1:5000 --timeout 300 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable ${SERVICE_NAME}.service
    
    print_success "Systemd service created and enabled"
}

# Function to set final permissions
set_final_permissions() {
    print_status "Setting final permissions..."
    
    # Set ownership
    sudo chown -R "$INSTALL_USER:gpio" "$PROJECT_DIR"
    
    # Set directory permissions
    find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
    
    # Set file permissions
    find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
    
    # IMPORTANT: Ensure nginx can traverse to user's home directory
    # This fixes the common issue where static files get 403 Forbidden
    HOME_DIR=$(eval echo "~$INSTALL_USER")
    if [ "$(stat -c %a "$HOME_DIR")" = "700" ]; then
        print_status "Setting home directory permissions for web server access..."
        chmod 755 "$HOME_DIR"
        print_success "Home directory permissions updated for nginx access"
    else
        print_status "Home directory permissions already suitable for web server"
    fi
    
    # Make scripts executable
    find "$PROJECT_DIR" -name "*.sh" -exec chmod +x {} \;
    
    # Set virtual environment permissions
    if [ -d "$PROJECT_DIR/venv" ]; then
        find "$PROJECT_DIR/venv/bin" -type f -exec chmod +x {} \;
    fi
    
    # Database permissions
    if [ -f "$PROJECT_DIR/device_states.db" ]; then
        chmod 664 "$PROJECT_DIR/device_states.db"
        chown "$INSTALL_USER:gpio" "$PROJECT_DIR/device_states.db"
    fi
    
    print_success "Permissions set correctly"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start DEWHOME service
    if sudo systemctl start ${SERVICE_NAME}.service; then
        print_success "DEWHOME service started"
    else
        print_error "Failed to start DEWHOME service"
        sudo journalctl -u ${SERVICE_NAME}.service --no-pager -n 20
        return 1
    fi
    
    # Ensure Nginx is running
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        sudo systemctl restart nginx
        print_success "Nginx restarted"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running system tests..."
    
    # Test GPIO access
    if python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); GPIO.cleanup(); print('GPIO test passed')" >> "$LOG_FILE" 2>&1; then
        print_success "GPIO access test passed"
    else
        print_warning "GPIO access test failed - may need reboot"
    fi
    
    # Test service status
    if sudo systemctl is-active --quiet ${SERVICE_NAME}.service; then
        print_success "DEWHOME service is active"
    else
        print_warning "DEWHOME service is not active"
    fi
    
    # Test web interface
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
        print_success "Web interface is responding"
    else
        print_warning "Web interface test failed"
    fi
}

# Function to display final information
show_final_info() {
    local ip_address=$(hostname -I | awk '{print $1}')
    
    echo
    echo "======================================"
    echo -e "${GREEN}DEWHOME Installation Complete!${NC}"
    echo "======================================"
    echo
    echo "🌐 Access your DEWHOME interface at:"
    echo "   http://$ip_address"
    echo "   http://$(hostname).local (if mDNS is enabled)"
    echo
    echo "🔧 GPIO Pin Mapping:"
    echo "   Device 1 (Bulb 1): GPIO 17"
    echo "   Device 2 (Bulb 2): GPIO 27"
    echo "   Device 3 (Fan):    GPIO 18"
    echo "   Device 4 (Device): GPIO 22"
    echo
    echo "📋 Useful Commands:"
    echo "   sudo systemctl status dewhome    # Check service status"
    echo "   sudo systemctl restart dewhome   # Restart service"
    echo "   sudo journalctl -u dewhome -f    # View logs"
    echo "   sudo systemctl restart nginx     # Restart web server"
    echo
    echo "👤 Installed for user: $INSTALL_USER"
    echo "📁 Project Location: $PROJECT_DIR"
    echo "📄 Installation Log: $LOG_FILE"
    echo
    if [ ! -f "/var/run/reboot-required" ]; then
        echo -e "${YELLOW}⚠️  Reboot recommended to ensure all changes take effect${NC}"
        echo "   sudo reboot"
    fi
    echo
}

# Function to handle errors
error_handler() {
    local line_number=$1
    print_error "Installation failed at line $line_number"
    print_error "Check the log file: $LOG_FILE"
    echo
    echo "Common solutions:"
    echo "1. Ensure you're running as the correct user"
    echo "2. Check internet connection"
    echo "3. Ensure sufficient disk space"
    echo "4. Try running the script again"
    echo
    exit 1
}

# Main installation function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Setup error handling
    trap 'error_handler $LINENO' ERR
    
    # Clear log file
    > "$LOG_FILE"
    
    echo "======================================"
    echo "DEWHOME Installation Script"
    echo "======================================"
    echo
    
    print_status "Starting DEWHOME installation..."
    print_status "Log file: $LOG_FILE"
    echo
    
    # Pre-installation checks
    setup_user_config
    check_raspberry_pi
    
    # Installation steps
    print_status "Step 1/12: Disabling WiFi power management..."
    disable_wifi_power_save
    
    print_status "Step 2/12: Updating system..."
    update_system
    
    print_status "Step 3/12: Installing dependencies..."
    install_dependencies
    
    print_status "Step 4/12: Setting up GPIO permissions..."
    setup_gpio_permissions
    
    print_status "Step 5/12: Setting up project..."
    setup_project
    
    print_status "Step 6/12: Setting up Python environment..."
    setup_python_env
    
    print_status "Step 7/12: Enabling GPIO in application..."
    enable_gpio_in_app
    
    print_status "Step 8/12: Setting up database..."
    setup_database
    
    print_status "Step 9/12: Configuring Nginx..."
    configure_nginx
    
    print_status "Step 10/12: Creating systemd service..."
    create_systemd_service
    
    print_status "Step 11/12: Setting permissions..."
    set_final_permissions
    
    print_status "Step 12/12: Starting services..."
    start_services
    
    print_status "Running tests..."
    run_tests
    
    show_final_info
    
    print_success "Installation completed successfully!"
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 