// Logika antarmuka chat: kirim pesan ke /api/chat dengan fetch()
// dan tampilkan balasan serta kandidat intent tanpa memuat ulang halaman.
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const btnClear = document.getElementById("btn-clear");
const learnMode = document.getElementById("learn-mode");

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

function addMessage(sender, text, meta) {
  const row = document.createElement("div");
  row.className = `msg msg-${sender}`;

  if (sender === "bot") {
    row.appendChild(createBotAvatar());
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  if (meta) {
    const small = document.createElement("small");
    small.className = "meta";
    small.textContent = meta;
    bubble.appendChild(small);
  }

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubble;
}

function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "msg msg-bot";
  row.appendChild(createBotAvatar());

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-typing";
  bubble.setAttribute("aria-label", "Bot sedang mengetik");
  bubble.innerHTML =
    '<span class="typing-dots"><span></span><span></span><span></span></span>';

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

async function showCandidates(bubble, text) {
  const res = await fetch("/api/explain", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, theme: THEME.id }),
  });
  const data = await res.json();

  const panel = document.createElement("div");
  panel.className = "explain-panel";

  const title = document.createElement("div");
  title.className = "explain-title";
  title.textContent = `Top 3 Kandidat Intent (Ambang ${data.threshold})`;
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
  bubble.appendChild(panel);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(text) {
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
    const bubble = addMessage("bot", data.reply, meta);
    if (learnMode.checked) await showCandidates(bubble, text);
  } catch (err) {
    typingRow.remove();
    addMessage("bot", "Gagal terhubung ke server. Periksa koneksi Anda.");
    console.error(err);
  } finally {
    input.disabled = false;
    input.focus();
  }
}

async function loadHistory() {
  const res = await fetch(`/api/history/${THEME.id}`);
  const rows = await res.json();
  if (rows.length === 0) {
    addMessage("bot", THEME.greeting);
    return;
  }
  rows.forEach((r) => addMessage(r.sender, r.text));
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => sendMessage(chip.textContent));
});

btnClear.addEventListener("click", async () => {
  await fetch(`/api/history/${THEME.id}`, { method: "DELETE" });
  messagesEl.innerHTML = "";
  addMessage("bot", THEME.greeting);
});

loadHistory();
