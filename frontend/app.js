const API_URL = "http://127.0.0.1:5000/triage";

// ── Main triage call ──
async function runTriage() {
  const message = document.getElementById("messageInput").value.trim();

  if (!message) {
    showError("Please enter a support message before running triage.");
    return;
  }

  setLoading(true);
  hideError();
  hideReport();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    renderReport(data.triage_report);

  } catch (err) {
    showError("Could not connect to the triage server. Is Flask running?");
  } finally {
    setLoading(false);
  }
}

// ── Render report into UI ──
function renderReport(r) {
  // Metadata
  document.getElementById("reportId").textContent   = r.metadata.report_id;
  document.getElementById("reportTime").textContent = r.metadata.timestamp;

  // Classification tags
  const urgency = r.classification.urgency;
  const intent  = r.classification.intent;

  const urgencyTag = document.getElementById("urgencyTag");
  urgencyTag.textContent  = urgencyEmoji(urgency) + " " + urgency.toUpperCase();
  urgencyTag.className    = `tag tag-${urgency}`;

  const intentTag = document.getElementById("intentTag");
  intentTag.textContent = intentEmoji(intent) + " " + intent.toUpperCase();
  intentTag.className   = `tag tag-${intent}`;

  // Entities table
  const labels = {
    property_ids:  "Property IDs",
    names:         "Names",
    dates:         "Dates",
    phone_numbers: "Phone Numbers",
    locations:     "Locations",
    amounts:       "Amounts",
  };

  const tbody = document.querySelector("#entityTable tbody");
  tbody.innerHTML = "";

  for (const [key, label] of Object.entries(labels)) {
    const values = r.entities[key];
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${label}</td>
      <td>${values && values.length ? values.join(", ") : "—"}</td>
    `;
    tbody.appendChild(tr);
  }

  // Routing & SLA
  document.getElementById("routingText").textContent = r.routing.assigned_to;
  document.getElementById("slaText").textContent     = "⏱️  SLA: " + r.routing.sla;

  // Draft response
  document.getElementById("draftResponse").textContent = r.draft_response;

  // Show panel
  document.getElementById("reportPanel").classList.remove("hidden");
  document.getElementById("reportPanel").scrollIntoView({ behavior: "smooth" });
}

// ── Copy draft to clipboard ──
function copyDraft() {
  const text = document.getElementById("draftResponse").textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector(".copy-btn");
    btn.textContent = "✅ Copied!";
    setTimeout(() => btn.textContent = "📋 Copy Draft", 2000);
  });
}

// ── Clear everything ──
function clearAll() {
  document.getElementById("messageInput").value = "";
  hideReport();
  hideError();
}

// ── Helpers ──
function setLoading(on) {
  const btn     = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("btnSpinner");
  btn.disabled = on;
  btnText.textContent = on ? "Analysing..." : "Run Triage";
  spinner.classList.toggle("hidden", !on);
}

function showError(msg) {
  const box = document.getElementById("errorBox");
  box.textContent = "⚠️  " + msg;
  box.classList.remove("hidden");
}

function hideError() {
  document.getElementById("errorBox").classList.add("hidden");
}

function hideReport() {
  document.getElementById("reportPanel").classList.add("hidden");
}

function urgencyEmoji(u) {
  return { urgent: "🔴", medium: "🟠", low: "🟢" }[u] || "⚪";
}

function intentEmoji(i) {
  return { complaint: "😤", query: "❓", booking: "📅" }[i] || "📌";
}
