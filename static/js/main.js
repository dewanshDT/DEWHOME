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

// Existing JavaScript Code
function controlDevice(deviceId, action) {
  fetch("/device", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: deviceId,
      action: action,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message || data.error)
      // Update the device state on the page
      document.getElementById("device-state-" + deviceId).textContent =
        action.toUpperCase()
    })
    .catch((error) => {
      console.error("Error:", error)
    })
}

// Fetch and display the initial device states
fetch("/devices")
  .then((response) => response.json())
  .then((deviceStates) => {
    for (const [deviceId, state] of Object.entries(deviceStates)) {
      document.getElementById("device-state-" + deviceId).textContent =
        state.toUpperCase()
    }
  })
  .catch((error) => console.error("Error fetching device states:", error))
