/**
 * ShieldHer - Emergency Contacts Module
 * Handles management of emergency contacts
 */

// Contacts state
let contacts = [];
let editingContactId = null;

// Contact validation patterns
const VALIDATION = {
  phone: /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/,
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
};

/**
 * Initialize contacts module
 */
function initContacts() {
  console.log("👥 Contacts module initialized");
  loadContacts();

  // Add event listeners
  const addForm = document.getElementById("addContactForm");
  if (addForm) {
    addForm.addEventListener("submit", handleAddContact);
  }

  // Add phone input formatting
  const phoneInput = document.getElementById("contactPhone");
  if (phoneInput) {
    phoneInput.addEventListener("input", formatPhoneNumber);
  }
}

/**
 * Load contacts from server
 */
async function loadContacts() {
  try {
    const response = await fetch("/api/contacts/get");
    contacts = await response.json();

    displayContacts();
    updateContactsCount();

    return contacts;
  } catch (error) {
    console.error("Load contacts error:", error);
    showToast("Error", "Could not load contacts", "danger");
  }
}

/**
 * Display contacts in UI
 */
function displayContacts() {
  const contactsList = document.getElementById("contactsList");
  if (!contactsList) return;

  if (contacts.length === 0) {
    contactsList.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-address-book fa-4x text-muted mb-3"></i>
                <p class="text-muted">No emergency contacts added yet.</p>
                <p class="small">Add your first contact to get started.</p>
            </div>
        `;
    return;
  }

  contactsList.innerHTML = contacts
    .map(
      (contact) => `
        <div class="card mb-3 contact-card" data-contact-id="${contact.id}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="contact-info">
                        <h6 class="mb-1">
                            <i class="fas ${getContactIcon(contact.relationship)}"></i>
                            ${escapeHtml(contact.name)}
                            ${contact.is_primary ? '<span class="badge bg-primary ms-2">Primary</span>' : ""}
                        </h6>
                        <p class="mb-0 small text-muted">
                            <i class="fas fa-phone-alt"></i> ${formatPhoneNumberDisplay(contact.phone)}
                        </p>
                        ${
                          contact.email
                            ? `
                            <p class="mb-0 small text-muted">
                                <i class="fas fa-envelope"></i> ${escapeHtml(contact.email)}
                            </p>
                        `
                            : ""
                        }
                        ${
                          contact.relationship
                            ? `
                            <p class="mb-0 small">
                                <i class="fas fa-heart text-danger"></i> ${escapeHtml(contact.relationship)}
                            </p>
                        `
                            : ""
                        }
                    </div>
                    <div class="contact-actions">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editContact(${contact.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteContact(${contact.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-success" onclick="testContact(${contact.id})">
                        <i class="fas fa-paper-plane"></i> Test Alert
                    </button>
                </div>
            </div>
        </div>
    `,
    )
    .join("");
}

/**
 * Get icon based on relationship
 */
function getContactIcon(relationship) {
  const icons = {
    Mother: "fa-female",
    Father: "fa-male",
    Sister: "fa-female",
    Brother: "fa-male",
    Friend: "fa-user-friends",
    Spouse: "fa-heart",
    Other: "fa-user",
  };
  return icons[relationship] || "fa-user";
}

/**
 * Handle add/edit contact form submission
 */
async function handleAddContact(event) {
  event.preventDefault();

  const name = document.getElementById("contactName")?.value.trim();
  const phone = document.getElementById("contactPhone")?.value.trim();
  const email = document.getElementById("contactEmail")?.value.trim();
  const relationship = document.getElementById("contactRelation")?.value;
  const isPrimary = document.getElementById("contactPrimary")?.checked || false;

  // Validation
  if (!name) {
    showToast("Validation Error", "Name is required", "warning");
    return;
  }

  if (!phone) {
    showToast("Validation Error", "Phone number is required", "warning");
    return;
  }

  if (!VALIDATION.phone.test(phone)) {
    showToast(
      "Validation Error",
      "Please enter a valid phone number",
      "warning",
    );
    return;
  }

  if (email && !VALIDATION.email.test(email)) {
    showToast(
      "Validation Error",
      "Please enter a valid email address",
      "warning",
    );
    return;
  }

  const contactData = {
    name: name,
    phone: phone,
    email: email,
    relationship: relationship,
    is_primary: isPrimary,
  };

  try {
    let response;

    if (editingContactId) {
      // Update existing contact
      response = await fetch(`/api/contacts/update/${editingContactId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(contactData),
      });
    } else {
      // Add new contact
      response = await fetch("/api/contacts/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(contactData),
      });
    }

    const result = await response.json();

    if (result.success) {
      showToast(
        editingContactId ? "Contact Updated" : "Contact Added",
        `${name} has been ${editingContactId ? "updated" : "added"} to your emergency contacts`,
        "success",
      );

      resetContactForm();
      loadContacts();
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error("Save contact error:", error);
    showToast(
      "Error",
      `Could not ${editingContactId ? "update" : "add"} contact`,
      "danger",
    );
  }
}

/**
 * Edit contact
 */
async function editContact(contactId) {
  const contact = contacts.find((c) => c.id === contactId);
  if (!contact) return;

  editingContactId = contactId;

  // Fill form with contact data
  document.getElementById("contactName").value = contact.name;
  document.getElementById("contactPhone").value = contact.phone;
  document.getElementById("contactEmail").value = contact.email || "";
  document.getElementById("contactRelation").value =
    contact.relationship || "Friend";

  const primaryCheckbox = document.getElementById("contactPrimary");
  if (primaryCheckbox) {
    primaryCheckbox.checked = contact.is_primary || false;
  }

  // Change button text
  const submitBtn = document.querySelector(
    '#addContactForm button[type="submit"]',
  );
  if (submitBtn) {
    submitBtn.innerHTML = '<i class="fas fa-save"></i> Update Contact';
  }

  // Add cancel button if not exists
  let cancelBtn = document.getElementById("cancelEditBtn");
  if (!cancelBtn) {
    cancelBtn = document.createElement("button");
    cancelBtn.id = "cancelEditBtn";
    cancelBtn.type = "button";
    cancelBtn.className = "btn btn-secondary w-100 mt-2";
    cancelBtn.innerHTML = '<i class="fas fa-times"></i> Cancel';
    cancelBtn.onclick = resetContactForm;
    document.querySelector("#addContactForm").appendChild(cancelBtn);
  } else {
    cancelBtn.style.display = "block";
  }

  // Scroll to form
  document
    .querySelector("#addContactForm")
    .scrollIntoView({ behavior: "smooth" });
}

/**
 * Delete contact
 */
async function deleteContact(contactId) {
  const contact = contacts.find((c) => c.id === contactId);
  if (!contact) return;

  if (
    !confirm(
      `Are you sure you want to remove ${contact.name} from your emergency contacts?`,
    )
  ) {
    return;
  }

  try {
    const response = await fetch(`/api/contacts/delete/${contactId}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (result.success) {
      showToast("Contact Deleted", `${contact.name} has been removed`, "info");
      loadContacts();
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error("Delete contact error:", error);
    showToast("Error", "Could not delete contact", "danger");
  }
}

/**
 * Test contact alert
 */
async function testContact(contactId) {
  const contact = contacts.find((c) => c.id === contactId);
  if (!contact) return;

  if (
    !confirm(
      `Send a test alert to ${contact.name}? This will send a test SMS/email.`,
    )
  ) {
    return;
  }

  try {
    const response = await fetch("/api/sos/send-alert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contact_id: contactId,
        test_mode: true,
      }),
    });

    const result = await response.json();

    if (result.success) {
      showToast(
        "Test Alert Sent",
        `Test alert sent to ${contact.name}`,
        "success",
      );
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error("Test alert error:", error);
    showToast("Error", "Could not send test alert", "danger");
  }
}

/**
 * Set primary contact
 */
async function setPrimaryContact(contactId) {
  try {
    const response = await fetch(`/api/contacts/set-primary/${contactId}`, {
      method: "POST",
    });

    const result = await response.json();

    if (result.success) {
      showToast(
        "Primary Contact Updated",
        "Your primary emergency contact has been updated",
        "success",
      );
      loadContacts();
    }
  } catch (error) {
    console.error("Set primary error:", error);
    showToast("Error", "Could not update primary contact", "danger");
  }
}

/**
 * Reset contact form
 */
function resetContactForm() {
  document.getElementById("addContactForm").reset();
  editingContactId = null;

  const submitBtn = document.querySelector(
    '#addContactForm button[type="submit"]',
  );
  if (submitBtn) {
    submitBtn.innerHTML = '<i class="fas fa-plus"></i> Add Contact';
  }

  const cancelBtn = document.getElementById("cancelEditBtn");
  if (cancelBtn) {
    cancelBtn.style.display = "none";
  }
}

/**
 * Format phone number as user types
 */
function formatPhoneNumber(event) {
  let input = event.target;
  let value = input.value.replace(/\D/g, "");

  if (value.length > 10) {
    value = value.slice(0, 10);
  }

  if (value.length > 6) {
    value = value.replace(/(\d{3})(\d{3})(\d{4})/, "($1) $2-$3");
  } else if (value.length > 3) {
    value = value.replace(/(\d{3})(\d+)/, "($1) $2");
  }

  input.value = value;
}

/**
 * Format phone number for display
 */
function formatPhoneNumberDisplay(phone) {
  if (!phone) return "";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  return phone;
}

/**
 * Update contacts count in UI
 */
function updateContactsCount() {
  const countElement = document.getElementById("contactsCount");
  if (countElement) {
    countElement.textContent = contacts.length;
  }
}

/**
 * Export contacts as JSON
 */
function exportContacts() {
  const dataStr = JSON.stringify(contacts, null, 2);
  const dataUri =
    "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

  const exportFileDefaultName = `shieldher_contacts_${new Date().toISOString().slice(0, 19)}.json`;

  const linkElement = document.createElement("a");
  linkElement.setAttribute("href", dataUri);
  linkElement.setAttribute("download", exportFileDefaultName);
  linkElement.click();

  showToast(
    "Contacts Exported",
    "Your contacts have been exported as JSON",
    "success",
  );
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", initContacts);

// Export functions for global use
window.editContact = editContact;
window.deleteContact = deleteContact;
window.testContact = testContact;
window.setPrimaryContact = setPrimaryContact;
window.exportContacts = exportContacts;
