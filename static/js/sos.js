/**
 * ShieldHer - SOS Functionality
 * Handles SOS button and alert system
 */

// SOS State
let sosActive = false;
let sosInterval = null;
let currentSOSId = null;

// SOS Settings
const SOS_HOLD_DURATION = 3000; // milliseconds
const SOS_UPDATE_INTERVAL = 5000; // 5 seconds

/**
 * Initialize SOS system
 */
function initSOS() {
  const sosBtn = document.getElementById("sosFloatingBtn");
  if (!sosBtn) return;

  // Add touch/click handlers
  let pressTimer = null;

  sosBtn.addEventListener("mousedown", () => {
    pressTimer = setTimeout(() => {
      triggerSOS();
    }, SOS_HOLD_DURATION);

    // Show countdown indicator
    showSOSCountdown();
  });

  sosBtn.addEventListener("mouseup", () => {
    if (pressTimer) {
      clearTimeout(pressTimer);
      hideSOSCountdown();
    }
  });

  sosBtn.addEventListener("mouseleave", () => {
    if (pressTimer) {
      clearTimeout(pressTimer);
      hideSOSCountdown();
    }
  });

  // Touch events for mobile
  sosBtn.addEventListener("touchstart", (e) => {
    e.preventDefault();
    pressTimer = setTimeout(() => {
      triggerSOS();
    }, SOS_HOLD_DURATION);
    showSOSCountdown();
  });

  sosBtn.addEventListener("touchend", () => {
    if (pressTimer) {
      clearTimeout(pressTimer);
      hideSOSCountdown();
    }
  });
}

/**
 * Show SOS countdown indicator
 */
function showSOSCountdown() {
  let countdown = 3;
  const countdownEl = document.createElement("div");
  countdownEl.id = "sosCountdown";
  countdownEl.className = "sos-countdown-overlay";
  countdownEl.innerHTML = `
        <div class="countdown-circle">
            <span class="countdown-number">${countdown}</span>
        </div>
        <div class="countdown-text">Hold for SOS</div>
    `;
  document.body.appendChild(countdownEl);

  const timer = setInterval(() => {
    countdown--;
    const numberEl = countdownEl.querySelector(".countdown-number");
    if (numberEl) {
      numberEl.textContent = countdown;
    }

    if (countdown <= 0) {
      clearInterval(timer);
      countdownEl.remove();
    }
  }, 1000);

  // Store timer for cleanup
  window.sosCountdownTimer = timer;
  window.sosCountdownEl = countdownEl;
}

/**
 * Hide SOS countdown indicator
 */
function hideSOSCountdown() {
  if (window.sosCountdownTimer) {
    clearInterval(window.sosCountdownTimer);
  }
  if (window.sosCountdownEl) {
    window.sosCountdownEl.remove();
  }
}

/**
 * Trigger SOS alert
 */
async function triggerSOS() {
  if (sosActive) {
    showToast("SOS Active", "SOS alert is already active", "warning");
    return;
  }

  if (
    !confirm(
      "🚨 EMERGENCY SOS! This will alert all your emergency contacts. Continue?",
    )
  ) {
    return;
  }

  try {
    // Get current location
    const location = await getCurrentLocation();

    // Show loading
    showToast(
      "Sending SOS",
      "Getting your location and notifying contacts...",
      "info",
    );

    // Send SOS to server
    const response = await fetch("/api/sos/trigger", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        latitude: location.latitude,
        longitude: location.longitude,
        accuracy: location.accuracy,
      }),
    });

    const result = await response.json();

    if (result.success) {
      sosActive = true;
      currentSOSId = result.sos_id;

      // Play alert sound
      playAlertSound();

      // Show success message
      showToast(
        "🚨 SOS Alert Sent!",
        `${result.contacts_notified} contacts notified. Help is on the way.`,
        "danger",
      );

      // Show location sharing modal
      showLocationSharingModal(location);

      // Start continuous location updates
      startContinuousLocationUpdates();

      // Log action
      logAction("sos_triggered", {
        sos_id: result.sos_id,
        latitude: location.latitude,
        longitude: location.longitude,
      });
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error("SOS trigger error:", error);
    showToast(
      "SOS Failed",
      "Could not send SOS. Please check your connection.",
      "danger",
    );
  }
}

/**
 * Start continuous location updates for active SOS
 */
function startContinuousLocationUpdates() {
  if (sosInterval) {
    clearInterval(sosInterval);
  }

  sosInterval = setInterval(async () => {
    if (!sosActive) {
      clearInterval(sosInterval);
      return;
    }

    try {
      const location = await getCurrentLocation();

      // Update location on server
      await fetch("/api/location/update", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude: location.latitude,
          longitude: location.longitude,
          accuracy: location.accuracy,
          sos_id: currentSOSId,
        }),
      });

      // Emit via socket for real-time tracking
      if (window.socket) {
        window.socket.emit("location_update", {
          sos_id: currentSOSId,
          latitude: location.latitude,
          longitude: location.longitude,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error("Location update error:", error);
    }
  }, SOS_UPDATE_INTERVAL);
}

/**
 * Stop continuous location updates
 */
function stopContinuousLocationUpdates() {
  if (sosInterval) {
    clearInterval(sosInterval);
    sosInterval = null;
  }
}

/**
 * Show location sharing modal
 */
function showLocationSharingModal(location) {
  const modal = document.createElement("div");
  modal.className = "modal fade";
  modal.id = "locationModal";
  modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-location-dot"></i> Location Shared
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-3">
                        <i class="fas fa-check-circle fa-4x text-success"></i>
                    </div>
                    <p>Your location has been shared with your emergency contacts.</p>
                    <div class="alert alert-info">
                        <strong>📍 Location:</strong><br>
                        Latitude: ${location.latitude.toFixed(6)}<br>
                        Longitude: ${location.longitude.toFixed(6)}<br>
                        Accuracy: ${Math.round(location.accuracy)} meters
                    </div>
                    <a href="https://maps.google.com/?q=${location.latitude},${location.longitude}" 
                       target="_blank" class="btn btn-primary w-100">
                        <i class="fas fa-map"></i> View on Google Maps
                    </a>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-success" onclick="resolveSOS()">
                        <i class="fas fa-check"></i> I'm Safe
                    </button>
                </div>
            </div>
        </div>
    `;

  document.body.appendChild(modal);
  const modalInstance = new bootstrap.Modal(modal);
  modalInstance.show();

  // Remove modal from DOM when hidden
  modal.addEventListener("hidden.bs.modal", () => {
    modal.remove();
  });
}

/**
 * Resolve active SOS
 */
async function resolveSOS() {
  if (!currentSOSId) {
    return;
  }

  if (
    !confirm(
      "Are you safe? This will notify your contacts that the emergency is over.",
    )
  ) {
    return;
  }

  try {
    const response = await fetch(`/api/sos/resolve/${currentSOSId}`, {
      method: "POST",
    });

    const result = await response.json();

    if (result.success) {
      sosActive = false;
      stopContinuousLocationUpdates();
      currentSOSId = null;

      showToast(
        "SOS Resolved",
        "Your contacts have been notified that you are safe.",
        "success",
      );

      // Close any open modals
      const modals = document.querySelectorAll(".modal");
      modals.forEach((modal) => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
          modalInstance.hide();
        }
      });
    }
  } catch (error) {
    console.error("Error resolving SOS:", error);
    showToast("Error", "Could not resolve SOS", "danger");
  }
}

/**
 * Get current location with promise
 */
function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation not supported"));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        });
      },
      (error) => {
        reject(new Error(error.message));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  });
}

/**
 * Play alert sound
 */
function playAlertSound() {
  try {
    const audio = new Audio("/static/audio/sos_alarm.mp3");
    audio.play().catch((e) => console.log("Audio play failed:", e));
  } catch (e) {
    console.log("Audio not supported");
  }

  // Vibrate pattern for SOS
  if (navigator.vibrate) {
    navigator.vibrate([200, 100, 200, 100, 200, 100, 500]);
  }
}

/**
 * Log action to server
 */
async function logAction(actionType, details) {
  try {
    await fetch("/api/log-action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        action_type: actionType,
        details: details,
      }),
    });
  } catch (error) {
    console.error("Log action error:", error);
  }
}

/**
 * Show toast notification
 */
function showToast(title, message, type = "info") {
  if (window.ShieldHer && window.ShieldHer.showToast) {
    window.ShieldHer.showToast(title, message, type);
  } else {
    console.log(`${title}: ${message}`);
  }
}

// Initialize SOS when DOM is ready
document.addEventListener("DOMContentLoaded", initSOS);

// Export functions for global use
window.triggerSOS = triggerSOS;
window.resolveSOS = resolveSOS;
