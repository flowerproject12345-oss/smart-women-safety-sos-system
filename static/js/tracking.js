/**
 * ShieldHer - Live Tracking Module
 * Handles real-time location tracking and sharing
 */

// Tracking state variables
let trackingActive = false;
let watchId = null;
let trackingSessionId = null;
let locationHistory = [];
let map = null;
let marker = null;
let pathCoordinates = [];
let polyline = null;

// Tracking settings
const TRACKING_CONFIG = {
  updateInterval: 5000, // 5 seconds between updates
  accuracyThreshold: 50, // Minimum accuracy in meters
  maxHistoryLength: 50, // Maximum location history points
  highAccuracy: true, // Use high accuracy GPS
  timeout: 10000, // 10 second timeout
  maximumAge: 0, // No cached locations
};

/**
 * Initialize tracking module
 */
function initTracking() {
  console.log("📍 Tracking module initialized");

  // Check if tracking was previously active
  checkTrackingStatus();

  // Initialize map if Google Maps is available
  if (typeof google !== "undefined") {
    initMap();
  }

  // Add event listeners for tracking buttons
  const startBtn = document.getElementById("startTrackingBtn");
  const stopBtn = document.getElementById("stopTrackingBtn");

  if (startBtn) {
    startBtn.addEventListener("click", startTracking);
  }
  if (stopBtn) {
    stopBtn.addEventListener("click", stopTracking);
  }
}

/**
 * Initialize Google Map
 */
function initMap() {
  const defaultLocation = { lat: 13.0827, lng: 80.2707 }; // Chennai

  map = new google.maps.Map(document.getElementById("trackingMap"), {
    center: defaultLocation,
    zoom: 15,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    styles: [
      {
        featureType: "poi",
        elementType: "labels",
        stylers: [{ visibility: "off" }],
      },
    ],
  });

  // Add custom marker icon
  const icon = {
    url: "/static/img/map-marker.png",
    scaledSize: new google.maps.Size(40, 40),
    origin: new google.maps.Point(0, 0),
    anchor: new google.maps.Point(20, 40),
  };

  marker = new google.maps.Marker({
    position: defaultLocation,
    map: map,
    icon: icon,
    title: "Your Location",
  });

  // Create polyline for path
  polyline = new google.maps.Polyline({
    path: pathCoordinates,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 3,
    map: map,
  });
}

/**
 * Start live tracking
 */
async function startTracking() {
  if (trackingActive) {
    showToast(
      "Tracking Active",
      "Location tracking is already active",
      "warning",
    );
    return;
  }

  if (!navigator.geolocation) {
    showToast(
      "Error",
      "Geolocation is not supported by your browser",
      "danger",
    );
    return;
  }

  try {
    // Start tracking session on server
    const response = await fetch("/api/tracking/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const result = await response.json();

    if (result.success) {
      trackingSessionId = result.session_id;
      trackingActive = true;

      // Start location watching
      watchId = navigator.geolocation.watchPosition(
        handleLocationUpdate,
        handleLocationError,
        {
          enableHighAccuracy: TRACKING_CONFIG.highAccuracy,
          timeout: TRACKING_CONFIG.timeout,
          maximumAge: TRACKING_CONFIG.maximumAge,
        },
      );

      // Update UI
      updateTrackingUI(true);

      // Show success message
      showToast(
        "📍 Live Tracking Started",
        "Your location is now being shared with your emergency contacts",
        "success",
      );

      // Log action
      logAction("tracking_started", { session_id: trackingSessionId });

      // Emit via Socket.IO
      if (window.socket) {
        window.socket.emit("start_tracking", {
          session_id: trackingSessionId,
        });
      }
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error("Start tracking error:", error);
    showToast("Error", "Could not start tracking. Please try again.", "danger");
  }
}

/**
 * Stop live tracking
 */
async function stopTracking() {
  if (!trackingActive) {
    return;
  }

  try {
    // Stop tracking session on server
    const response = await fetch("/api/tracking/stop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const result = await response.json();

    if (result.success) {
      // Clear location watch
      if (watchId) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
      }

      trackingActive = false;
      trackingSessionId = null;

      // Update UI
      updateTrackingUI(false);

      // Show success message
      showToast(
        "Tracking Stopped",
        "Location sharing has been turned off",
        "info",
      );

      // Log action
      logAction("tracking_stopped", {});

      // Emit via Socket.IO
      if (window.socket) {
        window.socket.emit("stop_tracking", {});
      }
    }
  } catch (error) {
    console.error("Stop tracking error:", error);
    showToast("Error", "Could not stop tracking", "danger");
  }
}

/**
 * Handle location update from GPS
 */
async function handleLocationUpdate(position) {
  const { latitude, longitude, accuracy, timestamp } = position.coords;

  // Check accuracy
  if (accuracy > TRACKING_CONFIG.accuracyThreshold) {
    console.log(`📍 Low accuracy: ${accuracy}m`);
  }

  // Update map
  updateMapLocation(latitude, longitude);

  // Add to path
  const latLng = new google.maps.LatLng(latitude, longitude);
  pathCoordinates.push(latLng);

  // Keep only last 100 points
  if (pathCoordinates.length > 100) {
    pathCoordinates.shift();
  }

  // Update polyline
  if (polyline) {
    polyline.setPath(pathCoordinates);
  }

  // Add to history
  const locationPoint = {
    latitude: latitude,
    longitude: longitude,
    accuracy: accuracy,
    timestamp: new Date(timestamp),
    address: null,
  };

  locationHistory.unshift(locationPoint);

  // Keep only last 50 points
  if (locationHistory.length > TRACKING_CONFIG.maxHistoryLength) {
    locationHistory.pop();
  }

  // Update history display
  updateLocationHistory();

  // Send to server
  try {
    const response = await fetch("/api/location/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        latitude: latitude,
        longitude: longitude,
        accuracy: accuracy,
        tracking_session_id: trackingSessionId,
      }),
    });

    const result = await response.json();

    // Update address if available
    if (result.address) {
      locationPoint.address = result.address;
      updateLocationHistory();
    }

    // Check safe zone alerts
    if (result.safe_zone_alerts && result.safe_zone_alerts.length > 0) {
      result.safe_zone_alerts.forEach((alert) => {
        showToast(
          "🏠 Safe Zone Alert",
          `You are near ${alert.zone_name} (${alert.distance}m away)`,
          "info",
        );
      });
    }

    // Emit via Socket.IO for real-time sharing
    if (window.socket && trackingActive) {
      window.socket.emit("location_update", {
        session_id: trackingSessionId,
        latitude: latitude,
        longitude: longitude,
        accuracy: accuracy,
        timestamp: new Date().toISOString(),
      });
    }
  } catch (error) {
    console.error("Server location update error:", error);
  }

  // Update location display in UI
  updateLocationDisplay(latitude, longitude, accuracy, timestamp);
}

/**
 * Update map with new location
 */
function updateMapLocation(latitude, longitude) {
  if (!map || !marker) return;

  const position = new google.maps.LatLng(latitude, longitude);
  marker.setPosition(position);
  map.setCenter(position);

  // Optional: Add accuracy circle
  if (window.accuracyCircle) {
    window.accuracyCircle.setMap(null);
  }

  window.accuracyCircle = new google.maps.Circle({
    center: position,
    radius: position.coords?.accuracy || 50,
    fillColor: "#FF0000",
    fillOpacity: 0.1,
    strokeColor: "#FF0000",
    strokeOpacity: 0.5,
    strokeWeight: 1,
    map: map,
  });
}

/**
 * Update location display in UI
 */
function updateLocationDisplay(latitude, longitude, accuracy, timestamp) {
  const locationDiv = document.getElementById("currentLocation");
  if (!locationDiv) return;

  const date = new Date(timestamp);
  const accuracyText =
    accuracy < 10
      ? "Excellent"
      : accuracy < 50
        ? "Good"
        : accuracy < 100
          ? "Fair"
          : "Poor";

  locationDiv.innerHTML = `
        <div class="location-info">
            <p><strong>📍 Current Location:</strong></p>
            <p>Latitude: ${latitude.toFixed(6)}</p>
            <p>Longitude: ${longitude.toFixed(6)}</p>
            <p>Accuracy: ${Math.round(accuracy)}m (${accuracyText})</p>
            <p>Last Update: ${date.toLocaleTimeString()}</p>
            <a href="https://maps.google.com/?q=${latitude},${longitude}" 
               target="_blank" class="btn btn-sm btn-primary mt-2">
                <i class="fas fa-external-link-alt"></i> Open in Google Maps
            </a>
        </div>
    `;
}

/**
 * Update location history display
 */
function updateLocationHistory() {
  const historyDiv = document.getElementById("locationHistory");
  if (!historyDiv) return;

  if (locationHistory.length === 0) {
    historyDiv.innerHTML =
      '<div class="text-center text-muted">No location history yet</div>';
    return;
  }

  historyDiv.innerHTML = locationHistory
    .slice(0, 10)
    .map(
      (loc) => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-map-pin text-danger"></i>
                    <strong>${loc.latitude.toFixed(6)}, ${loc.longitude.toFixed(6)}</strong>
                    ${loc.address ? `<br><small class="text-muted">${loc.address}</small>` : ""}
                </div>
                <small class="text-muted">${loc.timestamp.toLocaleTimeString()}</small>
            </div>
            <div class="mt-1">
                <span class="badge bg-secondary">Accuracy: ${Math.round(loc.accuracy)}m</span>
            </div>
        </div>
    `,
    )
    .join("");
}

/**
 * Handle location error
 */
function handleLocationError(error) {
  let message = "";

  switch (error.code) {
    case error.PERMISSION_DENIED:
      message =
        "❌ Location permission denied. Please enable location access in your browser settings.";
      break;
    case error.POSITION_UNAVAILABLE:
      message =
        "❌ Location information unavailable. Please check your GPS signal.";
      break;
    case error.TIMEOUT:
      message = "❌ Location request timed out. Please try again.";
      break;
    default:
      message = "❌ An unknown error occurred while getting your location.";
  }

  console.error("Location error:", message);
  showToast("Location Error", message, "danger");

  const locationDiv = document.getElementById("currentLocation");
  if (locationDiv) {
    locationDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
  }
}

/**
 * Update tracking UI elements
 */
function updateTrackingUI(isTracking) {
  const startBtn = document.getElementById("startTrackingBtn");
  const stopBtn = document.getElementById("stopTrackingBtn");
  const trackingStatus = document.getElementById("trackingStatus");

  if (startBtn) startBtn.disabled = isTracking;
  if (stopBtn) stopBtn.disabled = !isTracking;

  if (trackingStatus) {
    if (isTracking) {
      trackingStatus.innerHTML =
        '<span class="badge bg-success"><i class="fas fa-circle"></i> LIVE</span>';
      trackingStatus.classList.add("tracking-active");
    } else {
      trackingStatus.innerHTML =
        '<span class="badge bg-secondary">Offline</span>';
      trackingStatus.classList.remove("tracking-active");
    }
  }
}

/**
 * Check if tracking was previously active
 */
async function checkTrackingStatus() {
  try {
    const response = await fetch("/api/tracking/status");
    const data = await response.json();

    if (data.is_tracking) {
      trackingSessionId = data.session_id;
      startTracking();
    }
  } catch (error) {
    console.error("Check tracking status error:", error);
  }
}

/**
 * Share current tracking link
 */
function shareTrackingLink() {
  if (!trackingSessionId) {
    showToast("No Active Tracking", "Please start tracking first", "warning");
    return;
  }

  const shareUrl = `${window.location.origin}/share/track/${trackingSessionId}`;

  if (navigator.share) {
    navigator
      .share({
        title: "ShieldHer Live Tracking",
        text: "Track my location in real-time",
        url: shareUrl,
      })
      .catch((err) => console.log("Share cancelled:", err));
  } else {
    // Fallback: copy to clipboard
    navigator.clipboard.writeText(shareUrl);
    showToast("Link Copied", "Tracking link copied to clipboard", "success");
  }
}

/**
 * Get location statistics
 */
function getLocationStats() {
  if (locationHistory.length === 0) return null;

  const speeds = [];
  let totalDistance = 0;

  for (let i = 1; i < locationHistory.length; i++) {
    const prev = locationHistory[i - 1];
    const curr = locationHistory[i];

    const distance = calculateDistance(
      prev.latitude,
      prev.longitude,
      curr.latitude,
      curr.longitude,
    );

    totalDistance += distance;

    const timeDiff = (curr.timestamp - prev.timestamp) / 1000; // seconds
    if (timeDiff > 0) {
      speeds.push(distance / timeDiff); // meters per second
    }
  }

  const avgSpeed =
    speeds.length > 0 ? speeds.reduce((a, b) => a + b, 0) / speeds.length : 0;

  return {
    totalDistance: totalDistance,
    avgSpeed: avgSpeed,
    maxSpeed: Math.max(...speeds, 0),
    totalPoints: locationHistory.length,
    duration:
      locationHistory.length > 0
        ? (locationHistory[0].timestamp -
            locationHistory[locationHistory.length - 1].timestamp) /
          1000
        : 0,
  };
}

/**
 * Calculate distance between two points (Haversine formula)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", initTracking);

// Export functions for global use
window.startTracking = startTracking;
window.stopTracking = stopTracking;
window.shareTrackingLink = shareTrackingLink;
