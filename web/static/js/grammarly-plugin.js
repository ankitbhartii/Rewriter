// Grammarly Web Component Plugin (matches @grammarly/editor-sdk architecture)

class GrammarlyEditorPlugin extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.targetInput = null;
    this.suggestions = [];
    this.currentScore = 100;
    this.debounceTimer = null;
  }

  connectedCallback() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: inline-block;
          position: relative;
          width: 100%;
        }
        .g-floating-widget {
          position: absolute;
          bottom: 12px;
          right: 12px;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #ffffff;
          border: 2px solid #15C39A;
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          font-weight: 800;
          font-size: 14px;
          color: #15C39A;
          cursor: pointer;
          z-index: 1000;
          user-select: none;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .g-floating-widget:hover {
          transform: scale(1.1);
          box-shadow: 0 4px 12px rgba(21, 195, 154, 0.4);
        }
        .g-badge {
          position: absolute;
          top: -4px;
          right: -4px;
          background: #ef4444;
          color: white;
          font-size: 10px;
          font-weight: bold;
          border-radius: 50%;
          width: 16px;
          height: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 1.5px solid #ffffff;
        }
        .g-badge.clean {
          background: #15C39A;
        }
        .g-quick-popup {
          position: absolute;
          bottom: 48px;
          right: 0;
          width: 280px;
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
          padding: 12px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          z-index: 1001;
          display: none;
        }
        .g-popup-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 11px;
          font-weight: 700;
          color: #ef4444;
          text-transform: uppercase;
          margin-bottom: 6px;
        }
        .g-fix-btn {
          width: 100%;
          background: #e8f9f5;
          color: #0c6a53;
          border: 1px solid #15C39A;
          padding: 6px 10px;
          border-radius: 6px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 8px;
        }
        .g-fix-btn:hover {
          background: #15C39A;
          color: white;
        }
      </style>
      <slot></slot>
      <div class="g-floating-widget" id="widgetBtn" title="Grammarly Assistant">
        <span>G</span>
        <div class="g-badge clean" id="badgeEl">✓</div>
      </div>
      <div class="g-quick-popup" id="quickPopup">
        <div class="g-popup-header">
          <span id="popupCategory">Grammar Issue</span>
          <span style="cursor:pointer;color:#94a3b8;" id="closePopup">✕</span>
        </div>
        <div id="popupMsg" style="font-size:12px;color:#475569;margin-bottom:6px;">Check suggestions</div>
        <button class="g-fix-btn" id="fixBtn">
          <span id="fixText">Accept Fix</span>
          <span>✓</span>
        </button>
      </div>
    `;

    // Locate target input inside slot
    setTimeout(() => {
      this.targetInput = this.querySelector(
        "textarea, input[type='text'], [contenteditable='true']",
      );
      if (this.targetInput) {
        this.targetInput.addEventListener("input", () => this.onInput());
        this.onInput();
      }
    }, 50);

    const widgetBtn = this.shadowRoot.getElementById("widgetBtn");
    const quickPopup = this.shadowRoot.getElementById("quickPopup");
    const closePopup = this.shadowRoot.getElementById("closePopup");
    const fixBtn = this.shadowRoot.getElementById("fixBtn");

    widgetBtn.addEventListener("click", () => {
      if (this.suggestions.length > 0) {
        quickPopup.style.display =
          quickPopup.style.display === "block" ? "none" : "block";
        this.populateQuickPopup();
      }
    });

    closePopup.addEventListener("click", () => {
      quickPopup.style.display = "none";
    });

    fixBtn.addEventListener("click", () => {
      this.applyFirstFix();
      quickPopup.style.display = "none";
    });
  }

  onInput() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.checkText();
    }, 400);
  }

  async checkText() {
    if (!this.targetInput) return;
    const text = this.targetInput.value || this.targetInput.innerText || "";
    if (!text.trim()) {
      this.updateBadge(0);
      return;
    }

    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      this.suggestions = data.suggestions || [];
      this.updateBadge(this.suggestions.length);
    } catch (err) {
      console.warn("Plugin check error:", err);
    }
  }

  updateBadge(count) {
    const badge = this.shadowRoot.getElementById("badgeEl");
    if (!badge) return;
    if (count === 0) {
      badge.className = "g-badge clean";
      badge.innerText = "✓";
    } else {
      badge.className = "g-badge";
      badge.innerText = count;
    }
  }

  populateQuickPopup() {
    if (this.suggestions.length === 0) return;
    const first = this.suggestions[0];
    const categoryEl = this.shadowRoot.getElementById("popupCategory");
    const msgEl = this.shadowRoot.getElementById("popupMsg");
    const fixText = this.shadowRoot.getElementById("fixText");

    categoryEl.innerText = (first.category || "Grammar").toUpperCase();
    msgEl.innerText = first.message;
    fixText.innerText = `${first.original} → ${first.replacement}`;
  }

  applyFirstFix() {
    if (this.suggestions.length === 0 || !this.targetInput) return;
    const first = this.suggestions[0];
    const text = this.targetInput.value || "";
    const newText =
      text.slice(0, first.start) + first.replacement + text.slice(first.end);
    this.targetInput.value = newText;
    this.onInput();
  }
}

customElements.define("grammarly-editor-plugin", GrammarlyEditorPlugin);
