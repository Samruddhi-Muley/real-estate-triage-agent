const API_URL = "http://127.0.0.1:5000/triage";

const SAMPLES = {
  urgent: "Hi, I'm Priya Sharma. The ceiling in my flat APT-2047 in Bandra West is leaking badly and my furniture is getting completely damaged. There's water everywhere. Please send a technician TODAY. This is an emergency. My number is 9876543210.",
  medium: "Hi, I'd like to schedule a property viewing for Unit B-12 in Powai on 20th April around 11am. Please confirm availability. My name is Rahul Mehta, contact: 9123456780.",
  low:    "Can you tell me what documents are needed for renting a 2BHK flat in Mumbai? Looking for a checklist of required paperwork.",
};

// ── Sample loader ──
function loadSample(type) {
  document.getElementById("messageInput").value = SAMPLES[type];
  updateCharCount();
}

// ── Char counter ──
function updateCharCount() {
  const len = document.getElementById("messageInput").value.length;
  document.getElementById("charCount").textContent = `${len} chars`;
}

// ── Main triage call ──
async function runTriage() {
  const message = document.getElementById("messageInput").value.trim();

  if (!message) {
    showError("Please enter or paste a support message before running triage.");
    return;
  }

  setLoading(true);
  hideError();
  hideReport();

  try {
    const response = await fetch(API_URL, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    renderReport(data.triage_report);

  } catch {
    showError("Could not connect to the triage server. Is Flask running on port 5000?");
  } finally {
    setLoading(false);
  }
}

// ── Render report ──
function renderReport(r) {
  // Metadata
  document.getElementById("reportIdBadge").textContent  = r.metadata.report_id;
  document.getElementById("reportTimestamp").textContent = r.metadata.timestamp;

  // Classification
  const urgency = r.classification.urgency;
  const intent  = r.classification.intent;

  const uTag = document.getElementById("urgencyTag");
  uTag.textContent = urgencyEmoji(urgency) + "  " + urgency.toUpperCase();
  uTag.className   = `urgency-tag u-${urgency}`;

  const iTag = document.getElementById("intentTag");
  iTag.textContent = intentEmoji(intent) + "  " + intent.toUpperCase();
  iTag.className   = `intent-tag i-${intent}`;

  // Routing
  document.getElementById("routingText").textContent = r.routing.assigned_to;
  document.getElementById("slaChip").textContent     = "⏱  " + r.routing.sla;

  // Entities
  const labels = {
    property_ids:  "Property IDs",
    names:         "Names",
    dates:         "Dates",
    phone_numbers: "Phone Numbers",
    locations:     "Locations",
    amounts:       "Amounts",
  };

  const grid = document.getElementById("entitiesGrid");
  grid.innerHTML = "";

  for (const [key, label] of Object.entries(labels)) {
    const vals     = r.entities[key];
    const hasValue = vals && vals.length > 0;
    const div      = document.createElement("div");
    div.className  = `entity-item${hasValue ? " has-value" : ""}`;
    div.innerHTML  = `
      <div class="entity-label">${label}</div>
      <div class="entity-value ${hasValue ? "" : "empty"}">
        ${hasValue ? vals.join(", ") : "—"}
      </div>
    `;
    grid.appendChild(div);
  }

  // Draft
  document.getElementById("draftResponse").textContent = r.draft_response;

  // Show panel
  const panel = document.getElementById("reportPanel");
  panel.classList.remove("hidden");
  setTimeout(() => panel.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
}

// ── Copy draft ──
function copyDraft() {
  const text = document.getElementById("draftResponse").textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById("copyBtn");
    btn.textContent = "✓ Copied";
    setTimeout(() => btn.textContent = "⊕ Copy", 2000);
  });
}

// ── Clear ──
function clearAll() {
  document.getElementById("messageInput").value = "";
  updateCharCount();
  hideReport();
  hideError();
}

// ── Helpers ──
function setLoading(on) {
  const btn     = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("btnSpinner");
  const icon    = document.querySelector(".btn-icon");

  btn.disabled        = on;
  btnText.textContent = on ? "Analysing..." : "Run Triage";
  spinner.classList.toggle("hidden", !on);
  if (icon) icon.classList.toggle("hidden", on);
}

function showError(msg) {
  const box = document.getElementById("errorBox");
  box.textContent = "⚠  " + msg;
  box.classList.remove("hidden");
}

function hideError()  { document.getElementById("errorBox").classList.add("hidden"); }
function hideReport() { document.getElementById("reportPanel").classList.add("hidden"); }

function urgencyEmoji(u) { return { urgent: "🔴", medium: "🟠", low: "🟢" }[u] || "⚪"; }
function intentEmoji(i)  { return { complaint: "😤", query: "❓", booking: "📅" }[i] || "📌"; }