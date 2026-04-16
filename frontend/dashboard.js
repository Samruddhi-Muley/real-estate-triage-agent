const API = "http://127.0.0.1:5000";
let currentReportId = null;

// ── Boot ──
document.addEventListener("DOMContentLoaded", loadDashboard);

async function loadDashboard() {
  await Promise.all([loadStats(), loadReports()]);
}

// ─────────────────────────────────────────
// STATS
// ─────────────────────────────────────────

async function loadStats() {
  try {
    const res  = await fetch(`${API}/stats`);
    const data = await res.json();

    document.querySelector("#statTotal .stat-number").textContent =
      data.total_reports || 0;
    document.getElementById("statUrgent").textContent  =
      data.by_urgency?.urgent  || 0;
    document.getElementById("statMedium").textContent  =
      data.by_urgency?.medium  || 0;
    document.getElementById("statLow").textContent     =
      data.by_urgency?.low     || 0;
    document.getElementById("statPending").textContent =
      data.by_status?.pending_review || 0;
    document.getElementById("statResolved").textContent =
      data.by_status?.resolved || 0;

  } catch {
    console.error("Could not load stats");
  }
}

// ─────────────────────────────────────────
// LOAD REPORTS TABLE
// ─────────────────────────────────────────

async function loadReports(urgency = "", intent = "", status = "") {
  const tbody = document.getElementById("reportsBody");
  tbody.innerHTML = `<tr><td colspan="7" class="loading-row">Loading...</td></tr>`;

  try {
    const params = new URLSearchParams();
    if (urgency) params.append("urgency", urgency);
    if (intent)  params.append("intent",  intent);
    if (status)  params.append("status",  status);

    const res  = await fetch(`${API}/reports?${params.toString()}`);
    const data = await res.json();

    document.getElementById("resultsCount").textContent =
      `Showing ${data.count} report${data.count !== 1 ? "s" : ""}`;

    if (data.count === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="loading-row">No reports found.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = "";
    data.reports.forEach(item => {
      const r  = item.triage_report;
      const tr = document.createElement("tr");
      tr.onclick = () => openModal(r.metadata.report_id);
      tr.innerHTML = `
        <td>${r.metadata.report_id}</td>
        <td>${r.metadata.timestamp}</td>
        <td>
          <span class="tag tag-${r.classification.urgency}">
            ${urgencyEmoji(r.classification.urgency)}
            ${r.classification.urgency.toUpperCase()}
          </span>
        </td>
        <td>
          <span class="tag tag-${r.classification.intent}">
            ${intentEmoji(r.classification.intent)}
            ${r.classification.intent.toUpperCase()}
          </span>
        </td>
        <td>
          <span class="preview-text">
            ${r.input.original_message}
          </span>
        </td>
        <td>
          <span class="status-badge status-${r.metadata.status.replace("_review", "")}">
            ${statusLabel(r.metadata.status)}
          </span>
        </td>
        <td>
          <button class="view-btn"
            onclick="event.stopPropagation(); openModal('${r.metadata.report_id}')">
            View
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch {
    document.getElementById("errorBox").textContent =
      "⚠️ Could not connect to server. Is Flask running?";
    document.getElementById("errorBox").classList.remove("hidden");
  }
}

// ─────────────────────────────────────────
// FILTERS
// ─────────────────────────────────────────

function applyFilters() {
  const urgency = document.getElementById("filterUrgency").value;
  const intent  = document.getElementById("filterIntent").value;
  const status  = document.getElementById("filterStatus").value;
  loadReports(urgency, intent, status);
}

function clearFilters() {
  document.getElementById("filterUrgency").value = "";
  document.getElementById("filterIntent").value  = "";
  document.getElementById("filterStatus").value  = "";
  loadReports();
}

// ─────────────────────────────────────────
// MODAL
// ─────────────────────────────────────────

async function openModal(reportId) {
  currentReportId = reportId;

  try {
    const res  = await fetch(`${API}/reports/${reportId}`);
    const data = await res.json();
    const r    = data.triage_report;

    // Metadata
    document.getElementById("modalReportId").textContent  = r.metadata.report_id;
    document.getElementById("modalTimestamp").textContent = r.metadata.timestamp;

    // Message
    document.getElementById("modalMessage").textContent = r.input.original_message;

    // Classification
    const uTag = document.getElementById("modalUrgency");
    uTag.textContent = urgencyEmoji(r.classification.urgency) + " " +
                       r.classification.urgency.toUpperCase();
    uTag.className   = `tag tag-${r.classification.urgency}`;

    const iTag = document.getElementById("modalIntent");
    iTag.textContent = intentEmoji(r.classification.intent) + " " +
                       r.classification.intent.toUpperCase();
    iTag.className   = `tag tag-${r.classification.intent}`;

    // Entities
    const labels = {
      property_ids: "Property IDs", names: "Names",
      dates: "Dates", phone_numbers: "Phone Numbers",
      locations: "Locations", amounts: "Amounts",
    };

    const tbody = document.querySelector("#modalEntityTable tbody");
    tbody.innerHTML = "";
    for (const [key, label] of Object.entries(labels)) {
      const vals = r.entities[key];
      const tr   = document.createElement("tr");
      tr.innerHTML = `
        <td>${label}</td>
        <td>${vals && vals.length ? vals.join(", ") : "—"}</td>`;
      tbody.appendChild(tr);
    }

    // Routing & SLA
    document.getElementById("modalRouting").textContent = r.routing.assigned_to;
    document.getElementById("modalSla").textContent     = "⏱️ SLA: " + r.routing.sla;

    // Draft
    document.getElementById("modalDraft").textContent = r.draft_response;

    // Status dropdown
    document.getElementById("modalStatusSelect").value = r.metadata.status;
    document.getElementById("statusUpdateMsg").classList.add("hidden");

    // Show modal
    document.getElementById("modalOverlay").classList.remove("hidden");

  } catch (err) {
    console.error("Could not load report detail", err);
  }
}

function closeModal(event) {
  if (event && event.target !== document.getElementById("modalOverlay")) return;
  document.getElementById("modalOverlay").classList.add("hidden");
  currentReportId = null;
}

// ─────────────────────────────────────────
// UPDATE STATUS
// ─────────────────────────────────────────

async function updateStatus() {
  if (!currentReportId) return;

  const newStatus = document.getElementById("modalStatusSelect").value;

  try {
    const res = await fetch(`${API}/reports/${currentReportId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });

    if (res.ok) {
      const msg = document.getElementById("statusUpdateMsg");
      msg.textContent = `✅ Status updated to "${newStatus}"`;
      msg.classList.remove("hidden");

      // Refresh table and stats in background
      loadReports(
        document.getElementById("filterUrgency").value,
        document.getElementById("filterIntent").value,
        document.getElementById("filterStatus").value
      );
      loadStats();
    }
  } catch {
    console.error("Status update failed");
  }
}

// ─────────────────────────────────────────
// COPY DRAFT
// ─────────────────────────────────────────

function copyModalDraft() {
  const text = document.getElementById("modalDraft").textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector(".copy-btn");
    btn.textContent = "✅ Copied!";
    setTimeout(() => btn.textContent = "📋 Copy Draft", 2000);
  });
}

// ─────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────

function urgencyEmoji(u) {
  return { urgent: "🔴", medium: "🟠", low: "🟢" }[u] || "⚪";
}

function intentEmoji(i) {
  return { complaint: "😤", query: "❓", booking: "📅" }[i] || "📌";
}

function statusLabel(s) {
  return { pending_review: "🕐 Pending", escalated: "🔺 Escalated",
           resolved: "✅ Resolved" }[s] || s;
}