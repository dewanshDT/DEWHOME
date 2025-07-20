#!/bin/bash

# DEWHOME Update Script
# This script updates DEWHOME to the latest version from git
# Author: DEWHOME Project
# Version: 2.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
UPDATE_USER="${UPDATE_USER:-$USER}"
UPDATE_BRANCH="${UPDATE_BRANCH:-main}"
USER_HOME=$(eval echo "~$UPDATE_USER")
PROJECT_DIR="$USER_HOME/dewhome"
SERVICE_NAME="dewhome"
LOG_FILE="/tmp/dewhome_update.log"
BACKUP_DIR="$USER_HOME/dewhome_backup_$(date +%Y%m%d_%H%M%S)"
GITHUB_REPO="https://github.com/dewanshDT/dewhome.git"

# Function to show usage
show_usage() {
    echo "DEWHOME Update Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -u, --user USERNAME      Update for specific user (default: current user)"
    echo "  -b, --branch BRANCH      Update to specific git branch (default: main)"
    echo "  --force                  Force update even if working directory is dirty"
    echo "  --no-backup             Skip creating backup before update"
    echo "  --no-restart             Skip restarting services after update"
    echo "  -h, --help              Show this help message"
    echo
    echo "Environment Variables:"
    echo "  UPDATE_USER             Username to update for (can be set instead of -u)"
    echo "  UPDATE_BRANCH           Git branch to update to (can be set instead of -b)"
    echo
    echo "Examples:"
    echo "  $0                      # Update current user to main branch"
    echo "  $0 -u pi                # Update for user 'pi' to main branch"
    echo "  $0 -b feature/actions   # Update to feature/actions branch"
    echo "  $0 -u pi -b develop     # Update user 'pi' to develop branch"
    echo "  UPDATE_USER=pi UPDATE_BRANCH=feature/actions $0  # Using environment variables"
    echo
}

# Parse command line arguments
parse_arguments() {
    FORCE_UPDATE=false
    NO_BACKUP=false
    NO_RESTART=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--user)
                UPDATE_USER="$2"
                shift 2
                ;;
            -b|--branch)
                UPDATE_BRANCH="$2"
                shift 2
                ;;
            --force)
                FORCE_UPDATE=true
                shift
                ;;
            --no-backup)
                NO_BACKUP=true
                shift
                ;;
            --no-restart)
                NO_RESTART=true
                shift
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
    if [ -z "$UPDATE_USER" ]; then
        UPDATE_USER="$USER"
    fi
    
    # Verify the user exists
    if ! id "$UPDATE_USER" &>/dev/null; then
        print_error "User '$UPDATE_USER' does not exist on this system"
        exit 1
    fi
    
    # Update variables based on actual user
    USER_HOME=$(eval echo "~$UPDATE_USER")
    PROJECT_DIR="$USER_HOME/dewhome"
    BACKUP_DIR="$USER_HOME/dewhome_backup_$(date +%Y%m%d_%H%M%S)"
    
    print_success "Update configured for user: $UPDATE_USER"
    print_success "Home directory: $USER_HOME"
    print_success "Project directory: $PROJECT_DIR"
    print_success "Target branch: $UPDATE_BRANCH"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if DEWHOME is installed
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "DEWHOME installation not found at $PROJECT_DIR"
        print_error "Please install DEWHOME first using install.sh"
        exit 1
    fi
    
    # Check if it's a git repository
    if [ ! -d "$PROJECT_DIR/.git" ]; then
        print_error "DEWHOME directory is not a git repository"
        print_error "Cannot update non-git installation"
        exit 1
    fi
    
    # Check if user owns the directory
    if [ ! -w "$PROJECT_DIR" ]; then
        print_error "No write permission to $PROJECT_DIR"
        print_error "You may need to run as the correct user or with sudo"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to backup current installation
backup_current() {
    if [ "$NO_BACKUP" = true ]; then
        print_status "Skipping backup as requested"
        return 0
    fi
    
    print_status "Creating backup of current installation..."
    
    if [ -d "$PROJECT_DIR" ]; then
        cp -r "$PROJECT_DIR" "$BACKUP_DIR"
        print_success "Backup created at: $BACKUP_DIR"
        
        # Also backup the database separately
        if [ -f "$PROJECT_DIR/device_states.db" ]; then
            cp "$PROJECT_DIR/device_states.db" "$BACKUP_DIR/device_states.db.backup"
            print_success "Database backup created"
        fi
    else
        print_warning "Project directory not found, skipping backup"
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping DEWHOME services..."
    
    if systemctl is-active --quiet ${SERVICE_NAME}.service 2>/dev/null; then
        sudo systemctl stop ${SERVICE_NAME}.service
        print_success "DEWHOME service stopped"
    else
        print_status "DEWHOME service was not running"
    fi
}

# Function to update git repository
update_repository() {
    print_status "Updating git repository..."
    
    cd "$PROJECT_DIR"
    
    # Check working directory status
    if [ "$(git status --porcelain)" ] && [ "$FORCE_UPDATE" = false ]; then
        print_error "Working directory has uncommitted changes"
        print_error "Use --force to override or commit/stash your changes"
        git status --short
        exit 1
    fi
    
    # Fetch latest changes
    print_status "Fetching latest changes from remote..."
    git fetch origin >> "$LOG_FILE" 2>&1
    
    # Check if target branch exists on remote
    if ! git ls-remote --heads origin "$UPDATE_BRANCH" | grep -q "$UPDATE_BRANCH"; then
        print_error "Branch '$UPDATE_BRANCH' not found on remote"
        print_error "Available branches:"
        git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^/  /'
        exit 1
    fi
    
    # Stash local changes if forcing update
    if [ "$(git status --porcelain)" ] && [ "$FORCE_UPDATE" = true ]; then
        print_warning "Stashing local changes..."
        git stash push -m "Auto-stash before update $(date)" >> "$LOG_FILE" 2>&1
    fi
    
    # Get current branch and commit
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    CURRENT_COMMIT=$(git rev-parse HEAD)
    
    print_status "Current branch: $CURRENT_BRANCH"
    print_status "Current commit: $CURRENT_COMMIT"
    
    # Switch to target branch if different
    if [ "$CURRENT_BRANCH" != "$UPDATE_BRANCH" ]; then
        print_status "Switching from $CURRENT_BRANCH to $UPDATE_BRANCH..."
        git checkout "$UPDATE_BRANCH" >> "$LOG_FILE" 2>&1
    fi
    
    # Pull latest changes
    print_status "Pulling latest changes..."
    git pull origin "$UPDATE_BRANCH" >> "$LOG_FILE" 2>&1
    
    NEW_COMMIT=$(git rev-parse HEAD)
    
    if [ "$CURRENT_COMMIT" = "$NEW_COMMIT" ]; then
        print_success "Already up to date"
        return 1  # Signal no changes
    else
        print_success "Updated from $CURRENT_COMMIT to $NEW_COMMIT"
        
        # Show what changed
        print_status "Changes in this update:"
        git log --oneline "$CURRENT_COMMIT..$NEW_COMMIT" | head -10
        
        return 0  # Signal changes were made
    fi
}

# Function to update Python dependencies
update_dependencies() {
    print_status "Updating Python dependencies..."
    
    cd "$PROJECT_DIR"
    
    if [ -f "requirements.txt" ]; then
        source venv/bin/activate
        pip install --upgrade pip >> "$LOG_FILE" 2>&1
        pip install -r requirements.txt --upgrade >> "$LOG_FILE" 2>&1
        deactivate
        print_success "Python dependencies updated"
    else
        print_warning "requirements.txt not found, skipping dependency update"
    fi
}

# Function to run database migrations
update_database() {
    print_status "Updating database..."
    
    cd "$PROJECT_DIR"
    
    # Backup database before migration
    if [ -f "device_states.db" ]; then
        cp "device_states.db" "device_states.db.pre-update"
        print_success "Database backed up before migration"
    fi
    
    # Run database initialization/migration
    source venv/bin/activate
    python3 -c "
try:
    from modules import db_operations
    db_operations.init_db()
    print('Database migration completed')
except Exception as e:
    print(f'Database migration failed: {e}')
    exit(1)
" >> "$LOG_FILE" 2>&1
    deactivate
    
    print_success "Database updated"
}

# Function to update configuration files
update_configuration() {
    print_status "Updating configuration files..."
    
    # Update systemd service if it exists
    if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
        print_status "Updating systemd service..."
        # Regenerate service file with current paths
        sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Gunicorn instance to serve DEWHOME Flask app
Documentation=https://github.com/dewanshDT/dewhome
After=network.target syslog.target multi-user.target systemd-udev-settle.service
Wants=network.target

[Service]
Type=notify
User=$UPDATE_USER
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
        
        sudo systemctl daemon-reload
        print_success "Systemd service updated"
    fi
    
    # Update nginx configuration if it exists
    if [ -f "/etc/nginx/sites-available/dewhome" ]; then
        print_status "Nginx configuration is current"
    fi
    
    print_success "Configuration updated"
}

# Function to set permissions
update_permissions() {
    print_status "Updating permissions..."
    
    # Set ownership
    sudo chown -R "$UPDATE_USER:gpio" "$PROJECT_DIR"
    
    # Set directory permissions
    find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
    
    # Set file permissions
    find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
    
    # Make scripts executable
    find "$PROJECT_DIR" -name "*.sh" -exec chmod +x {} \;
    
    # Set virtual environment permissions
    if [ -d "$PROJECT_DIR/venv" ]; then
        find "$PROJECT_DIR/venv/bin" -type f -exec chmod +x {} \;
    fi
    
    # Database permissions
    if [ -f "$PROJECT_DIR/device_states.db" ]; then
        chmod 664 "$PROJECT_DIR/device_states.db"
        chown "$UPDATE_USER:gpio" "$PROJECT_DIR/device_states.db"
    fi
    
    print_success "Permissions updated"
}

# Function to start services
start_services() {
    if [ "$NO_RESTART" = true ]; then
        print_status "Skipping service restart as requested"
        return 0
    fi
    
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
    
    # Wait a moment and check status
    sleep 3
    if sudo systemctl is-active --quiet ${SERVICE_NAME}.service; then
        print_success "DEWHOME service is running successfully"
    else
        print_warning "DEWHOME service may have issues"
        sudo systemctl status ${SERVICE_NAME}.service --no-pager -l
    fi
}

# Function to run tests
run_tests() {
    print_status "Running post-update tests..."
    
    # Test web interface
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
            print_success "Web interface is responding"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                print_warning "Web interface test failed after $max_attempts attempts"
            else
                print_status "Waiting for web interface... (attempt $attempt/$max_attempts)"
                sleep 2
            fi
        fi
        ((attempt++))
    done
    
    # Test GPIO access (if on Raspberry Pi)
    if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        if python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
try:
    from modules import gpio_control
    print('GPIO module loaded successfully')
except Exception as e:
    print(f'GPIO test failed: {e}')
    exit(1)
" >> "$LOG_FILE" 2>&1; then
            print_success "GPIO access test passed"
        else
            print_warning "GPIO access test failed"
        fi
    fi
}

# Function to display final information
show_final_info() {
    local ip_address=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    
    echo
    echo "======================================"
    echo -e "${GREEN}DEWHOME Update Complete!${NC}"
    echo "======================================"
    echo
    echo "🌐 Access your DEWHOME interface at:"
    echo "   http://$ip_address"
    echo "   http://$(hostname).local (if mDNS is enabled)"
    echo
    echo "📋 Useful Commands:"
    echo "   sudo systemctl status dewhome    # Check service status"
    echo "   sudo systemctl restart dewhome   # Restart service"
    echo "   sudo journalctl -u dewhome -f    # View logs"
    echo "   sudo systemctl restart nginx     # Restart web server"
    echo
    echo "👤 Updated for user: $UPDATE_USER"
    echo "🌿 Updated to branch: $UPDATE_BRANCH"
    echo "📁 Project location: $PROJECT_DIR"
    echo "💾 Backup location: $BACKUP_DIR"
    echo "📄 Update log: $LOG_FILE"
    echo
}

# Function to handle rollback
rollback() {
    print_error "Update failed! Rolling back..."
    
    if [ -d "$BACKUP_DIR" ]; then
        print_status "Restoring from backup..."
        rm -rf "$PROJECT_DIR"
        mv "$BACKUP_DIR" "$PROJECT_DIR"
        
        # Restart service with old version
        if [ "$NO_RESTART" != true ]; then
            sudo systemctl restart ${SERVICE_NAME}.service
        fi
        
        print_success "Rollback completed"
        print_status "Your previous version has been restored"
    else
        print_error "No backup found, cannot rollback automatically"
        print_error "Please restore manually or reinstall DEWHOME"
    fi
}

# Function to handle errors
error_handler() {
    local line_number=$1
    print_error "Update failed at line $line_number"
    print_error "Check the log file: $LOG_FILE"
    
    # Offer rollback
    if [ -d "$BACKUP_DIR" ] && [ "$NO_BACKUP" != true ]; then
        echo
        read -p "Would you like to rollback to the previous version? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        fi
    fi
    
    exit 1
}

# Main update function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Setup error handling
    trap 'error_handler $LINENO' ERR
    
    # Clear log file
    > "$LOG_FILE"
    
    echo "======================================"
    echo "DEWHOME Update Script"
    echo "======================================"
    echo
    
    print_status "Starting DEWHOME update..."
    print_status "Log file: $LOG_FILE"
    echo
    
    # Update steps
    print_status "Step 1/9: Setting up configuration..."
    setup_user_config
    
    print_status "Step 2/9: Checking prerequisites..."
    check_prerequisites
    
    print_status "Step 3/9: Creating backup..."
    backup_current
    
    print_status "Step 4/9: Stopping services..."
    stop_services
    
    print_status "Step 5/9: Updating repository..."
    if update_repository; then
        CHANGES_MADE=true
    else
        CHANGES_MADE=false
    fi
    
    if [ "$CHANGES_MADE" = true ]; then
        print_status "Step 6/9: Updating dependencies..."
        update_dependencies
        
        print_status "Step 7/9: Updating database..."
        update_database
        
        print_status "Step 8/9: Updating configuration..."
        update_configuration
        
        print_status "Step 9/9: Setting permissions..."
        update_permissions
    else
        print_status "No code changes detected, skipping dependency/database updates"
    fi
    
    print_status "Starting services..."
    start_services
    
    print_status "Running tests..."
    run_tests
    
    show_final_info
    
    if [ "$CHANGES_MADE" = true ]; then
        print_success "Update completed successfully!"
    else
        print_success "System was already up to date!"
    fi
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 