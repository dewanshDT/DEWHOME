function controlDevice(deviceId, action) {
    fetch('/device', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            device_id: deviceId,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        // alert(data.message || data.error);
        // Update the device state on the page
        document.getElementById('device-state-' + deviceId).textContent = action.toUpperCase();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Fetch and display the initial device states
fetch('/devices')
    .then(response => response.json())
    .then(deviceStates => {
        for (const [deviceId, state] of Object.entries(deviceStates)) {
            document.getElementById('device-state-' + deviceId).textContent = state.toUpperCase();
        }
    })
    .catch(error => console.error('Error fetching device states:', error));
