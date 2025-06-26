// Custom Console Message
;(function () {
  const styleTitle = [
    "font-size: 16px",
    "font-weight: bold",
    "color: #2E86C1",
    "text-shadow: 1px 1px 0px #fff, 1px 1px 0px rgba(0,0,0,0.1)",
    "padding: 4px 0",
  ].join(";")

  const styleSubtitle = [
    "font-size: 12px",
    "color: #566573",
    "padding: 2px 0",
  ].join(";")

  const styleLink = [
    "font-size: 12px",
    "color: #2874A6",
    "text-decoration: underline",
    "padding: 2px 0",
  ].join(";")

  const styleMessage = [
    "font-size: 12px",
    "color: #1C2833",
    "padding: 2px 0",
  ].join(";")

  console.log("%cDEWHOME", styleTitle)
  console.log("%cDeveloped by Dewansh", styleSubtitle)
  console.log("%chttps://dewansh.space", styleLink)
  console.log("%cWelcome to the DEWHOME application console!", styleMessage)
})()

// Global variables
let availablePins = [];
let confirmCallback = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  loadUsablePins();
  loadInitialDeviceStates();
  setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
  // Add device form submission
  document.getElementById('addDeviceForm').addEventListener('submit', handleAddDevice);
  
  // Pin selection change
  document.getElementById('devicePin').addEventListener('change', handlePinSelection);
  
  // Modal close on outside click
  window.addEventListener('click', function(event) {
    const addModal = document.getElementById('addDeviceModal');
    const confirmModal = document.getElementById('confirmModal');
    
    if (event.target === addModal) {
      closeAddDeviceModal();
    }
    if (event.target === confirmModal) {
      closeConfirmModal();
    }
  });
}

// Load available pins for device creation
async function loadUsablePins() {
  try {
    const response = await fetch('/pins/usable');
    availablePins = await response.json();
    populatePinDropdown();
  } catch (error) {
    console.error('Error loading pins:', error);
    showNotification('Error loading GPIO pins', 'error');
  }
}

// Populate the pin dropdown
function populatePinDropdown() {
  const pinSelect = document.getElementById('devicePin');
  const defaultOption = pinSelect.querySelector('option[value=""]');
  pinSelect.innerHTML = '';
  pinSelect.appendChild(defaultOption);
  
  availablePins.forEach(pin => {
    const option = document.createElement('option');
    option.value = pin.pin_number;
    option.textContent = `Pin ${pin.pin_number} - ${pin.type} (${pin.category.toUpperCase()})`;
    option.dataset.category = pin.category;
    option.dataset.description = pin.description;
    pinSelect.appendChild(option);
  });
}

// Handle pin selection and show pin information
function handlePinSelection() {
  const pinSelect = document.getElementById('devicePin');
  const pinInfo = document.getElementById('pinInfo');
  const selectedOption = pinSelect.selectedOptions[0];
  
  if (selectedOption && selectedOption.value) {
    const category = selectedOption.dataset.category;
    const description = selectedOption.dataset.description;
    
    let infoHTML = `<strong>Pin Information:</strong><br>${description}`;
    
    // Add warnings for special pins
    if (category === 'i2c') {
      infoHTML += '<div class="pin-warning">⚠️ Warning: This is an I2C pin. Only use if I2C is not needed.</div>';
    } else if (category === 'uart') {
      infoHTML += '<div class="pin-warning">⚠️ Warning: This is a UART pin. Only use if serial console is disabled.</div>';
    } else if (category === 'spi') {
      infoHTML += '<div class="pin-warning">⚠️ Warning: This is an SPI pin. Only use if SPI is not needed.</div>';
    }
    
    pinInfo.innerHTML = infoHTML;
    pinInfo.classList.add('show');
  } else {
    pinInfo.classList.remove('show');
  }
}

// Modal functions
function openAddDeviceModal() {
  document.getElementById('addDeviceModal').style.display = 'block';
  loadUsablePins(); // Refresh available pins
}

function closeAddDeviceModal() {
  document.getElementById('addDeviceModal').style.display = 'none';
  document.getElementById('addDeviceForm').reset();
  document.getElementById('pinInfo').classList.remove('show');
}

function openConfirmModal(message, callback) {
  document.getElementById('confirmMessage').textContent = message;
  document.getElementById('confirmModal').style.display = 'block';
  confirmCallback = callback;
}

function closeConfirmModal() {
  document.getElementById('confirmModal').style.display = 'none';
  confirmCallback = null;
}

// Handle confirm button click
document.getElementById('confirmButton').addEventListener('click', function() {
  if (confirmCallback) {
    confirmCallback();
  }
  closeConfirmModal();
});

// Handle add device form submission
async function handleAddDevice(event) {
  event.preventDefault();
  
  const formData = new FormData(event.target);
  const deviceData = {
    name: formData.get('deviceName'),
    icon: formData.get('deviceIcon'),
    pin_number: parseInt(formData.get('devicePin'))
  };
  
  try {
    const response = await fetch('/devices', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(deviceData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showNotification(`Device "${deviceData.name}" added successfully!`, 'success');
      closeAddDeviceModal();
      location.reload(); // Refresh the page to show new device
    } else {
      showNotification(result.error || 'Failed to add device', 'error');
    }
  } catch (error) {
    console.error('Error adding device:', error);
    showNotification('Failed to add device', 'error');
  }
}

// Delete device function
function deleteDevice(deviceId) {
  const deviceCard = document.querySelector(`[data-device-id="${deviceId}"]`);
  const deviceName = deviceCard.querySelector('.device-title').textContent.trim();
  
  openConfirmModal(
    `Are you sure you want to delete "${deviceName}"? This action cannot be undone.`,
    async function() {
      try {
        const response = await fetch(`/devices/${deviceId}`, {
          method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
          showNotification(`Device "${deviceName}" deleted successfully!`, 'success');
          deviceCard.remove();
        } else {
          showNotification(result.error || 'Failed to delete device', 'error');
        }
      } catch (error) {
        console.error('Error deleting device:', error);
        showNotification('Failed to delete device', 'error');
      }
    }
  );
}

// Toggle device function
function toggleDevice(deviceId) {
  const button = document.getElementById("toggle-btn-" + deviceId);
  let currentState = button.getAttribute("data-state");
  let newAction = currentState === "1" ? "low" : "high";

  fetch("/device", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: deviceId,
      action: newAction,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message) {
        // Update the device state on the page
        const newState = newAction === "high" ? "1" : "0";
        button.setAttribute("data-state", newState);
        const stateLabel = document.getElementById("device-state-" + deviceId);
        stateLabel.className = newAction;

        // Update the button text
        button.textContent = newAction === "high" ? "Turn Off" : "Turn On";

        // Update the button class
        if (newAction === "high") {
          button.classList.remove("off");
          button.classList.add("on");
        } else {
          button.classList.remove("on");
          button.classList.add("off");
        }
      } else {
        showNotification(data.error || 'Failed to control device', 'error');
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification('Failed to control device', 'error');
    });
}

// Load initial device states
function loadInitialDeviceStates() {
  fetch("/devices")
    .then((response) => response.json())
    .then((devices) => {
      devices.forEach(device => {
        const stateLabel = document.getElementById("device-state-" + device.id);
        if (stateLabel) {
          stateLabel.className = device.state;
        }

        const button = document.getElementById("toggle-btn-" + device.id);
        if (button) {
          const newState = device.state === "high" ? "1" : "0";
          button.setAttribute("data-state", newState);
          button.textContent = device.state === "high" ? "Turn Off" : "Turn On";

          if (device.state === "high") {
            button.classList.add("on");
            button.classList.remove("off");
          } else {
            button.classList.add("off");
            button.classList.remove("on");
          }
        }
      });
    })
    .catch((error) => {
      console.error("Error fetching device states:", error);
      showNotification('Failed to load device states', 'error');
    });
}

// Show notification function
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Add styles
  notification.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 20px;
    padding: 12px 20px;
    border-radius: 6px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    opacity: 0;
    transition: opacity 0.3s ease;
    max-width: 300px;
    word-wrap: break-word;
  `;
  
  // Set background color based on type
  switch (type) {
    case 'success':
      notification.style.backgroundColor = '#28a745';
      break;
    case 'error':
      notification.style.backgroundColor = '#dc3545';
      break;
    case 'warning':
      notification.style.backgroundColor = '#ffc107';
      notification.style.color = 'black';
      break;
    default:
      notification.style.backgroundColor = '#17a2b8';
  }
  
  // Add to document
  document.body.appendChild(notification);
  
  // Fade in
  setTimeout(() => {
    notification.style.opacity = '1';
  }, 100);
  
  // Remove after 5 seconds
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);
}
