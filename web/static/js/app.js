// Grammarly: AI Writing and Grammar Checker App (Superhuman Go Architecture)

class GrammarlyApp {
  constructor() {
    this.textarea = document.getElementById("editorTextarea");
    this.highlightsLayer = document.getElementById("editorHighlights");
    this.viewport = document.getElementById("editorViewport");
    this.popup = document.getElementById("suggestionPopup");
    this.floatingBubble = document.getElementById("floatingGBubble");
    this.bubbleBadge = document.getElementById("bubbleBadge");

    // Status elements
    this.statusDot = document.getElementById("statusDot");
    this.statusText = document.getElementById("statusText");

    // Side drawer elements
    this.overallScore = document.getElementById("overallScore");
    this.scoreGaugeCircle = document.getElementById("scoreGaugeCircle");
    this.scoreStatus = document.getElementById("scoreStatus");

    // Superhuman Go Elements
    this.chipSummarize = document.getElementById("chipSummarize");
    this.chipShortenJargon = document.getElementById("chipShortenJargon");
    this.chipReviewSuggestions = document.getElementById(
      "chipReviewSuggestions",
    );
    this.labelReviewSuggestions = document.getElementById(
      "labelReviewSuggestions",
    );
    this.btnFixConsistencyCallout = document.getElementById(
      "btnFixConsistencyCallout",
    );
    this.paragraphCallout = document.getElementById("paragraphCallout");

    this.agentResponseCard = document.getElementById("agentResponseCard");
    this.agentResponseContent = document.getElementById("agentResponseContent");
    this.btnApplyAgentResponse = document.getElementById(
      "btnApplyAgentResponse",
    );
    this.btnCloseAgentResponse = document.getElementById(
      "btnCloseAgentResponse",
    );

    this.inputAgentChat = document.getElementById("inputAgentChat");
    this.btnSendAgentChat = document.getElementById("btnSendAgentChat");

    this.issuesList = document.getElementById("issuesList");
    this.issuesCountBadge = document.getElementById("issuesCountBadge");

    // State
    this.suggestions = [];
    this.activeSuggestion = null;
    this.debounceTimer = null;
    this.checkDelay = 350;
    this.isChecking = false;
    this.currentText = "";
    this.lastAgentReplacement = null;

    this.initEventListeners();
    this.initTheme();
    this.initParaphraser();
    this.loadSampleText();
  }

  initEventListeners() {
    // Text typing & input
    this.textarea.addEventListener("input", () => {
      this.handleInput();
    });

    // Synchronize scrolling between textarea and highlights
    this.textarea.addEventListener("scroll", () => {
      this.highlightsLayer.scrollTop = this.textarea.scrollTop;
      this.highlightsLayer.scrollLeft = this.textarea.scrollLeft;
      this.hidePopup();
    });

    // Click outside popup to dismiss
    document.addEventListener("click", (e) => {
      if (
        !this.popup.contains(e.target) &&
        !e.target.classList.contains("highlight-span")
      ) {
        this.hidePopup();
      }
    });

    // Floating Bubble click -> jump to next error
    this.floatingBubble.addEventListener("click", () => {
      this.jumpToNextIssue();
    });

    // Superhuman Go Action Chips
    this.chipSummarize?.addEventListener("click", () =>
      this.callAgent("summarize"),
    );
    this.chipShortenJargon?.addEventListener("click", () =>
      this.callAgent("shorten_jargon"),
    );
    this.chipReviewSuggestions?.addEventListener("click", () =>
      this.jumpToNextIssue(),
    );

    // Floating Callout ("Fix grammar and consistency")
    this.btnFixConsistencyCallout?.addEventListener("click", () =>
      this.applyAllSuggestions(),
    );

    // Click on textarea checks if cursor is inside any suggestion span to anchor popup
    this.textarea.addEventListener("click", () => {
      const pos = this.textarea.selectionStart;
      const matchIdx = this.suggestions.findIndex(
        (s) => pos >= s.start && pos <= s.end,
      );
      if (matchIdx !== -1) {
        const span = this.highlightsLayer.querySelector(
          `.highlight-span[data-idx="${matchIdx}"]`,
        );
        if (span) {
          this.showPopupForSuggestion(matchIdx, span);
          return;
        }
      }
      this.hidePopup();
    });

    // Apply All Issues Button
    document
      .getElementById("btnApplyAllIssues")
      ?.addEventListener("click", () => this.applyAllSuggestions());

    // Agent response card actions
    this.btnCloseAgentResponse?.addEventListener("click", () => {
      this.agentResponseCard.style.display = "none";
    });

    this.btnApplyAgentResponse?.addEventListener("click", () => {
      if (this.lastAgentReplacement) {
        this.textarea.value = this.lastAgentReplacement;
        this.handleInput();
        this.agentResponseCard.style.display = "none";
      }
    });

    // Agent Chat Bar
    this.btnSendAgentChat?.addEventListener("click", () =>
      this.sendCustomChat(),
    );
    this.inputAgentChat?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.sendCustomChat();
    });

    // Header buttons
    document
      .getElementById("btnSampleText")
      ?.addEventListener("click", () => this.loadSampleText());
    document
      .getElementById("btnClear")
      ?.addEventListener("click", () => this.clearText());
    document
      .getElementById("btnCopy")
      ?.addEventListener("click", () => this.copyText());
    document
      .getElementById("btnThemeToggle")
      ?.addEventListener("click", () => this.toggleTheme());
    document
      .getElementById("btnSettings")
      ?.addEventListener("click", () => this.openSettings());
    document
      .getElementById("btnToggleAgents")
      ?.addEventListener("click", () => this.openAgentDirectory());

    // Agent Directory Modal
    document
      .getElementById("btnCloseAgentDir")
      ?.addEventListener("click", () => this.closeAgentDirectory());
    document
      .getElementById("btnCloseAgentDirX")
      ?.addEventListener("click", () => this.closeAgentDirectory());
    document
      .getElementById("btnNewChatFromDir")
      ?.addEventListener("click", () => {
        this.closeAgentDirectory();
        this.inputAgentChat.focus();
      });
    document
      .getElementById("inputSearchAgents")
      ?.addEventListener("input", (e) => {
        this.filterAgentCards(e.target.value);
      });

    // Pinned sidebar agent shortcuts
    document.querySelectorAll(".dir-menu-item[data-agent-id]").forEach((el) => {
      el.addEventListener("click", () => {
        const agentId = el.dataset.agentId;
        this.closeAgentDirectory();
        this.runSelectedAgent(agentId);
      });
    });

    // Popup actions
    document
      .getElementById("popupCloseBtn")
      ?.addEventListener("click", () => this.hidePopup());
    document
      .getElementById("popupAcceptBtn")
      ?.addEventListener("click", () => this.acceptActiveSuggestion());
    document
      .getElementById("popupIgnoreBtn")
      ?.addEventListener("click", () => this.ignoreActiveSuggestion());
    document
      .getElementById("popupDictBtn")
      ?.addEventListener("click", () => this.addActiveToDictionary());

    window.addEventListener("resize", () => {
      this.adjustEditorHeight();
    });
  }

  handleInput() {
    this.currentText = this.textarea.value;
    this.adjustEditorHeight();

    this.setStatus("checking", "Checking...");
    clearTimeout(this.debounceTimer);

    this.debounceTimer = setTimeout(() => {
      this.runGrammarCheck();
    }, this.checkDelay);
  }

  adjustEditorHeight() {
    this.textarea.style.height = "auto";
    const newHeight = Math.max(500, this.textarea.scrollHeight);
    this.textarea.style.height = `${newHeight}px`;
    this.highlightsLayer.style.height = `${newHeight}px`;
  }

  async runGrammarCheck() {
    const text = this.textarea.value;
    if (!text.trim()) {
      this.suggestions = [];
      this.renderHighlights();
      this.updateSidePanel({
        score: 100,
        error_count: 0,
        warning_count: 0,
        info_count: 0,
        total_suggestions: 0,
        tone: {
          tones: ["Neutral"],
          reading_ease: 100,
          readability_label: "Easy",
          word_count: 0,
          char_count: 0,
          reading_time_sec: 0,
        },
      });
      this.setStatus("ready", "All good!");
      if (this.paragraphCallout) this.paragraphCallout.style.display = "none";
      return;
    }

    try {
      this.isChecking = true;
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();

      this.suggestions = data.suggestions || [];
      this.renderHighlights();
      this.updateSidePanel(data);
      this.setStatus(
        "ready",
        this.suggestions.length === 0
          ? "All good!"
          : `${this.suggestions.length} suggestions`,
      );

      // Toggle floating callout based on suggestions presence
      if (this.paragraphCallout) {
        this.paragraphCallout.style.display =
          this.suggestions.length > 0 ? "flex" : "none";
      }
    } catch (err) {
      console.error("Check failed:", err);
      this.setStatus("error", "Check failed");
    } finally {
      this.isChecking = false;
    }
  }

  renderHighlights() {
    const text = this.textarea.value;
    if (!text || this.suggestions.length === 0) {
      this.highlightsLayer.innerHTML = this.escapeHtml(text);
      return;
    }

    let html = "";
    let lastIndex = 0;

    this.suggestions.forEach((s, idx) => {
      html += this.escapeHtml(text.slice(lastIndex, s.start));

      let cls = "highlight-error";
      if (s.category === "clarity") cls = "highlight-warning";
      if (s.category === "style") cls = "highlight-info";

      const highlightedText = text.slice(s.start, s.end);
      html += `<span class="highlight-span ${cls}" data-idx="${idx}">${this.escapeHtml(highlightedText)}</span>`;

      lastIndex = s.end;
    });

    html += this.escapeHtml(text.slice(lastIndex));
    this.highlightsLayer.innerHTML = html;

    this.highlightsLayer.querySelectorAll(".highlight-span").forEach((span) => {
      span.addEventListener("click", (e) => {
        const idx = parseInt(span.dataset.idx, 10);
        this.showPopupForSuggestion(idx, span);
      });
    });
  }

  showPopupForSuggestion(idx, spanElement) {
    const s = this.suggestions[idx];
    if (!s) return;
    this.activeSuggestion = s;

    const categoryEl = document.getElementById("popupCategory");
    const descEl = document.getElementById("popupDesc");
    const replacementBtn = document.getElementById("popupReplacementBtn");

    categoryEl.className = `popup-category category-${s.category || "grammar"}`;
    categoryEl.innerText = (s.category || "Grammar").toUpperCase();

    descEl.innerText = s.message || "Improve phrasing or grammar.";
    const repText = s.replacement ? s.replacement : "(remove)";
    replacementBtn.innerHTML = `<span>${this.escapeHtml(repText)}</span> <span>✓ Accept</span>`;

    const viewportRect = this.viewport.getBoundingClientRect();
    const spanRect = spanElement.getBoundingClientRect();

    let top = spanRect.bottom - viewportRect.top + this.viewport.scrollTop + 8;
    let left = spanRect.left - viewportRect.left + this.viewport.scrollLeft;

    if (left + 320 > this.viewport.clientWidth) {
      left = Math.max(16, this.viewport.clientWidth - 336);
    }

    this.popup.style.top = `${top}px`;
    this.popup.style.left = `${left}px`;
    this.popup.style.display = "block";
  }

  hidePopup() {
    this.popup.style.display = "none";
    this.activeSuggestion = null;
  }

  applySuggestion(s) {
    if (!s) return;
    let text = this.textarea.value;
    let start = s.start;
    let end = s.end;

    // Verify if text matches at declared range
    if (text.slice(start, end) !== s.original) {
      // Look in a neighborhood around start first (within 60 chars)
      const searchStart = Math.max(0, start - 60);
      const searchEnd = Math.min(text.length, end + 60);
      const localWindow = text.slice(searchStart, searchEnd);
      const localFound = localWindow.indexOf(s.original);
      if (localFound !== -1) {
        start = searchStart + localFound;
        end = start + s.original.length;
      } else {
        const foundIdx = text.indexOf(s.original);
        if (foundIdx !== -1) {
          start = foundIdx;
          end = start + s.original.length;
        }
      }
    }

    const replacement = s.replacement !== undefined ? s.replacement : "";
    const newText = text.slice(0, start) + replacement + text.slice(end);
    this.textarea.value = newText;

    // Calculate character length difference
    const delta = replacement.length - (end - start);

    // Immediately remove s from this.suggestions
    this.suggestions = this.suggestions.filter((item) => item !== s);

    // Shift offsets for any subsequent suggestions
    this.suggestions.forEach((item) => {
      if (item.start >= end) {
        item.start += delta;
        item.end += delta;
      }
    });

    this.hidePopup();

    // Instant local UI update
    const remainingCount = this.suggestions.length;
    this.renderHighlights();
    this.updateSidePanel({
      score:
        remainingCount === 0
          ? 100
          : Math.min(100, Math.max(50, 100 - remainingCount * 5)),
      total_suggestions: remainingCount,
      error_count: this.suggestions.filter((x) => x.severity === "error")
        .length,
      warning_count: this.suggestions.filter((x) => x.severity === "warning")
        .length,
      info_count: this.suggestions.filter((x) => x.severity === "info").length,
    });

    if (remainingCount === 0) {
      this.setStatus("ready", "All good!");
      if (this.paragraphCallout) this.paragraphCallout.style.display = "none";
    }

    // Trigger debounced re-verification with backend
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.runGrammarCheck();
    }, 400);
  }

  acceptActiveSuggestion() {
    if (!this.activeSuggestion) return;
    this.applySuggestion(this.activeSuggestion);
  }

  applyAllSuggestions() {
    if (!this.suggestions || this.suggestions.length === 0) return;
    let text = this.textarea.value;

    // Sort suggestions descending by start offset so indices don't shift!
    const sorted = [...this.suggestions].sort((a, b) => b.start - a.start);
    for (const s of sorted) {
      let start = s.start;
      let end = s.end;
      const rep = s.replacement !== undefined ? s.replacement : "";
      if (text.slice(start, end) === s.original) {
        text = text.slice(0, start) + rep + text.slice(end);
      } else {
        const found = text.indexOf(s.original);
        if (found !== -1) {
          text =
            text.slice(0, found) + rep + text.slice(found + s.original.length);
        }
      }
    }

    this.textarea.value = text;
    this.suggestions = [];
    this.hidePopup();

    // Instant visual update to 100% clean
    this.renderHighlights();
    this.updateSidePanel({
      score: 100,
      total_suggestions: 0,
      error_count: 0,
      warning_count: 0,
      info_count: 0,
    });
    this.setStatus("ready", "All good!");
    if (this.paragraphCallout) this.paragraphCallout.style.display = "none";

    // Trigger debounced re-verification with backend
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.runGrammarCheck();
    }, 400);
  }

  ignoreActiveSuggestion() {
    if (!this.activeSuggestion) return;
    const s = this.activeSuggestion;
    this.suggestions = this.suggestions.filter((item) => item !== s);
    this.hidePopup();
    this.renderHighlights();
  }

  async addActiveToDictionary() {
    if (!this.activeSuggestion) return;
    const word = this.activeSuggestion.original.trim();
    if (!word) return;

    try {
      await fetch("/api/dictionary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word }),
      });
      this.hidePopup();
      this.runGrammarCheck();
    } catch (err) {
      console.error("Failed to add to dictionary:", err);
    }
  }

  jumpToNextIssue() {
    if (this.suggestions.length === 0) return;
    const firstSpan = this.highlightsLayer.querySelector(".highlight-span");
    if (firstSpan) {
      firstSpan.scrollIntoView({ behavior: "smooth", block: "center" });
      const idx = parseInt(firstSpan.dataset.idx, 10);
      this.showPopupForSuggestion(idx, firstSpan);
    }
  }

  updateSidePanel(data) {
    const score = data.score ?? 100;
    this.overallScore.innerText = score;

    const offset = 163 - (163 * score) / 100;
    this.scoreGaugeCircle.style.strokeDashoffset = offset;

    if (score >= 90) {
      this.scoreStatus.innerText = "Excellent writing";
    } else if (score >= 75) {
      this.scoreStatus.innerText = "Looking good";
    } else {
      this.scoreStatus.innerText = "Needs revision";
    }

    const count = data.total_suggestions || 0;
    this.bubbleBadge.innerText = count;
    if (count === 0) {
      this.bubbleBadge.classList.add("zero");
      this.bubbleBadge.innerText = "✓";
    } else {
      this.bubbleBadge.classList.remove("zero");
    }

    // Update Superhuman Go action chip count
    if (this.labelReviewSuggestions) {
      this.labelReviewSuggestions.innerText = `Review ${count} suggestions`;
    }
    if (this.issuesCountBadge) {
      this.issuesCountBadge.innerText = `${count} issues`;
    }

    // Issues list accordion
    if (this.suggestions.length === 0) {
      this.issuesList.innerHTML = `<div style="color:var(--text-muted);font-size:0.85rem;text-align:center;padding:12px;">No issues detected. Your document looks polished! 🌟</div>`;
    } else {
      this.issuesList.innerHTML = this.suggestions
        .map(
          (s, idx) => `
        <div class="issue-item ${s.category}" data-idx="${idx}" title="Click to apply this fix">
          <div class="issue-header">
            <span class="issue-category-tag">${(s.category || "grammar").toUpperCase()}</span>
            <button class="btn-issue-dismiss" data-action="dismiss" data-idx="${idx}">Dismiss</button>
          </div>
          <div class="issue-title">
            <span class="issue-orig-tag">${this.escapeHtml(s.original)}</span>
            <span>→</span>
            <strong style="color:var(--primary);">${this.escapeHtml(s.replacement || "(remove)")}</strong>
          </div>
          <div class="issue-sub">${this.escapeHtml(s.message)}</div>
          <div class="issue-actions-row">
            <button class="btn-issue-apply" data-action="apply" data-idx="${idx}">
              ✓ Accept ${this.escapeHtml(s.replacement || "Fix")}
            </button>
          </div>
        </div>
      `,
        )
        .join("");

      this.issuesList.querySelectorAll(".issue-item").forEach((el) => {
        el.addEventListener("click", (e) => {
          const idx = parseInt(el.dataset.idx, 10);
          const s = this.suggestions[idx];
          if (!s) return;

          // If user clicked Dismiss
          if (e.target.dataset.action === "dismiss") {
            e.stopPropagation();
            this.suggestions = this.suggestions.filter((item) => item !== s);
            this.renderHighlights();
            this.updateSidePanel({
              score: this.overallScore.innerText,
              total_suggestions: this.suggestions.length,
              error_count: this.suggestions.filter(
                (x) => x.severity === "error",
              ).length,
              warning_count: this.suggestions.filter(
                (x) => x.severity === "warning",
              ).length,
              info_count: this.suggestions.filter((x) => x.severity === "info")
                .length,
            });
            return;
          }

          // In ANY OTHER case (whether clicking the '✓ Accept' button or clicking the card itself):
          // Immediately apply the suggestion!
          e.stopPropagation();
          this.applySuggestion(s);
        });
      });
    }
  }

  async callAgent(action) {
    const text = this.textarea.value.trim();
    if (!text) return;

    this.agentResponseCard.style.display = "block";
    this.agentResponseContent.innerText = "Superhuman Go is thinking...";
    this.btnApplyAgentResponse.style.display = "none";

    try {
      const res = await fetch("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, action }),
      });
      const data = await res.json();

      this.agentResponseContent.innerText = data.response;

      if (data.type === "replace") {
        this.lastAgentReplacement = data.response;
        this.btnApplyAgentResponse.style.display = "block";
        this.btnApplyAgentResponse.innerText = "Apply to Document";
      } else {
        this.btnApplyAgentResponse.style.display = "none";
      }
    } catch (err) {
      console.error("Agent call error:", err);
      this.agentResponseContent.innerText =
        "Superhuman Go request failed. Please check backend.";
    }
  }

  async sendCustomChat() {
    const query = this.inputAgentChat.value.trim();
    if (!query) return;

    const text = this.textarea.value.trim();
    this.inputAgentChat.value = "";

    this.agentResponseCard.style.display = "block";
    this.agentResponseContent.innerText = `Thinking about "${query}"...`;
    this.btnApplyAgentResponse.style.display = "none";

    try {
      const res = await fetch("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, action: "chat", query }),
      });
      const data = await res.json();
      this.agentResponseContent.innerText = data.response;
      if (data.type === "replace") {
        this.lastAgentReplacement = data.response;
        this.btnApplyAgentResponse.style.display = "block";
      }
    } catch (err) {
      console.error("Agent chat error:", err);
      this.agentResponseContent.innerText = "Could not reach Superhuman Go.";
    }
  }

  setStatus(type, text) {
    this.statusDot.className = `status-dot ${type}`;
    this.statusText.innerText = text;
  }

  loadSampleText() {
    // Exact Superhuman Go Zephyr Campaign demo text from screenshot
    this.textarea.value = `A meeting was held by our team on Monday with the client team for the Zephyr project to review the status of the forthcoming Q3 launch campaign. The campaign, originally built as an omnichannel activation across CTV, paid social and programmatic display, is now subject to substantial midstream revisions, as has been detailed in a previous update.

We conduct a daily standup each morning through end of week to identify blockers. The next client check-in is scheduled for July 3rd, where we preview asset revisions and confirm compliance milestones. Final go/no-go is slated for July 7th at 17:00 PDT. We are proceeding with all mitigations in parallel, and escalated any dependency delays as they surface.`;
    this.handleInput();
  }

  clearText() {
    this.textarea.value = "";
    this.handleInput();
  }

  copyText() {
    navigator.clipboard.writeText(this.textarea.value);
    const btn = document.getElementById("btnCopy");
    if (btn) {
      const orig = btn.innerText;
      btn.innerText = "Copied! ✓";
      setTimeout(() => {
        btn.innerText = orig;
      }, 1500);
    }
  }

  toggleTheme() {
    const isDark = document.body.getAttribute("data-theme") === "dark";
    if (isDark) {
      document.body.removeAttribute("data-theme");
      localStorage.setItem("theme", "light");
    } else {
      document.body.setAttribute("data-theme", "dark");
      localStorage.setItem("theme", "dark");
    }
  }

  initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
      document.body.setAttribute("data-theme", "dark");
    }
  }

  async openSettings() {
    const modal = document.getElementById("settingsModal");
    modal.classList.add("active");

    try {
      const res = await fetch("/api/config");
      const cfg = await res.json();
      document.getElementById("cfgAiProvider").value =
        cfg.ai_provider || "offline";
      document.getElementById("cfgOllamaUrl").value =
        cfg.ollama_url || "http://localhost:11434";
      document.getElementById("cfgOllamaModel").value =
        cfg.ollama_model || "llama3.2:latest";
      document.getElementById("cfgOpenAiKey").value = cfg.openai_api_key || "";
      document.getElementById("cfgOpenAiModel").value =
        cfg.openai_model || "gpt-4o-mini";

      this.renderDictionaryTags(cfg.personal_dictionary || []);
    } catch (err) {
      console.error("Error loading config:", err);
    }

    document.getElementById("modalCloseBtn").onclick = () =>
      modal.classList.remove("active");
    document.getElementById("btnCancelSettings").onclick = () =>
      modal.classList.remove("active");

    document.getElementById("btnSaveSettings").onclick = async () => {
      const updates = {
        ai_provider: document.getElementById("cfgAiProvider").value,
        ollama_url: document.getElementById("cfgOllamaUrl").value,
        ollama_model: document.getElementById("cfgOllamaModel").value,
        openai_api_key: document.getElementById("cfgOpenAiKey").value,
        openai_model: document.getElementById("cfgOpenAiModel").value,
      };
      await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });
      modal.classList.remove("active");
      this.runGrammarCheck();
    };

    document.getElementById("btnAddDictWord").onclick = async () => {
      const input = document.getElementById("inputDictWord");
      const word = input.value.trim();
      if (word) {
        const res = await fetch("/api/dictionary", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ word }),
        });
        const data = await res.json();
        input.value = "";
        this.renderDictionaryTags(data.dictionary || []);
      }
    };
  }

  renderDictionaryTags(dict) {
    const container = document.getElementById("dictionaryTags");
    if (!container) return;
    container.innerHTML = dict
      .map(
        (w) => `
      <span class="dict-tag">
        ${this.escapeHtml(w)}
        <span class="dict-tag-remove" data-word="${this.escapeHtml(w)}">×</span>
      </span>
    `,
      )
      .join("");

    container.querySelectorAll(".dict-tag-remove").forEach((el) => {
      el.addEventListener("click", async () => {
        const word = el.dataset.word;
        const res = await fetch(`/api/dictionary/${encodeURIComponent(word)}`, {
          method: "DELETE",
        });
        const data = await res.json();
        this.renderDictionaryTags(data.dictionary || []);
      });
    });
  }

  async openAgentDirectory() {
    const modal = document.getElementById("agentDirModal");
    modal.classList.add("active");

    if (!this.cachedAgents) {
      try {
        const res = await fetch("/api/agents");
        const data = await res.json();
        this.cachedAgents = data.agents || [];
      } catch (err) {
        console.error("Failed to load agents:", err);
        this.cachedAgents = [];
      }
    }

    this.renderAgentCards(this.cachedAgents);
  }

  closeAgentDirectory() {
    document.getElementById("agentDirModal")?.classList.remove("active");
  }

  renderAgentCards(agents) {
    const grid = document.getElementById("agentCardsGrid");
    if (!grid) return;

    grid.innerHTML = agents
      .map(
        (a) => `
      <div class="agent-card-item">
        <div class="agent-card-icon">${a.icon}</div>
        <div class="agent-card-info">
          <div class="agent-card-title-row">
            <span class="agent-card-title">${this.escapeHtml(a.name)}</span>
            ${a.badge ? `<span class="badge-template">${this.escapeHtml(a.badge)}</span>` : ""}
          </div>
          <div class="agent-card-desc">${this.escapeHtml(a.description)}</div>
        </div>
        <button class="btn-open-agent" data-agent-id="${a.id}">Open</button>
      </div>
    `,
      )
      .join("");

    grid.querySelectorAll(".btn-open-agent").forEach((btn) => {
      btn.addEventListener("click", () => {
        const agentId = btn.dataset.agentId;
        this.closeAgentDirectory();
        this.runSelectedAgent(agentId);
      });
    });
  }

  filterAgentCards(query) {
    if (!this.cachedAgents) return;
    const q = (query || "").toLowerCase();
    const filtered = this.cachedAgents.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        a.description.toLowerCase().includes(q) ||
        a.category.toLowerCase().includes(q),
    );
    this.renderAgentCards(filtered);
  }

  async runSelectedAgent(agentId) {
    const text = this.textarea.value.trim();
    if (!text) return;

    this.agentResponseCard.style.display = "block";
    const agentObj = (this.cachedAgents || []).find((a) => a.id === agentId);
    const agentName = agentObj ? agentObj.name : "Superhuman Go Agent";

    document.getElementById("agentResponseTitle").innerText =
      `${agentObj ? agentObj.icon : "⚡"} ${agentName}`;
    this.agentResponseContent.innerText = `Running ${agentName}...`;
    this.btnApplyAgentResponse.style.display = "none";

    try {
      const res = await fetch("/api/agents/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId, text }),
      });
      const data = await res.json();

      this.agentResponseContent.innerText = data.response;

      if (data.type === "replace") {
        this.lastAgentReplacement = data.response;
        this.btnApplyAgentResponse.style.display = "block";
        this.btnApplyAgentResponse.innerText = "Apply to Document";
      } else {
        this.btnApplyAgentResponse.style.display = "none";
      }
    } catch (err) {
      console.error("Run agent failed:", err);
      this.agentResponseContent.innerText = `Failed to run ${agentName}.`;
    }
  }


  initParaphraser() {
    this.paraModal = document.getElementById("paraphraserModal");
    this.btnOpenParaphraser = document.getElementById("btnOpenParaphraser");
    this.btnCloseParaphraser = document.getElementById("btnCloseParaphraser");
    this.paraInputText = document.getElementById("paraInputText");
    this.paraOutputContainer = document.getElementById("paraOutputContainer");
    this.paraSynonymSlider = document.getElementById("paraSynonymSlider");
    this.paraSliderVal = document.getElementById("paraSliderVal");
    this.btnDoParaphrase = document.getElementById("btnDoParaphrase");
    this.btnParaRephrase = document.getElementById("btnParaRephrase");
    this.btnParaPaste = document.getElementById("btnParaPaste");
    this.btnParaClear = document.getElementById("btnParaClear");
    this.btnParaCopy = document.getElementById("btnParaCopy");
    this.btnParaSendToEditor = document.getElementById("btnParaSendToEditor");
    this.inputFreezeWord = document.getElementById("inputFreezeWord");
    this.paraFreezeTags = document.getElementById("paraFreezeTags");
    this.paraSynonymPopover = document.getElementById("paraSynonymPopover");
    this.paraSynList = document.getElementById("paraSynList");
    this.paraChangesBadge = document.getElementById("paraChangesBadge");
    this.paraInputStats = document.getElementById("paraInputStats");
    this.paraOutputStats = document.getElementById("paraOutputStats");

    this.paraMode = "standard";
    this.paraEngine = "quillbot";
    this.paraTone = "Formal";
    this.paraVariantsCount = 3;
    this.allVariants = [];
    this.activeVariantIdx = 0;
    this.paraSynonymLevel = 2;
    this.paraFreezeWords = [];
    this.currentParaTokens = [];
    this.activeTokenIndex = null;

    this.paraEngineSwitcher = document.getElementById("paraEngineSwitcher");
    this.paraModesBar = document.getElementById("paraModesBar");
    this.paraAhrefsTonesBar = document.getElementById("paraAhrefsTonesBar");
    this.paraSliderGroup = document.getElementById("paraSliderGroup");
    this.paraVariantsGroup = document.getElementById("paraVariantsGroup");
    this.selectParaVariants = document.getElementById("selectParaVariants");
    this.paraVariantsBar = document.getElementById("paraVariantsBar");

    if (!this.paraModal) return;

    // Open Paraphraser Modal
    this.btnOpenParaphraser?.addEventListener("click", () => {
      this.paraModal.classList.add("active");
      if (!this.paraInputText.value.trim() && this.textarea.value.trim()) {
        this.paraInputText.value = this.textarea.value.trim();
        this.updateParaInputStats();
      }
    });

    // Close Modal
    this.btnCloseParaphraser?.addEventListener("click", () => {
      this.paraModal.classList.remove("active");
      this.hideParaPopover();
    });

    // Outside click dismisses popover
    document.addEventListener("click", (e) => {
      if (this.paraSynonymPopover && !this.paraSynonymPopover.contains(e.target) && !e.target.classList.contains("token-replaced")) {
        this.hideParaPopover();
      }
    });

    // Input stats update
    this.paraInputText?.addEventListener("input", () => {
      this.updateParaInputStats();
    });

    // Engine Switcher: QuillBot vs Ahrefs
    document.querySelectorAll(".para-engine-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".para-engine-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        this.paraEngine = tab.dataset.engine;

        if (this.paraEngine === "ahrefs") {
          if (this.paraModesBar) this.paraModesBar.style.display = "none";
          if (this.paraSliderGroup) this.paraSliderGroup.style.display = "none";
          if (this.paraAhrefsTonesBar) this.paraAhrefsTonesBar.style.display = "flex";
          if (this.paraVariantsGroup) this.paraVariantsGroup.style.display = "flex";
          if (this.btnDoParaphrase) this.btnDoParaphrase.style.background = "#ff4d00";
        } else {
          if (this.paraModesBar) this.paraModesBar.style.display = "flex";
          if (this.paraSliderGroup) this.paraSliderGroup.style.display = "flex";
          if (this.paraAhrefsTonesBar) this.paraAhrefsTonesBar.style.display = "none";
          if (this.paraVariantsGroup) this.paraVariantsGroup.style.display = "none";
          if (this.btnDoParaphrase) this.btnDoParaphrase.style.background = "#15C39A";
        }

        if (this.paraInputText && this.paraInputText.value.trim()) {
          this.executeParaphrase();
        }
      });
    });

    // QuillBot Modes Bar selection
    document.querySelectorAll("#paraModesBar .para-mode-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        document.querySelectorAll("#paraModesBar .para-mode-chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        this.paraMode = chip.dataset.mode;
        if (this.paraInputText.value.trim()) {
          this.executeParaphrase();
        }
      });
    });

    // Ahrefs Tones Bar selection
    document.querySelectorAll("#paraAhrefsTonesBar .para-mode-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        document.querySelectorAll("#paraAhrefsTonesBar .para-mode-chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        this.paraTone = chip.dataset.tone;
        if (this.paraInputText.value.trim()) {
          this.executeParaphrase();
        }
      });
    });

    // Ahrefs Variants Count selection
    this.selectParaVariants?.addEventListener("change", (e) => {
      this.paraVariantsCount = parseInt(e.target.value, 10);
      if (this.paraInputText && this.paraInputText.value.trim()) {
        this.executeParaphrase();
      }
    });

    // Synonyms Slider
    const sliderLabels = { 1: "Fewest", 2: "Balanced", 3: "Dynamic", 4: "Maximum" };
    this.paraSynonymSlider?.addEventListener("input", (e) => {
      this.paraSynonymLevel = parseInt(e.target.value, 10);
      if (this.paraSliderVal) {
        this.paraSliderVal.innerText = sliderLabels[this.paraSynonymLevel] || "Balanced";
      }
    });

    // Freeze Words input
    this.inputFreezeWord?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const word = this.inputFreezeWord.value.trim();
        if (word && !this.paraFreezeWords.includes(word)) {
          this.paraFreezeWords.push(word);
          this.renderFreezeTags();
          this.inputFreezeWord.value = "";
        }
      }
    });

    // Paraphrase Execution Actions
    this.btnDoParaphrase?.addEventListener("click", () => this.executeParaphrase());
    this.btnParaRephrase?.addEventListener("click", () => this.executeParaphrase());

    // Paste
    this.btnParaPaste?.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        this.paraInputText.value = text;
        this.updateParaInputStats();
      } catch (err) {
        console.error("Paste failed:", err);
      }
    });

    // Clear
    this.btnParaClear?.addEventListener("click", () => {
      this.paraInputText.value = "";
      this.updateParaInputStats();
      this.paraOutputContainer.innerHTML = '<div class="para-placeholder">Click \'Paraphrase\' to generate restructured text with alternative synonym chips.</div>';
      if (this.paraChangesBadge) this.paraChangesBadge.innerText = "0 changes";
      if (this.paraOutputStats) this.paraOutputStats.innerText = "0 words";
      this.currentParaTokens = [];
    });

    // Copy Output
    this.btnParaCopy?.addEventListener("click", () => {
      const fullText = this.getParaphrasedPlaintext();
      if (fullText) {
        navigator.clipboard.writeText(fullText);
        const orig = this.btnParaCopy.innerText;
        this.btnParaCopy.innerText = "Copied! ✓";
        setTimeout(() => { this.btnParaCopy.innerText = orig; }, 1500);
      }
    });

    // Send to Document
    this.btnParaSendToEditor?.addEventListener("click", () => {
      const fullText = this.getParaphrasedPlaintext();
      if (fullText) {
        this.textarea.value = fullText;
        this.handleInput();
        this.paraModal.classList.remove("active");
      }
    });
  }

  updateParaInputStats() {
    const text = this.paraInputText.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    if (this.paraInputStats) {
      this.paraInputStats.innerText = `${words} words • ${chars} characters`;
    }
  }

  renderFreezeTags() {
    if (!this.paraFreezeTags) return;
    this.paraFreezeTags.innerHTML = this.paraFreezeWords.map((w, idx) => `
      <span class="para-freeze-tag">
        <span>${this.escapeHtml(w)}</span>
        <span class="para-freeze-tag-remove" data-idx="${idx}">×</span>
      </span>
    `).join("");

    this.paraFreezeTags.querySelectorAll(".para-freeze-tag-remove").forEach((el) => {
      el.addEventListener("click", () => {
        const idx = parseInt(el.dataset.idx, 10);
        this.paraFreezeWords.splice(idx, 1);
        this.renderFreezeTags();
      });
    });
  }

  async executeParaphrase() {
    const text = this.paraInputText.value.trim();
    if (!text) return;

    const isAhrefs = this.paraEngine === "ahrefs";
    const engineLabel = isAhrefs ? `Ahrefs AI (${this.paraTone})` : `QuillBot ${this.paraMode}`;

    this.btnDoParaphrase.disabled = true;
    this.btnDoParaphrase.innerHTML = `<span>⏳ Paraphrasing...</span>`;
    this.paraOutputContainer.innerHTML = `<div style="color:var(--text-muted);font-style:italic;padding:12px;">Rewriting text with ${engineLabel}...</div>`;

    try {
      const endpoint = isAhrefs ? "/api/ahrefs/paraphrase" : "/api/paraphrase";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          mode: this.paraMode,
          provider: this.paraEngine,
          tone: this.paraTone,
          variants_count: this.paraVariantsCount,
          synonym_level: this.paraSynonymLevel,
          freeze_words: this.paraFreezeWords
        })
      });
      const data = await res.json();
      this.allVariants = data.variants || [data.paraphrased_text || ""];
      this.activeVariantIdx = 0;
      this.currentParaTokens = data.tokens || [];

      // Render Multi-Variant selector if multiple variants returned
      this.renderVariantPills(this.allVariants);

      this.renderParaphraseTokens(this.currentParaTokens);
      if (this.paraChangesBadge) {
        const sourceTag = data.source === "ahrefs_live_v4" ? " · Ahrefs Live v4" : (isAhrefs ? " · Ahrefs Engine" : "");
        this.paraChangesBadge.innerText = `${data.changes_count || 0} changes${sourceTag}`;
      }
      if (this.paraOutputStats) {
        const wordCount = (data.paraphrased_text || "").trim().split(/\s+/).filter(Boolean).length;
        this.paraOutputStats.innerText = `${wordCount} words`;
      }
    } catch (err) {
      console.error("Paraphrase failed:", err);
      this.paraOutputContainer.innerHTML = `<div style="color:var(--error);padding:12px;">Paraphrase failed. Check server status.</div>`;
    } finally {
      this.btnDoParaphrase.disabled = false;
      this.btnDoParaphrase.innerHTML = `<span>⚡ Paraphrase</span>`;
    }
  }

  renderVariantPills(variants) {
    if (!this.paraVariantsBar) return;
    if (!variants || variants.length <= 1) {
      this.paraVariantsBar.style.display = "none";
      this.paraVariantsBar.innerHTML = "";
      return;
    }

    this.paraVariantsBar.style.display = "flex";
    this.paraVariantsBar.innerHTML = `
      <span style="font-size:0.75rem;color:var(--text-muted);font-weight:700;margin-right:6px;">Variants:</span>
      ${variants.map((v, i) => `
        <button class="para-variant-pill ${i === this.activeVariantIdx ? "active" : ""}" data-idx="${i}">
          Variant ${i + 1}
        </button>
      `).join("")}
    `;

    this.paraVariantsBar.querySelectorAll(".para-variant-pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.dataset.idx, 10);
        this.selectVariant(idx);
      });
    });
  }

  selectVariant(idx) {
    if (!this.allVariants[idx]) return;
    this.activeVariantIdx = idx;
    this.paraVariantsBar.querySelectorAll(".para-variant-pill").forEach((btn, i) => {
      btn.classList.toggle("active", i === idx);
    });

    const chosenText = this.allVariants[idx];
    const tokens = chosenText.split(/(\s+)/).filter(Boolean).map((t) => ({
      text: t,
      original: t,
      type: t.trim() ? "replaced" : "unchanged",
      alternatives: []
    }));
    this.currentParaTokens = tokens;
    this.renderParaphraseTokens(tokens);

    if (this.paraOutputStats) {
      const words = chosenText.trim().split(/\s+/).filter(Boolean).length;
      this.paraOutputStats.innerText = `${words} words`;
    }
  }

  renderParaphraseTokens(tokens) {
    if (!tokens || tokens.length === 0) {
      this.paraOutputContainer.innerHTML = "";
      return;
    }

    let html = "";
    tokens.forEach((tok, idx) => {
      let cls = "para-token";
      if (tok.type === "replaced") {
        cls += " token-replaced";
      } else if (tok.type === "added") {
        cls += " token-added";
      }
      
      const needsSpace = idx > 0 && !/^[,.!?;:'")\]}]/.test(tok.text) && !html.endsWith("(") && !html.endsWith('"') && !html.endsWith("'");
      if (needsSpace) html += " ";

      if (tok.type === "replaced" && tok.alternatives && tok.alternatives.length > 0) {
        html += `<span class="${cls}" data-tok-idx="${idx}" title="Click to view alternative synonyms">${this.escapeHtml(tok.text)}</span>`;
      } else {
        html += `<span class="${cls}">${this.escapeHtml(tok.text)}</span>`;
      }
    });

    this.paraOutputContainer.innerHTML = html;

    // Attach click events on replaced tokens to show alternative synonyms dropdown
    this.paraOutputContainer.querySelectorAll(".token-replaced").forEach((el) => {
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        const tokIdx = parseInt(el.dataset.tokIdx, 10);
        this.showParaPopover(tokIdx, el);
      });
    });
  }

  showParaPopover(tokIdx, element) {
    const tok = this.currentParaTokens[tokIdx];
    if (!tok || !tok.alternatives || tok.alternatives.length === 0) return;
    this.activeTokenIndex = tokIdx;

    let itemsHtml = tok.alternatives.map((alt) => `
      <div class="para-syn-item" data-word="${this.escapeHtml(alt)}">
        <span>${this.escapeHtml(alt)}</span>
        <span style="font-size:0.75rem;color:var(--text-muted);">✓</span>
      </div>
    `).join("");

    this.paraSynList.innerHTML = itemsHtml;

    const modalRect = this.paraModal.getBoundingClientRect();
    const elRect = element.getBoundingClientRect();

    let top = (elRect.bottom - modalRect.top) + 6;
    let left = (elRect.left - modalRect.left);

    if (left + 230 > modalRect.width) {
      left = Math.max(16, modalRect.width - 240);
    }

    this.paraSynonymPopover.style.top = `${top}px`;
    this.paraSynonymPopover.style.left = `${left}px`;
    this.paraSynonymPopover.style.display = "block";

    this.paraSynList.querySelectorAll(".para-syn-item").forEach((item) => {
      item.addEventListener("click", () => {
        const newWord = item.dataset.word;
        this.selectAlternativeSynonym(tokIdx, newWord);
      });
    });
  }

  selectAlternativeSynonym(tokIdx, newWord) {
    if (this.currentParaTokens[tokIdx]) {
      this.currentParaTokens[tokIdx].text = newWord;
      this.renderParaphraseTokens(this.currentParaTokens);
      this.hideParaPopover();
    }
  }

  hideParaPopover() {
    if (this.paraSynonymPopover) {
      this.paraSynonymPopover.style.display = "none";
    }
    this.activeTokenIndex = null;
  }

  getParaphrasedPlaintext() {
    if (!this.currentParaTokens || this.currentParaTokens.length === 0) {
      return this.paraOutputContainer.innerText || "";
    }
    let res = "";
    this.currentParaTokens.forEach((tok, idx) => {
      const needsSpace = idx > 0 && !/^[,.!?;:'")\]}]/.test(tok.text) && !res.endsWith("(") && !res.endsWith('"');
      if (needsSpace) res += " ";
      res += tok.text;
    });
    return res;
  }

  escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.grammarly = new GrammarlyApp();
});
