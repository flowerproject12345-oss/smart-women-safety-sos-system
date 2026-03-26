/**
 * ShieldHer - Main JavaScript File
 * Core functionality for the Smart Women Safety SOS System
 */

// Global variables
let socket = null;
let currentUser = null;
let locationWatchId = null;
let notificationPermission = false;

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  console.log("🛡️ ShieldHer initialized");

  // Initialize Socket.IO connection
  initSocket();

  // Request notification permission
  requestNotificationPermission();

  // Check authentication status
  checkAuthStatus();

  // Initialize tooltips
  initTooltips();
});

/**
 * Initialize Socket.IO connection for real-time features
 */
function initSocket() {
  socket = io();

  socket.on("connect", function () {
    console.log("🔌 Connected to ShieldHer server");
    showToast("Connected", "Real-time features are active", "success");
  });

  socket.on("disconnect", function () {
    console.log("🔌 Disconnected from server");
    showToast("Disconnected", "Real-time features unavailable", "warning");
  });

  socket.on("sos_alert", function (data) {
    console.log("🚨 SOS Alert received:", data);
    showToast("🚨 SOS Alert", `${data.username} needs help!`, "danger");

    // Play alert sound
    playAlertSound();
  });

  socket.on("location_updated", function (data) {
    console.log("📍 Location update:", data);

    // Update map if available
    if (window.updateMapLocation) {
      window.updateMapLocation(data.latitude, data.longitude);
    }
  });

  socket.on("tracking_started", function (data) {
    showToast("📍 Tracking Started", data.message, "info");
  });

  socket.on("tracking_stopped", function (data) {
    showToast("📍 Tracking Stopped", data.message, "info");
  });
}

/**
 * Request notification permission
 */
function requestNotificationPermission() {
  if ("Notification" in window) {
    Notification.requestPermission().then(function (permission) {
      notificationPermission = permission === "granted";
      if (notificationPermission) {
        console.log("📢 Notifications enabled");
      }
    });
  }
}

/**
 * Show browser notification
 */
function showNotification(title, body, icon = "/static/img/logo.png") {
  if (notificationPermission && "Notification" in window) {
    new Notification(title, { body: body, icon: icon });
  }
}

/**
 * Show toast notification
 */
function showToast(title, message, type = "info") {
  const toast = document.createElement("div");
  toast.className = "toast-notification";

  const bgColor =
    {
      success: "#28a745",
      danger: "#dc3545",
      warning: "#ffc107",
      info: "#17a2b8",
    }[type] || "#6c757d";

  toast.innerHTML = `
        <div class="toast-header" style="background: ${bgColor}; color: white;">
            <strong>${title}</strong>
            <button type="button" class="btn-close btn-close-white ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;

  document.body.appendChild(toast);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.remove();
    }
  }, 5000);
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

  // Vibrate if supported
  if (navigator.vibrate) {
    navigator.vibrate([200, 100, 200, 100, 200]);
  }
}

/**
 * Check authentication status
 */
async function checkAuthStatus() {
  try {
    const response = await fetch("/api/auth/me");
    const data = await response.json();

    if (data.success) {
      currentUser = data.user;
      console.log("👤 Logged in as:", currentUser.username);
      updateUIForLoggedInUser();
    } else {
      console.log("🔓 Not logged in");
      showLoginPrompt();
    }
  } catch (error) {
    console.error("Auth check error:", error);
  }
}

/**
 * Update UI for logged in user
 */
function updateUIForLoggedInUser() {
  // Update welcome message
  const welcomeElements = document.querySelectorAll(".welcome-user");
  welcomeElements.forEach((el) => {
    el.textContent = currentUser.full_name || currentUser.username;
  });

  // Show user avatar
  const avatarElements = document.querySelectorAll(".user-avatar");
  avatarElements.forEach((el) => {
    el.innerHTML = `<i class="fas fa-user-circle"></i> ${currentUser.username}`;
  });
}

/**
 * Show login prompt
 */
function showLoginPrompt() {
  // Optional: Show login modal or redirect
  console.log("Please login to access full features");
}

/**
 * Get current location
 */
async function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject("Geolocation not supported");
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
        reject(error.message);
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
 * Format timestamp
 */
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

/**
 * Format distance in meters
 */
function formatDistance(meters) {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  } else {
    return `${(meters / 1000).toFixed(1)}km`;
  }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Copied!", "Text copied to clipboard", "success");
  } catch (err) {
    console.error("Failed to copy:", err);
    showToast("Error", "Failed to copy text", "danger");
  }
}

/**
 * Share location using Web Share API
 */
async function shareLocation(latitude, longitude, address) {
  const shareData = {
    title: "📍 My Location - ShieldHer",
    text: `I'm at: ${address || `${latitude}, ${longitude}`}`,
    url: `https://maps.google.com/?q=${latitude},${longitude}`,
  };

  if (navigator.share) {
    try {
      await navigator.share(shareData);
      showToast("Shared!", "Location shared successfully", "success");
    } catch (err) {
      console.log("Share cancelled:", err);
    }
  } else {
    // Fallback: copy to clipboard
    copyToClipboard(shareData.url);
  }
}

// Export functions for use in other scripts
window.ShieldHer = {
  showToast,
  showNotification,
  getCurrentLocation,
  formatTimestamp,
  formatDistance,
  escapeHtml,
  copyToClipboard,
  shareLocation,
};
