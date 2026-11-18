// =====================================================================
// AegisBot Chat & Analytics Engine (Optimized Interaction Flows)
// =====================================================================
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const btnNewChat = document.getElementById("btn-new-chat");
const learnMode = document.getElementById("learn-mode");
const suggestionsBar = document.getElementById("suggestions-bar");
const toastContainer = document.getElementById("toast-container");

// Drawer elements
const btnStats = document.getElementById("btn-stats");
const statsDrawer = document.getElementById("stats-drawer");
const statsBackdrop = document.getElementById("stats-drawer-backdrop");
const btnCloseDrawer = document.getElementById("btn-close-drawer");

// Modal elements
const confirmModalBackdrop = document.getElementById("confirm-modal-backdrop");
const btnCancelClear = document.getElementById("btn-cancel-clear");
const btnConfirmClear = document.getElementById("btn-confirm-clear");

// State to track last user query for on-demand explain inspection
let lastUserMessage = "";

// ---------------------------------------------------------------------
// Utility: Toast Notification
// ---------------------------------------------------------------------
function showToast(message, duration = 2200) {
  if (!toastContainer) return;
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  toastContainer.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => toast.classList.add("toast-visible"));

  setTimeout(() => {
    toast.classList.remove("toast-visible");
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ---------------------------------------------------------------------
// SVG Helper
// ---------------------------------------------------------------------
function createBotAvatar() {
  const wrap = document.createElement("span");
  wrap.className = "msg-avatar";
  wrap.setAttribute("aria-hidden", "true");
  wrap.innerHTML =
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>' +
    '<path d="m9 12 2 2 4-4"/></svg>';
  return wrap;
}

// ---------------------------------------------------------------------
// Message Bubbles & Actions (1-Click Copy & Interactive Inspector)
// ---------------------------------------------------------------------
function addMessage(sender, text, meta = null, userQuery = "") {
  const row = document.createElement("div");
  row.className = `msg msg-${sender}`;

  if (sender === "bot") {
    row.appendChild(createBotAvatar());
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const contentEl = document.createElement("div");
  contentEl.className = "bubble-text";
  contentEl.textContent = text;
  bubble.appendChild(contentEl);

  // For bot message: attach Action Bar (Interactive Meta + 1-Click Copy)
  if (sender === "bot") {
    const actionsRow = document.createElement("div");
    actionsRow.className = "bubble-actions";

    // 1. Metadata Button / Inspector Trigger
    if (meta) {
      const metaBtn = document.createElement("button");
      metaBtn.type = "button";
      metaBtn.className = "meta-badge";
      metaBtn.title = "Klik untuk memeriksa perhitungan intent & skor kemiripan";
      metaBtn.setAttribute("aria-expanded", "false");
      metaBtn.innerHTML = `
        <span class="meta-dot"></span>
        <span class="meta-label">${meta}</span>
        <svg class="meta-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
      `;

      let explainPanel = null;
      metaBtn.addEventListener("click", async () => {
        const isExpanded = metaBtn.getAttribute("aria-expanded") === "true";
        if (isExpanded) {
          metaBtn.setAttribute("aria-expanded", "false");
          if (explainPanel) explainPanel.hidden = true;
        } else {
          metaBtn.setAttribute("aria-expanded", "true");
          if (!explainPanel) {
            const queryToInspect = userQuery || lastUserMessage || text;
            explainPanel = await createExplainPanel(queryToInspect);
            bubble.appendChild(explainPanel);
          } else {
            explainPanel.hidden = false;
          }
          messagesEl.scrollTop = messagesEl.scrollHeight;
        }
      });

      actionsRow.appendChild(metaBtn);

      // If learn-mode switch is checked, expand immediately
      if (learnMode && learnMode.checked) {
        metaBtn.click();
      }
    }

    // 2. 1-Click Copy Button
    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "btn-copy";
    copyBtn.title = "Salin panduan keamanan ini ke clipboard";
    copyBtn.innerHTML = `
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
      </svg>
      <span>Salin</span>
    `;

    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(text);
        copyBtn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span style="color: #22c55e; font-weight: 600;">Disalin!</span>
        `;
        showToast("Teks berhasil disalin ke clipboard");
        setTimeout(() => {
          copyBtn.innerHTML = `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
            </svg>
            <span>Salin</span>
          `;
        }, 1800);
      } catch (err) {
        showToast("Gagal menyalin teks.");
      }
    });

    actionsRow.appendChild(copyBtn);
    bubble.appendChild(actionsRow);
  }

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubble;
}

// ---------------------------------------------------------------------
// Typing Indicator (3-dot Pulse)
// ---------------------------------------------------------------------
function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "msg msg-bot msg-typing";
  row.appendChild(createBotAvatar());

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-typing";
  bubble.setAttribute("aria-label", "AegisBot sedang memproses...");
  bubble.innerHTML =
    '<span class="typing-dots"><span></span><span></span><span></span></span>';

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

// ---------------------------------------------------------------------
// Explain / Inspector Panel (On-Demand Evaluation)
// ---------------------------------------------------------------------
async function createExplainPanel(text) {
  const panel = document.createElement("div");
  panel.className = "explain-panel";

  try {
    const res = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, theme: THEME.id }),
    });
    const data = await res.json();

    const title = document.createElement("div");
    title.className = "explain-title";
    title.textContent = `Top 3 Kandidat Intent (Ambang: ${data.threshold})`;
    panel.appendChild(title);

    const list = document.createElement("ol");
    list.className = "candidates";
    data.candidates.forEach((c) => {
      const li = document.createElement("li");
      const passed = c.score >= data.threshold;
      li.className = passed ? "cand-item cand-pass" : "cand-item cand-fail";
      const statusLabel = passed ? "lolos ambang" : "di bawah ambang";
      li.textContent = `${c.intent} · ${c.score.toFixed(2)} (${statusLabel}) — pola “${c.pattern}”`;
      list.appendChild(li);
    });
    panel.appendChild(list);
  } catch (err) {
    panel.textContent = "Gagal memuat kandidat intent.";
  }
  return panel;
}

// ---------------------------------------------------------------------
// Welcoming Starter Cards (Inside Messages on Empty State)
// ---------------------------------------------------------------------
function renderWelcomeState() {
  messagesEl.innerHTML = "";

  const welcomeBox = document.createElement("div");
  welcomeBox.className = "welcome-box";
  welcomeBox.innerHTML = `
    <div class="welcome-header">
      <div class="welcome-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>
        </svg>
      </div>
      <h2>Halo, saya AegisBot 🛡️</h2>
      <p>${THEME.greeting}</p>
    </div>
    <div class="starter-cards-grid">
      <button type="button" class="starter-card" data-prompt="Cara bikin password kuat">
        <div class="starter-card-icon">🔑</div>
        <div class="starter-card-text">
          <strong>Password & 2FA</strong>
          <span>Passphrase aman & Bitwarden</span>
        </div>
      </button>
      <button type="button" class="starter-card" data-prompt="Ciri link phishing & APK kurir">
        <div class="starter-card-icon">🎣</div>
        <div class="starter-card-text">
          <strong>Deteksi Phishing</strong>
          <span>Scam APK kurir & tautan palsu</span>
        </div>
      </button>
      <button type="button" class="starter-card" data-prompt="Aman gak pakai Wi-Fi publik?">
        <div class="starter-card-icon">📶</div>
        <div class="starter-card-text">
          <strong>Keamanan Wi-Fi</strong>
          <span>Mitigasi MitM, VPN & DNS DoH</span>
        </div>
      </button>
      <button type="button" class="starter-card" data-prompt="Solusi akun kena hack">
        <div class="starter-card-icon">🚨</div>
        <div class="starter-card-text">
          <strong>Akun Diretas</strong>
          <span>Pertolongan pertama akun dibajak</span>
        </div>
      </button>
    </div>
  `;

  welcomeBox.querySelectorAll(".starter-card").forEach((card) => {
    card.addEventListener("click", () => {
      const prompt = card.getAttribute("data-prompt");
      if (prompt) sendMessage(prompt);
    });
  });

  messagesEl.appendChild(welcomeBox);
}

// ---------------------------------------------------------------------
// Send Message
// ---------------------------------------------------------------------
async function sendMessage(text) {
  // If welcome box is present, remove it to start active chat stream
  const welcome = messagesEl.querySelector(".welcome-box");
  if (welcome) welcome.remove();

  lastUserMessage = text;
  addMessage("user", text);
  const typingRow = addTypingIndicator();
  input.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, theme: THEME.id }),
    });
    const data = await res.json();
    typingRow.remove();

    if (!res.ok) {
      addMessage("bot", `Galat: ${data.error}`);
      return;
    }

    const meta = data.intent
      ? `intent: ${data.intent} · skor ${data.score.toFixed(2)}`
      : `tidak dikenali · skor ${data.score.toFixed(2)}`;

    addMessage("bot", data.reply, meta, text);
  } catch (err) {
    typingRow.remove();
    addMessage("bot", "Gagal terhubung ke server. Periksa koneksi Anda.");
    console.error(err);
  } finally {
    input.disabled = false;
    input.focus();
  }
}

// ---------------------------------------------------------------------
// Load History
// ---------------------------------------------------------------------
async function loadHistory() {
  try {
    const res = await fetch(`/api/history/${THEME.id}`);
    const rows = await res.json();
    if (!rows || rows.length === 0) {
      renderWelcomeState();
      return;
    }
    messagesEl.innerHTML = "";
    let lastQuery = "";
    rows.forEach((r) => {
      if (r.sender === "user") {
        lastQuery = r.text;
        addMessage("user", r.text);
      } else {
        const meta = r.intent
          ? `intent: ${r.intent} · skor ${Number(r.score || 0).toFixed(2)}`
          : (r.score !== null ? `skor ${Number(r.score).toFixed(2)}` : null);
        addMessage("bot", r.text, meta, lastQuery);
      }
    });
  } catch (e) {
    renderWelcomeState();
  }
}

// ---------------------------------------------------------------------
// Slide-Over Analytics Drawer (Zero Page Reload)
// ---------------------------------------------------------------------
async function openAnalyticsDrawer() {
  if (!statsDrawer || !statsBackdrop) return;
  statsDrawer.hidden = false;
  statsBackdrop.hidden = false;
  requestAnimationFrame(() => {
    statsDrawer.classList.add("drawer-open");
    statsBackdrop.classList.add("backdrop-open");
  });

  // Fetch live stats
  try {
    let res = await fetch(`/api/analytics/${THEME.id}`);
    if (!res.ok) {
      // Fallback to /api/stats/<theme_id>
      const statsRes = await fetch(`/api/stats/${THEME.id}`);
      const statsData = await statsRes.json();
      renderDrawerData({
        summary: { total: statsData.reduce((acc, c) => acc + c.jumlah, 0), persen_dikenali: 100, tidak_dikenali: 0, sesi: 1 },
        stats: statsData,
        unknown: [],
        threshold: 0.45,
      });
      return;
    }
    const data = await res.json();
    renderDrawerData(data);
  } catch (err) {
    console.error("Gagal memuat analitik:", err);
  }
}

function closeAnalyticsDrawer() {
  if (!statsDrawer || !statsBackdrop) return;
  statsDrawer.classList.remove("drawer-open");
  statsBackdrop.classList.remove("backdrop-open");
  setTimeout(() => {
    statsDrawer.hidden = true;
    statsBackdrop.hidden = true;
  }, 220);
}

function renderDrawerData(data) {
  const sum = data.summary || {};
  document.getElementById("stat-total").textContent = sum.total ?? 0;
  document.getElementById("stat-rate").textContent = (sum.persen_dikenali ?? 0) + "%";
  document.getElementById("stat-failed").textContent = sum.tidak_dikenali ?? 0;
  document.getElementById("stat-sessions").textContent = sum.sesi ?? 0;
  document.getElementById("drawer-threshold").textContent = data.threshold ?? 0.45;

  // Intent distribution
  const intentWrap = document.getElementById("drawer-intent-container");
  if (!data.stats || data.stats.length === 0) {
    intentWrap.innerHTML = '<p class="muted empty-state">Belum ada aktivitas obrolan pada sesi ini.</p>';
  } else {
    let rowsHtml = data.stats
      .map((s) => {
        const pct = sum.total ? Math.round((100 * s.jumlah) / sum.total) : 0;
        return `
          <tr>
            <td><span class="intent-tag">${s.intent}</span></td>
            <td class="num-cell">${s.jumlah}</td>
            <td>
              <div class="bar-wrap">
                <div class="bar"><span style="width: ${pct}%"></span></div>
                <span class="bar-pct">${pct}%</span>
              </div>
            </td>
          </tr>
        `;
      })
      .join("");

    intentWrap.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Intent</th>
            <th>Jumlah</th>
            <th>Proporsi</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    `;
  }

  // Unknown queries
  const unknownWrap = document.getElementById("drawer-unknown-container");
  if (!data.unknown || data.unknown.length === 0) {
    unknownWrap.innerHTML = '<p class="muted empty-state">Semua kueri berhasil dikenali dengan baik.</p>';
  } else {
    let unkHtml = data.unknown
      .map((u) => {
        return `
          <tr>
            <td>${u.text}</td>
            <td><span class="score-pill">${Number(u.score || 0).toFixed(2)}</span></td>
            <td class="time-cell">${u.created_at || "-"}</td>
          </tr>
        `;
      })
      .join("");

    unknownWrap.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Kueri</th>
            <th>Skor</th>
            <th>Waktu</th>
          </tr>
        </thead>
        <tbody>${unkHtml}</tbody>
      </table>
    `;
  }
}

// ---------------------------------------------------------------------
// Event Listeners
// ---------------------------------------------------------------------
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

// Suggestion chips click
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => sendMessage(chip.textContent.trim()));
});

// Reset / Sesi Baru with Confirmation Modal
if (btnNewChat) {
  btnNewChat.addEventListener("click", () => {
    confirmModalBackdrop.hidden = false;
    requestAnimationFrame(() => confirmModalBackdrop.classList.add("modal-open"));
  });
}

if (btnCancelClear) {
  btnCancelClear.addEventListener("click", () => {
    confirmModalBackdrop.classList.remove("modal-open");
    setTimeout(() => (confirmModalBackdrop.hidden = true), 200);
  });
}

if (btnConfirmClear) {
  btnConfirmClear.addEventListener("click", async () => {
    confirmModalBackdrop.classList.remove("modal-open");
    setTimeout(() => (confirmModalBackdrop.hidden = true), 200);

    try {
      await fetch(`/api/history/${THEME.id}`, { method: "DELETE" });
      renderWelcomeState();
      showToast("Sesi percakapan baru dimulai");
    } catch (e) {
      showToast("Gagal mereset sesi.");
    }
  });
}

// Drawer listeners
if (btnStats) {
  btnStats.addEventListener("click", openAnalyticsDrawer);
}
if (btnCloseDrawer) {
  btnCloseDrawer.addEventListener("click", closeAnalyticsDrawer);
}
if (statsBackdrop) {
  statsBackdrop.addEventListener("click", closeAnalyticsDrawer);
}

// Global Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    if (statsDrawer && !statsDrawer.hidden) closeAnalyticsDrawer();
    if (confirmModalBackdrop && !confirmModalBackdrop.hidden) {
      confirmModalBackdrop.classList.remove("modal-open");
      setTimeout(() => (confirmModalBackdrop.hidden = true), 200);
    }
  }
});

// Auto focus on page load
if (input) {
  setTimeout(() => input.focus(), 150);
}

// Initialize chat
loadHistory();
