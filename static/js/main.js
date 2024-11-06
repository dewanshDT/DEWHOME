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

// Function to toggle the device state
function toggleDevice(deviceId) {
  const button = document.getElementById("toggle-btn-" + deviceId)
  let currentState = button.getAttribute("data-state")

  // Determine the new action based on the current state
  let newAction = currentState === "1" ? "low" : "high"

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
        // alert(data.message);
        // Update the device state on the page
        const newState = newAction === "high" ? "1" : "0"
        button.setAttribute("data-state", newState)
        const stateLabel = document.getElementById("device-state-" + deviceId)
        // stateLabel.textContent = newAction.toUpperCase()
        stateLabel.className = newAction

        // Update the button text
        button.textContent = newAction === "high" ? "Turn Off" : "Turn On"

        // Update the button class
        if (newAction === "high") {
          button.classList.remove("off")
          button.classList.add("on")
        } else {
          button.classList.remove("on")
          button.classList.add("off")
        }
      } else {
        alert(data.error)
      }
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
      // Update the state display

      const stateLabel = document.getElementById("device-state-" + deviceId)
      // stateLabel.textContent = state.toUpperCase()
      stateLabel.className = state

      // Update the button state and text
      const button = document.getElementById("toggle-btn-" + deviceId)
      const newState = state === "high" ? "1" : "0"
      button.setAttribute("data-state", newState)
      button.textContent = state === "high" ? "Turn Off" : "Turn On"

      // Update the button class
      if (state === "high") {
        button.classList.add("on")
        button.classList.remove("off")
      } else {
        button.classList.add("off")
        button.classList.remove("on")
      }
    }
  })
  .catch((error) => console.error("Error fetching device states:", error))
