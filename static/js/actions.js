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

  console.log("%cDEWHOME - Actions", styleTitle)
  console.log("%cDeveloped by Dewansh", styleSubtitle)
  console.log("%chttps://dewansh.space", styleLink)
  console.log("%cWelcome to the DEWHOME actions console!", styleMessage)
})()

// Global variables
let availableDevices = [];
let confirmCallback = null;
let deviceActionCount = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  loadAvailableDevices();
  setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
  // Add action form submission
  document.getElementById('addActionForm').addEventListener('submit', handleAddAction);
  
  // Action type change
  document.getElementById('actionType').addEventListener('change', updateScheduleInput);
  
  // Modal close on outside click
  window.addEventListener('click', function(event) {
    const addModal = document.getElementById('addActionModal');
    const confirmModal = document.getElementById('confirmModal');
    
    if (event.target === addModal) {
      closeAddActionModal();
    }
    if (event.target === confirmModal) {
      closeConfirmModal();
    }
  });
}

// Load available devices for action creation
async function loadAvailableDevices() {
  try {
    const response = await fetch('/devices');
    availableDevices = await response.json();
  } catch (error) {
    console.error('Error loading devices:', error);
    showNotification('Error loading devices', 'error');
  }
}

// Modal functions
function openAddActionModal() {
  document.getElementById('addActionModal').style.display = 'block';
  loadAvailableDevices(); // Refresh available devices
  addDeviceAction(); // Add first device action by default
}

function closeAddActionModal() {
  document.getElementById('addActionModal').style.display = 'none';
  document.getElementById('addActionForm').reset();
  // Clear device actions
  const container = document.getElementById('deviceActions');
  container.innerHTML = '';
  deviceActionCount = 0;
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

// Update schedule input based on action type
function updateScheduleInput() {
  const actionType = document.getElementById('actionType').value;
  const scheduleInput = document.getElementById('actionSchedule');
  const scheduleHelp = document.getElementById('scheduleHelp');
  
  switch (actionType) {
    case 'timer':
      scheduleInput.placeholder = '30 7 * * 1-5';
      scheduleHelp.innerHTML = '<strong>Cron Format:</strong> minute hour day month day_of_week<br>Examples: "30 7 * * 1-5" (7:30 AM weekdays), "0 20 * * *" (8:00 PM daily)';
      break;
    case 'countdown':
      scheduleInput.placeholder = '30m';
      scheduleHelp.innerHTML = '<strong>Countdown Format:</strong> time + unit<br>Examples: "30m" (30 minutes), "2h" (2 hours), "1d" (1 day)';
      break;
    case 'interval':
      scheduleInput.placeholder = '5m';
      scheduleHelp.innerHTML = '<strong>Interval Format:</strong> time + unit<br>Examples: "30s" (every 30 seconds), "5m" (every 5 minutes), "1h" (every hour)';
      break;
  }
}

// Add device action to form
function addDeviceAction() {
  const container = document.getElementById('deviceActions');
  const deviceActionId = `deviceAction_${deviceActionCount++}`;
  
  const deviceActionDiv = document.createElement('div');
  deviceActionDiv.className = 'device-action-item';
  deviceActionDiv.id = deviceActionId;
  
  deviceActionDiv.innerHTML = `
    <div class="device-action-header">
      <h4>Device Action ${deviceActionCount}</h4>
      <button type="button" class="btn btn-danger btn-sm" onclick="removeDeviceAction('${deviceActionId}')">
        <i class="fas fa-trash"></i>
      </button>
    </div>
    <div class="device-action-fields">
      <div class="form-group">
        <label>Device:</label>
        <select class="device-select" name="deviceId" required>
          <option value="">Select a device...</option>
          ${availableDevices.map(device => 
            `<option value="${device.id}">${device.name} (Pin ${device.pin_number})</option>`
          ).join('')}
        </select>
      </div>
      <div class="form-group">
        <label>Action:</label>
        <select class="action-select" name="actionType" required>
          <option value="high">Turn On</option>
          <option value="low">Turn Off</option>
          <option value="toggle">Toggle</option>
        </select>
      </div>
      <div class="form-group">
        <label>Delay (seconds):</label>
        <input type="number" class="delay-input" name="delaySeconds" min="0" value="0" placeholder="0">
      </div>
    </div>
  `;
  
  container.appendChild(deviceActionDiv);
}

// Remove device action from form
function removeDeviceAction(deviceActionId) {
  const element = document.getElementById(deviceActionId);
  if (element) {
    element.remove();
  }
}

// Handle add action form submission
async function handleAddAction(event) {
  event.preventDefault();
  
  const formData = new FormData(event.target);
  const actionData = {
    name: formData.get('actionName'),
    type: formData.get('actionType'),
    schedule: formData.get('actionSchedule'),
    device_actions: []
  };
  
  // Collect device actions
  const deviceActionItems = document.querySelectorAll('.device-action-item');
  deviceActionItems.forEach(item => {
    const deviceId = item.querySelector('.device-select').value;
    const actionType = item.querySelector('.action-select').value;
    const delaySeconds = parseInt(item.querySelector('.delay-input').value) || 0;
    
    if (deviceId && actionType) {
      actionData.device_actions.push({
        device_id: parseInt(deviceId),
        action_type: actionType,
        delay_seconds: delaySeconds
      });
    }
  });
  
  if (actionData.device_actions.length === 0) {
    showNotification('Please add at least one device action', 'error');
    return;
  }
  
  try {
    const response = await fetch('/actions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(actionData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showNotification(`Action "${actionData.name}" created successfully!`, 'success');
      closeAddActionModal();
      location.reload(); // Refresh the page to show new action
    } else {
      showNotification(result.error || 'Failed to create action', 'error');
    }
  } catch (error) {
    console.error('Error creating action:', error);
    showNotification('Failed to create action', 'error');
  }
}

// Toggle action enabled/disabled
async function toggleAction(actionId) {
  try {
    const response = await fetch(`/actions/${actionId}/toggle`, {
      method: 'POST'
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showNotification(result.message, 'success');
      location.reload(); // Refresh to show updated state
    } else {
      showNotification(result.error || 'Failed to toggle action', 'error');
    }
  } catch (error) {
    console.error('Error toggling action:', error);
    showNotification('Failed to toggle action', 'error');
  }
}

// Execute action immediately
async function executeAction(actionId) {
  try {
    const response = await fetch(`/actions/${actionId}/execute`, {
      method: 'POST'
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showNotification(result.message, 'success');
    } else {
      showNotification(result.error || 'Failed to execute action', 'error');
    }
  } catch (error) {
    console.error('Error executing action:', error);
    showNotification('Failed to execute action', 'error');
  }
}

// Delete action function
function deleteAction(actionId) {
  const actionCard = document.querySelector(`[data-action-id="${actionId}"]`);
  const actionName = actionCard.querySelector('.action-title').textContent.trim();
  
  openConfirmModal(
    `Are you sure you want to delete "${actionName}"? This action cannot be undone.`,
    async function() {
      try {
        const response = await fetch(`/actions/${actionId}`, {
          method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
          showNotification(`Action "${actionName}" deleted successfully!`, 'success');
          actionCard.remove();
        } else {
          showNotification(result.error || 'Failed to delete action', 'error');
        }
      } catch (error) {
        console.error('Error deleting action:', error);
        showNotification('Failed to delete action', 'error');
      }
    }
  );
}

// Show notification function
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
      <span>${message}</span>
    </div>
    <button class="notification-close" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  // Add to page
  document.body.appendChild(notification);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
  
  // Animate in
  setTimeout(() => {
    notification.classList.add('show');
  }, 100);
}

// Initialize schedule input on page load
document.addEventListener('DOMContentLoaded', function() {
  updateScheduleInput();
}); 