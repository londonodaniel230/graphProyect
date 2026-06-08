// UI component for displaying status messages and error lists.
// Updates in real-time as operations succeed or fail.
export class StatusPanel {
  constructor(statusEl, errorsEl) {
    this.statusEl = statusEl;
    this.errorsEl = errorsEl;
  }

  // Displays a status message in the status element.
  setStatus(message) {
    if (this.statusEl) {
      this.statusEl.textContent = message || "";
    }
  }

  // Clears all error messages from the errors list.
  clearErrors() {
    if (!this.errorsEl) {
      return;
    }
    this.errorsEl.innerHTML = "";
  }

  // Displays an array of error messages as list items.
  showErrors(messages) {
    if (!this.errorsEl) {
      return;
    }

    this.clearErrors();
    (messages || []).forEach((message) => {
      const item = document.createElement("li");
      item.textContent = message;
      this.errorsEl.appendChild(item);
    });
  }
}
