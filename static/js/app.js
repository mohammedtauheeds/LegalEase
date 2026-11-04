/**
 * LegalEase - AI-Powered Indian Legal Awareness Chatbot
 * File: static/js/app.js
 *
 * Implements client-side state management, REST API integration with Flask backend,
 * conversation history loading, safe XSS-sanitized markdown formatting,
 * expandable legal citations/source badge rendering, and responsive interactions.
 */

(() => {
  "use strict";

  // ============================================================================
  // CONFIGURATION & STATE
  // ============================================================================
  const STORAGE_KEY_SESSION = "legalease_active_session";
  const MAX_CHAR_LIMIT = 1000;

  const state = {
    activeSessionId: null,
    isRequestInProgress: false,
    conversations: [],
    pendingDeleteSessionId: null,
    pendingRenameSessionId: null,
  };

  // ============================================================================
  // DOM ELEMENT REFERENCES
  // ============================================================================
  const DOM = {
    // Layout & Navigation
    sidebar: document.getElementById("sidebar"),
    sidebarBackdrop: document.getElementById("sidebarBackdrop"),
    mobileMenuBtn: document.getElementById("mobileMenuBtn"),
    mobileNewChatBtn: document.getElementById("mobileNewChatBtn"),
    btnNewChat: document.getElementById("btnNewChat"),
    btnRefreshHistory: document.getElementById("btnRefreshHistory"),
    conversationList: document.getElementById("conversationList"),
    statusDot: document.getElementById("statusDot"),
    statusText: document.getElementById("statusText"),

    // Chat Header & Body
    activeChatTitle: document.getElementById("activeChatTitle"),
    sessionBadge: document.getElementById("sessionBadge"),
    btnClearChat: document.getElementById("btnClearChat"),
    chatBody: document.getElementById("chatBody"),
    welcomeScreen: document.getElementById("welcomeScreen"),
    messagesContainer: document.getElementById("messagesContainer"),
    typingIndicator: document.getElementById("typingIndicator"),

    // Input Area
    userInput: document.getElementById("userInput"),
    btnSend: document.getElementById("btnSend"),
    charCounter: document.getElementById("charCounter"),

    // Modals
    renameModalEl: document.getElementById("renameModal"),
    renameTitleInput: document.getElementById("renameTitleInput"),
    renameSessionId: document.getElementById("renameSessionId"),
    btnConfirmRename: document.getElementById("btnConfirmRename"),

    deleteModalEl: document.getElementById("deleteConfirmModal"),
    deleteSessionId: document.getElementById("deleteSessionId"),
    btnConfirmDelete: document.getElementById("btnConfirmDelete"),

    // Toast
    appToastEl: document.getElementById("appToast"),
    toastMessage: document.getElementById("toastMessage"),
    toastIcon: document.getElementById("toastIcon"),
  };

  // Bootstrap Modal & Toast Instances
  let renameModalInstance = null;
  let deleteModalInstance = null;
  let toastInstance = null;

  // ============================================================================
  // INITIALIZATION
  // ============================================================================
  document.addEventListener("DOMContentLoaded", () => {
    initModalsAndToasts();
    bindEventListeners();
    checkSystemHealth();
    loadConversationList();
    restoreActiveSession();
  });

  function initModalsAndToasts() {
    if (window.bootstrap) {
      if (DOM.renameModalEl) renameModalInstance = new bootstrap.Modal(DOM.renameModalEl);
      if (DOM.deleteModalEl) deleteModalInstance = new bootstrap.Modal(DOM.deleteModalEl);
      if (DOM.appToastEl) toastInstance = new bootstrap.Toast(DOM.appToastEl, { delay: 3500 });
    }
  }

  // ============================================================================
  // API CLIENT METHODS
  // ============================================================================

  /**
   * Check backend health status (GET /api/health).
   */
  async function checkSystemHealth() {
    try {
      const resp = await fetch("/api/health", { method: "GET" });
      if (resp.ok) {
        const data = await resp.json();
        if (data.success) {
          DOM.statusDot.className = "status-dot online";
          DOM.statusText.textContent = `Online • ${data.service || "LegalEase"}`;
          return true;
        }
      }
      setSystemOffline();
    } catch (err) {
      console.warn("Backend health check failed:", err);
      setSystemOffline();
    }
    return false;
  }

  function setSystemOffline() {
    DOM.statusDot.className = "status-dot offline";
    DOM.statusText.textContent = "Service Offline";
  }

  /**
   * Fetch recent conversation list (GET /api/conversations).
   */
  async function loadConversationList() {
    try {
      const resp = await fetch("/api/conversations?limit=30&offset=0", { method: "GET" });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (data.success && Array.isArray(data.conversations)) {
        state.conversations = data.conversations;
        renderConversationList();
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
      DOM.conversationList.innerHTML = `
        <div class="conversation-empty-state">
          <i class="bi bi-exclamation-circle text-muted d-block mb-1"></i>
          <span>Could not load past chats.</span>
        </div>`;
    }
  }

  /**
   * Load a conversation session's message history (GET /api/chat/<session_id>).
   */
  async function loadConversationHistory(sessionId) {
    if (!sessionId) return;
    try {
      const resp = await fetch(`/api/chat/${encodeURIComponent(sessionId)}`, { method: "GET" });
      if (resp.status === 404) {
        // Session not found in DB; clear stored ID and reset to welcome screen
        clearActiveSession();
        return;
      }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const data = await resp.json();
      if (data.success) {
        state.activeSessionId = data.session_id;
        localStorage.setItem(STORAGE_KEY_SESSION, data.session_id);

        updateHeaderTitle(data.title || "Legal Consultation");
        highlightActiveConversation(data.session_id);

        if (Array.isArray(data.messages) && data.messages.length > 0) {
          showMessagesContainer();
          DOM.messagesContainer.innerHTML = "";
          data.messages.forEach(msg => {
            appendMessage(msg.role, msg.content, msg.sources, msg.metadata, msg.created_at);
          });
          scrollToBottom(true);
        } else {
          showWelcomeScreen();
        }
      }
    } catch (err) {
      console.error("Failed to retrieve chat history:", err);
      showToast("Unable to load chat history. Please try again.", "danger");
      clearActiveSession();
    }
  }

  /**
   * Send chat message to backend (POST /api/chat).
   */
  async function sendChatMessage(messageText) {
    const cleanText = messageText.trim();
    if (!cleanText || state.isRequestInProgress) return;

    if (cleanText.length > MAX_CHAR_LIMIT) {
      showToast(`Question exceeds maximum length of ${MAX_CHAR_LIMIT} characters.`, "warning");
      return;
    }

    const isFirstTurn = !state.activeSessionId;
    if (isFirstTurn) {
      updateHeaderTitle(cleanText.slice(0, 50));
    }

    // Set UI to loading state
    state.isRequestInProgress = true;
    DOM.btnSend.disabled = true;
    DOM.userInput.disabled = true;

    // Transition from welcome screen to message container
    showMessagesContainer();

    // Append user message bubble immediately
    appendMessage("user", cleanText);
    DOM.userInput.value = "";
    updateCharCounter();
    resetTextareaHeight();
    scrollToBottom(true);

    // Show typing indicator
    showTypingIndicator();

    try {
      const payload = {
        message: cleanText,
        session_id: state.activeSessionId || null,
      };

      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await resp.json();
      hideTypingIndicator();

      if (!resp.ok || !data.success) {
        const errorMsg = data.error || "An unexpected error occurred while processing your legal query.";
        appendMessage("assistant", `⚠️ **Notice:** ${errorMsg}\n\nPlease try rephrasing your legal question or verify your network connection.`);
        showToast(errorMsg, "danger");
      } else {
        // Update active session state
        state.activeSessionId = data.session_id;
        localStorage.setItem(STORAGE_KEY_SESSION, data.session_id);
        DOM.sessionBadge.textContent = "Active Session";

        // Append assistant response
        appendMessage("assistant", data.answer, data.sources, data.metadata);

        // Refresh conversation sidebar to reflect any new session or updated timestamp
        loadConversationList();
      }
    } catch (err) {
      console.error("Chat communication error:", err);
      hideTypingIndicator();
      appendMessage(
        "assistant",
        "⚠️ **Connection Error:** Could not reach the LegalEase server.\n\nPlease check your internet connection or verify the Flask backend is running on `http://127.0.0.1:5000`."
      );
      showToast("Failed to connect to LegalEase backend.", "danger");
    } finally {
      state.isRequestInProgress = false;
      DOM.userInput.disabled = false;
      DOM.btnSend.disabled = false;
      DOM.userInput.focus();
      scrollToBottom();
    }
  }

  /**
   * Rename conversation title (PATCH /api/chat/<session_id>).
   */
  async function renameConversation(sessionId, newTitle) {
    if (!sessionId || !newTitle.trim()) return;
    try {
      const resp = await fetch(`/api/chat/${encodeURIComponent(sessionId)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle.trim() }),
      });

      const data = await resp.json();
      if (resp.ok && data.success) {
        showToast("Conversation renamed successfully.", "success");
        if (state.activeSessionId === sessionId) {
          updateHeaderTitle(data.title);
        }
        loadConversationList();
      } else {
        showToast(data.error || "Failed to rename conversation.", "warning");
      }
    } catch (err) {
      console.error("Rename request failed:", err);
      showToast("Error renaming conversation.", "danger");
    }
  }

  /**
   * Delete conversation (DELETE /api/chat/<session_id>).
   */
  async function deleteConversation(sessionId) {
    if (!sessionId) return;
    try {
      const resp = await fetch(`/api/chat/${encodeURIComponent(sessionId)}`, {
        method: "DELETE",
      });

      const data = await resp.json();
      if (resp.ok && data.success) {
        showToast("Conversation deleted.", "success");
        if (state.activeSessionId === sessionId) {
          clearActiveSession();
        }
        loadConversationList();
      } else {
        showToast(data.error || "Failed to delete conversation.", "warning");
      }
    } catch (err) {
      console.error("Delete request failed:", err);
      showToast("Error deleting conversation.", "danger");
    }
  }

  // ============================================================================
  // UI RENDERING & COMPONENT BUILDERS
  // ============================================================================

  /**
   * Render the sidebar conversation list.
   */
  function renderConversationList() {
    DOM.conversationList.innerHTML = "";

    if (!state.conversations || state.conversations.length === 0) {
      DOM.conversationList.innerHTML = `
        <div class="conversation-empty-state">
          <i class="bi bi-chat-square-text text-muted d-block mb-2 fs-5"></i>
          <span>No conversation history yet. Start asking a question!</span>
        </div>`;
      return;
    }

    state.conversations.forEach(conv => {
      const item = document.createElement("div");
      item.className = `conversation-item ${conv.session_id === state.activeSessionId ? "active" : ""}`;
      item.dataset.sessionId = conv.session_id;

      item.innerHTML = `
        <div class="conversation-title-wrapper" title="${escapeHtml(conv.title)}">
          <i class="bi bi-chat-left-text"></i>
          <span class="conversation-title">${escapeHtml(conv.title || "Legal Consultation")}</span>
        </div>
        <div class="conversation-actions">
          <button class="btn-conv-action btn-conv-rename" title="Rename Title" aria-label="Rename conversation">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn-conv-action btn-conv-delete" title="Delete Chat" aria-label="Delete conversation">
            <i class="bi bi-trash"></i>
          </button>
        </div>`;

      // Click to select conversation
      item.addEventListener("click", e => {
        if (e.target.closest(".conversation-actions")) return;
        selectConversation(conv.session_id);
      });

      // Rename button
      const renameBtn = item.querySelector(".btn-conv-rename");
      renameBtn.addEventListener("click", e => {
        e.stopPropagation();
        openRenameModal(conv.session_id, conv.title);
      });

      // Delete button
      const deleteBtn = item.querySelector(".btn-conv-delete");
      deleteBtn.addEventListener("click", e => {
        e.stopPropagation();
        openDeleteModal(conv.session_id);
      });

      DOM.conversationList.appendChild(item);
    });
  }

  function highlightActiveConversation(sessionId) {
    document.querySelectorAll(".conversation-item").forEach(el => {
      if (el.dataset.sessionId === sessionId) {
        el.classList.add("active");
      } else {
        el.classList.remove("active");
      }
    });
  }

  function selectConversation(sessionId) {
    if (state.isRequestInProgress) {
      showToast("Please wait for the current legal query to finish processing.", "warning");
      return;
    }
    if (state.activeSessionId === sessionId) return;
    closeMobileSidebar();
    loadConversationHistory(sessionId);
  }

  /**
   * Append a single chat turn bubble to the messages feed.
   */
  function appendMessage(role, content, sources = [], metadata = {}, timestamp = null) {
    const isUser = role === "user";
    const timeString = timestamp ? formatTimestamp(timestamp) : formatCurrentTime();

    const row = document.createElement("div");
    row.className = `message-row ${isUser ? "user" : "assistant"}`;

    const avatarHtml = isUser
      ? `<div class="message-avatar" title="You"><i class="bi bi-person-fill"></i></div>`
      : `<div class="message-avatar" title="LegalEase Assistant"><i class="bi bi-shield-shaded"></i></div>`;

    const formattedBody = isUser ? escapeHtml(content).replace(/\n/g, "<br>") : safeMarkdownToHtml(content);

    // Build expandable sources HTML if assistant returned verified sources
    let sourcesHtml = "";
    if (!isUser && Array.isArray(sources) && sources.length > 0) {
      sourcesHtml = buildSourcesAccordionHtml(sources);
    }

    row.innerHTML = `
      ${avatarHtml}
      <div class="message-content-wrapper">
        <div class="message-bubble">
          ${formattedBody}
          ${sourcesHtml}
        </div>
        <span class="message-time">${timeString}</span>
      </div>`;

    // Bind source accordion toggle if present
    const toggleBtn = row.querySelector(".sources-toggle-btn");
    const sourcesContent = row.querySelector(".sources-content");
    if (toggleBtn && sourcesContent) {
      toggleBtn.addEventListener("click", () => {
        const isExpanded = toggleBtn.getAttribute("aria-expanded") === "true";
        toggleBtn.setAttribute("aria-expanded", !isExpanded);
        sourcesContent.classList.toggle("d-none");
      });
    }

    DOM.messagesContainer.appendChild(row);
  }

  /**
   * Build expandable source references HTML with verified cards and badges.
   */
  function buildSourcesAccordionHtml(sources) {
    if (!sources || sources.length === 0) return "";

    const count = sources.length;
    let cardsHtml = "";

    sources.forEach((src, idx) => {
      const title = escapeHtml(src.title || src.source_title || `Legal Citation #${idx + 1}`);
      const type = escapeHtml(src.type || src.source_type || "statute");
      const act = escapeHtml(src.act || src.act_name || "");
      const section = escapeHtml(src.section || "");
      const url = src.url || src.source_url || "";

      // Type Badge styling
      let badgeClass = "badge-statute";
      let typeLabel = "Statute";
      if (type.includes("judgment") || type.includes("case")) {
        badgeClass = "badge-judgment";
        typeLabel = "Court Judgment";
      } else if (type.includes("faq")) {
        badgeClass = "badge-faq";
        typeLabel = "Verified FAQ";
      } else if (type.includes("portal") || type.includes("official")) {
        badgeClass = "badge-portal";
        typeLabel = "Official Portal";
      }

      // Metadata string
      const metaParts = [];
      if (act) metaParts.push(act);
      if (section) metaParts.push(section.startsWith("Section") || section.startsWith("Sec") ? section : `Sec. ${section}`);
      const metaStr = metaParts.join(" • ");

      // Validate safe HTTP/HTTPS URL protocols strictly to prevent javascript: or data: injection
      const isSafeProtocol = url && (url.startsWith("https://") || url.startsWith("http://"));
      const linkHtml = isSafeProtocol
        ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="source-link-btn" title="Open verified official legal source">
             <span>Verify Source</span>
             <i class="bi bi-box-arrow-up-right"></i>
           </a>`
        : "";

      cardsHtml += `
        <div class="source-card">
          <div class="source-info">
            <div class="source-title-row">
              <span class="source-badge ${badgeClass}">${typeLabel}</span>
              <span class="source-title">${title}</span>
            </div>
            ${metaStr ? `<span class="source-meta">${metaStr}</span>` : ""}
          </div>
          ${linkHtml}
        </div>`;
    });

    return `
      <div class="message-sources-wrapper">
        <button class="sources-toggle-btn" aria-expanded="false" title="Toggle verified source references">
          <i class="bi bi-chevron-down"></i>
          <span>Verified Legal References (${count})</span>
        </button>
        <div class="sources-content d-none">
          ${cardsHtml}
        </div>
      </div>`;
  }

  // ============================================================================
  // SAFE MARKDOWN TO HTML PARSER (XSS-SANITIZED)
  // ============================================================================

  /**
   * Strictly escapes raw HTML characters first, then transforms
   * standard Markdown syntax and legal section tags into safe HTML.
   */
  function safeMarkdownToHtml(markdownText) {
    if (!markdownText || typeof markdownText !== "string") return "";

    // 1. Mandatory HTML escaping to eliminate XSS injection
    let text = escapeHtml(markdownText);

    // 2. Fenced code blocks ```code```
    const codeBlocks = [];
    text = text.replace(/```([\s\S]*?)```/g, (match, code) => {
      codeBlocks.push(`<pre><code>${code.trim()}</code></pre>`);
      return `__CODE_BLOCK_${codeBlocks.length - 1}__`;
    });

    // 3. Inline code `code`
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

    // 4. Headings (###, ##, #)
    text = text.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    text = text.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    text = text.replace(/^# (.*$)/gim, "<h1>$1</h1>");

    // 5. Bold & Italic
    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // 5b. Safe Markdown Links (Strictly HTTP/HTTPS)
    text = text.replace(
      /\[([^\]]+)\]\((https?:\/\/[^\s\)\"]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="chat-inline-link">$1</a>'
    );

    // 6. Blockquotes (> text)
    text = text.replace(/^> (.*$)/gim, "<blockquote>$1</blockquote>");

    // 7 & 8. Robust Line-by-Line List Processing (Unordered & Ordered)
    const lines = text.split("\n");
    const output = [];
    let inUl = false;
    let inOl = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Unordered list items starting with -, *, •, or Unicode bullet
      const ulMatch = trimmed.match(/^([-*•]|\u2022|&bull;)\s+(.*)$/);
      // Ordered list items starting with digits + dot (e.g. 1. Item)
      const olMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);

      if (ulMatch) {
        if (inOl) {
          output.push("</ol>");
          inOl = false;
        }
        if (!inUl) {
          output.push("<ul>");
          inUl = true;
        }
        output.push(`<li>${ulMatch[2]}</li>`);
      } else if (olMatch) {
        if (inUl) {
          output.push("</ul>");
          inUl = false;
        }
        if (!inOl) {
          output.push("<ol>");
          inOl = true;
        }
        output.push(`<li>${olMatch[2]}</li>`);
      } else {
        if (inUl) {
          output.push("</ul>");
          inUl = false;
        }
        if (inOl) {
          output.push("</ol>");
          inOl = false;
        }
        output.push(line);
      }
    }
    if (inUl) output.push("</ul>");
    if (inOl) output.push("</ol>");

    text = output.join("\n");

    // 9. Detect & Highlight Common Indian Legal Provisions
    text = text.replace(
      /\b(Section\s+\d+[A-Z]?(?:\s+of\s+(?:the\s+)?[A-Za-z\s]+)?|Article\s+\d+[A-Z]?|BNS|BNSS|BSA|IPC|CrPC|IEA|CPC|RTI Act|IT Act)\b/gi,
      '<span class="legal-tag">$1</span>'
    );

    // 10. Paragraphs & Line Breaks
    const paragraphs = text.split(/\n{2,}/);
    text = paragraphs
      .map(p => {
        p = p.trim();
        if (!p) return "";
        if (
          p.startsWith("<h") ||
          p.startsWith("<ul") ||
          p.startsWith("<ol") ||
          p.startsWith("<pre") ||
          p.startsWith("<block")
        ) {
          return p;
        }
        return `<p>${p.replace(/\n/g, "<br>")}</p>`;
      })
      .join("");

    // Restore Code Blocks
    codeBlocks.forEach((codeHtml, idx) => {
      text = text.replace(`__CODE_BLOCK_${idx}__`, codeHtml);
    });

    return text;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // ============================================================================
  // HELPER UTILITIES
  // ============================================================================

  function formatCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function formatTimestamp(isoString) {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return formatCurrentTime();
    }
  }

  function showTypingIndicator() {
    DOM.typingIndicator.classList.remove("d-none");
    scrollToBottom();
  }

  function hideTypingIndicator() {
    DOM.typingIndicator.classList.add("d-none");
  }

  function showWelcomeScreen() {
    DOM.welcomeScreen.classList.remove("d-none");
    DOM.messagesContainer.classList.add("d-none");
    DOM.messagesContainer.innerHTML = "";
    updateHeaderTitle("New Legal Query");
    DOM.sessionBadge.textContent = "Fresh Query";
  }

  function showMessagesContainer() {
    DOM.welcomeScreen.classList.add("d-none");
    DOM.messagesContainer.classList.remove("d-none");
  }

  function updateHeaderTitle(title) {
    DOM.activeChatTitle.textContent = title || "Legal Consultation";
  }

  function scrollToBottom(force = false) {
    if (force || isUserNearBottom()) {
      DOM.chatBody.scrollTo({
        top: DOM.chatBody.scrollHeight,
        behavior: force ? "auto" : "smooth",
      });
    }
  }

  function isUserNearBottom() {
    const threshold = 160;
    const position = DOM.chatBody.scrollTop + DOM.chatBody.clientHeight;
    return position >= DOM.chatBody.scrollHeight - threshold;
  }

  function showToast(message, type = "info") {
    if (!toastInstance) return;
    DOM.toastMessage.querySelector("span").textContent = message;

    const iconMap = {
      info: "bi-info-circle text-accent",
      success: "bi-check-circle text-success",
      warning: "bi-exclamation-triangle text-warning",
      danger: "bi-exclamation-octagon text-danger",
    };
    DOM.toastIcon.className = `bi me-2 ${iconMap[type] || iconMap.info}`;

    toastInstance.show();
  }

  function updateCharCounter() {
    const length = DOM.userInput.value.length;
    DOM.charCounter.textContent = `${length} / ${MAX_CHAR_LIMIT}`;

    DOM.charCounter.classList.remove("limit-near", "limit-max");
    if (length >= MAX_CHAR_LIMIT) {
      DOM.charCounter.classList.add("limit-max");
    } else if (length >= MAX_CHAR_LIMIT * 0.85) {
      DOM.charCounter.classList.add("limit-near");
    }

    DOM.btnSend.disabled = length === 0 || state.isRequestInProgress;
  }

  function adjustTextareaHeight() {
    DOM.userInput.style.height = "auto";
    const newHeight = Math.min(DOM.userInput.scrollHeight, 160);
    DOM.userInput.style.height = `${newHeight}px`;
  }

  function resetTextareaHeight() {
    DOM.userInput.style.height = "auto";
  }

  function clearActiveSession() {
    if (state.isRequestInProgress) {
      showToast("Please wait for the current legal query to finish processing.", "warning");
      return false;
    }
    state.activeSessionId = null;
    localStorage.removeItem(STORAGE_KEY_SESSION);
    showWelcomeScreen();
    highlightActiveConversation(null);
    return true;
  }

  function restoreActiveSession() {
    const savedId = localStorage.getItem(STORAGE_KEY_SESSION);
    if (savedId && savedId.trim()) {
      loadConversationHistory(savedId.trim());
    } else {
      showWelcomeScreen();
    }
  }

  function openRenameModal(sessionId, currentTitle) {
    state.pendingRenameSessionId = sessionId;
    DOM.renameSessionId.value = sessionId;
    DOM.renameTitleInput.value = currentTitle || "";
    if (renameModalInstance) renameModalInstance.show();
    setTimeout(() => DOM.renameTitleInput.focus(), 150);
  }

  function openDeleteModal(sessionId) {
    state.pendingDeleteSessionId = sessionId;
    DOM.deleteSessionId.value = sessionId;
    if (deleteModalInstance) deleteModalInstance.show();
  }

  function toggleMobileSidebar() {
    DOM.sidebar.classList.toggle("show");
    DOM.sidebarBackdrop.classList.toggle("show");
  }

  function closeMobileSidebar() {
    DOM.sidebar.classList.remove("show");
    DOM.sidebarBackdrop.classList.remove("show");
  }

  // ============================================================================
  // EVENT LISTENERS
  // ============================================================================
  function bindEventListeners() {
    // 1. Send Message on Button Click
    DOM.btnSend.addEventListener("click", () => {
      sendChatMessage(DOM.userInput.value);
    });

    // 2. Keyboard Send (Enter / Shift+Enter) & Auto-resize
    DOM.userInput.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage(DOM.userInput.value);
      }
    });

    DOM.userInput.addEventListener("input", () => {
      updateCharCounter();
      adjustTextareaHeight();
    });

    // 3. New Chat Buttons (Sidebar & Mobile)
    DOM.btnNewChat.addEventListener("click", () => {
      if (!clearActiveSession()) return;
      closeMobileSidebar();
      DOM.userInput.focus();
    });

    DOM.mobileNewChatBtn.addEventListener("click", () => {
      if (!clearActiveSession()) return;
      closeMobileSidebar();
      DOM.userInput.focus();
    });

    // 4. Reset / Clear View Action
    DOM.btnClearChat.addEventListener("click", () => {
      if (!clearActiveSession()) return;
      showToast("Chat view reset to fresh query.", "info");
    });

    // 5. Refresh Conversations List
    DOM.btnRefreshHistory.addEventListener("click", () => {
      loadConversationList();
      showToast("Refreshed conversation history.", "info");
    });

    // 6. Suggested Prompt Cards Click Handlers
    document.querySelectorAll(".prompt-card").forEach(card => {
      const handlePromptSelect = () => {
        if (state.isRequestInProgress) {
          showToast("Please wait for the current legal query to finish processing.", "warning");
          return;
        }
        const prompt = card.dataset.prompt;
        if (prompt) {
          DOM.userInput.value = prompt;
          updateCharCounter();
          sendChatMessage(prompt);
        }
      };

      card.addEventListener("click", handlePromptSelect);
      card.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handlePromptSelect();
        }
      });
    });

    // 7. Modal Actions: Confirm Rename
    DOM.renameTitleInput.addEventListener("keydown", e => {
      if (e.key === "Enter") {
        e.preventDefault();
        DOM.btnConfirmRename.click();
      }
    });

    DOM.btnConfirmRename.addEventListener("click", () => {
      const sessionId = DOM.renameSessionId.value;
      const newTitle = DOM.renameTitleInput.value.trim();
      if (!newTitle) {
        showToast("Title cannot be empty.", "warning");
        return;
      }
      if (renameModalInstance) renameModalInstance.hide();
      renameConversation(sessionId, newTitle);
    });

    // 8. Modal Actions: Confirm Delete
    DOM.btnConfirmDelete.addEventListener("click", () => {
      const sessionId = DOM.deleteSessionId.value;
      if (deleteModalInstance) deleteModalInstance.hide();
      deleteConversation(sessionId);
    });

    // 9. Mobile Sidebar Navigation Handlers
    DOM.mobileMenuBtn.addEventListener("click", toggleMobileSidebar);
    DOM.sidebarBackdrop.addEventListener("click", closeMobileSidebar);
  }
})();
