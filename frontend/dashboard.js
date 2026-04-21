const API = "http://127.0.0.1:5000";

// Active filters state
const filters = { urgency: "", intent: "", status: "" };
let currentReportId  = null;
let selectedStatus   = null;

// ── Boot ──
document.addEventListener("DOMContentLoaded", loadDashboard);

async function loadDashboard() {
  const icon = document.getElementById("refreshIcon");
  if (icon) { icon.style.display = "inline-block"; icon.style.animation = "spin 0.6s linear infinite"; }
  await Promise.all([loadStats(), loadReports()]);
  if (icon) { icon.style.animation = "none"; }
}

// ─────────────────────────────────────────
// STATS
// ─────────────────────────────────────────

async function loadStats() {
  try {
    const res  = await fetch(`${API}/stats`);
    const data = await res.json();

    document.getElementById("statTotal").textContent    = data.total_reports    || 0;
    document.getElementById("statUrgent").textContent   = data.by_urgency?.urgent  || 0;
    document.getElementById("statMedium").textContent   = data.by_urgency?.medium  || 0;
    document.getElementById("statLow").textContent      = data.by_urgency?.low     || 0;
    document.getElementById("statPending").textContent  = data.by_status?.pending_review || 0;
    document.getElementById("statEscalated").textContent = data.by_status?.escalated || 0;
    document.getElementById("statResolved").textContent = data.by_status?.resolved || 0;
  } catch {
    console.error("Stats load failed");
  }
}

// ─────────────────────────────────────────
// LOAD TABLE
// ─────────────────────────────────────────

async function loadReports() {
  const tbody = document.getElementById("reportsBody");
  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="empty-row">
        <span class="loading-spinner"></span> Loading...
      </td>
    </tr>`;

  try {
    const params = new URLSearchParams();
    if (filters.urgency) params.append("urgency", filters.urgency);
    if (filters.intent)  params.append("intent",  filters.intent);
    if (filters.status)  params.append("status",  filters.status);

    const res  = await fetch(`${API}/reports?${params.toString()}`);
    const data = await res.json();

    document.getElementById("resultsCount").textContent =
      `${data.count} report${data.count !== 1 ? "s" : ""}`;

    if (data.count === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="empty-row">No reports match the current filters.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = "";
    data.reports.forEach(item => {
      const r  = item.triage_report;
      const id = r.metadata.report_id;
      const tr = document.createElement("tr");
      tr.onclick = () => openModal(id);

      tr.innerHTML = `
        <td>${id}</td>
        <td style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-muted)">
          ${r.metadata.timestamp}
        </td>
        <td>
          <span class="urgency-tag u-${r.classification.urgency}" style="font-size:0.82rem">
            ${urgencyEmoji(r.classification.urgency)} ${r.classification.urgency.toUpperCase()}
          </span>
        </td>
        <td>
          <span class="intent-tag i-${r.classification.intent}" style="font-size:0.82rem">
            ${intentEmoji(r.classification.intent)} ${r.classification.intent.toUpperCase()}
          </span>
        </td>
        <td class="preview-cell">${r.input.original_message}</td>
        <td>
          <span class="status-badge ${statusClass(r.metadata.status)}">
            ${statusLabel(r.metadata.status)}
          </span>
        </td>
        <td>
          <button class="view-btn" onclick="event.stopPropagation();openModal('${id}')">
            View →
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    document.getElementById("errorBox").classList.add("hidden");

  } catch {
    document.getElementById("errorBox").textContent =
      "⚠  Could not connect to server. Is Flask running on port 5000?";
    document.getElementById("errorBox").classList.remove("hidden");
  }
}

// ─────────────────────────────────────────
// FILTERS (pill-based)
// ─────────────────────────────────────────

function setFilter(el, type, val) {
  // Deactivate all pills of same type
  document.querySelectorAll(`.pill[data-type="${type}"]`).forEach(p => {
    p.classList.remove("active");
  });
  el.classList.add("active");

  filters[type] = val;
  loadReports();
}

// ─────────────────────────────────────────
// MODAL — OPEN
// ─────────────────────────────────────────

async function openModal(reportId) {
  currentReportId = reportId;
  selectedStatus  = null;

  try {
    const res  = await fetch(`${API}/reports/${reportId}`);
    const data = await res.json();
    const r    = data.triage_report;

    // Topbar
    document.getElementById("modalReportId").textContent  = r.metadata.report_id;
    document.getElementById("modalTimestamp").textContent = r.metadata.timestamp;

    // Message
    document.getElementById("modalMessage").textContent = r.input.original_message;

    // Classification
    const uTag = document.getElementById("modalUrgency");
    uTag.textContent = urgencyEmoji(r.classification.urgency) + "  " + r.classification.urgency.toUpperCase();
    uTag.className   = `urgency-tag u-${r.classification.urgency}`;

    const iTag = document.getElementById("modalIntent");
    iTag.textContent = intentEmoji(r.classification.intent) + "  " + r.classification.intent.toUpperCase();
    iTag.className   = `intent-tag i-${r.classification.intent}`;

    // Routing
    document.getElementById("modalRouting").textContent = r.routing.assigned_to;
    document.getElementById("modalSla").textContent     = "⏱  " + r.routing.sla;

    // Entities
    const entityLabels = {
      property_ids: "Property IDs", names: "Names",
      dates: "Dates", phone_numbers: "Phone Numbers",
      locations: "Locations", amounts: "Amounts",
    };
    const egrid = document.getElementById("modalEntitiesGrid");
    egrid.innerHTML = "";
    for (const [key, label] of Object.entries(entityLabels)) {
      const vals     = r.entities[key];
      const hasValue = vals && vals.length > 0;
      const div      = document.createElement("div");
      div.className  = `entity-item${hasValue ? " has-value" : ""}`;
      div.innerHTML  = `
        <div class="entity-label">${label}</div>
        <div class="entity-value ${hasValue ? "" : "empty"}">
          ${hasValue ? vals.join(", ") : "—"}
        </div>`;
      egrid.appendChild(div);
    }

    // Draft
    document.getElementById("modalDraft").textContent = r.draft_response;
    document.getElementById("modalCopyBtn").textContent = "⊕ Copy";

    // Status pills — pre-select current
    document.querySelectorAll(".status-pill").forEach(p => {
      p.classList.toggle("selected", p.dataset.val === r.metadata.status);
    });
    selectedStatus = r.metadata.status;

    document.getElementById("statusMsg").classList.add("hidden");

    // Show
    document.getElementById("modalOverlay").classList.remove("hidden");
    document.body.style.overflow = "hidden";

  } catch (err) {
    console.error("Modal load failed", err);
  }
}

// ─────────────────────────────────────────
// MODAL — CLOSE
// ─────────────────────────────────────────

function closeModal() {
  document.getElementById("modalOverlay").classList.add("hidden");
  document.body.style.overflow = "";
  currentReportId = null;
}

// Click outside to close
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("modalOverlay").addEventListener("click", e => {
    if (e.target === document.getElementById("modalOverlay")) closeModal();
  });
  // ESC key
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeModal();
  });
});

// ─────────────────────────────────────────
// STATUS PILLS SELECT
// ─────────────────────────────────────────

function selectStatus(el) {
  document.querySelectorAll(".status-pill").forEach(p => p.classList.remove("selected"));
  el.classList.add("selected");
  selectedStatus = el.dataset.val;
}

// ─────────────────────────────────────────
// UPDATE STATUS
// ─────────────────────────────────────────

async function updateStatus() {
  if (!currentReportId || !selectedStatus) return;

  try {
    const res = await fetch(`${API}/reports/${currentReportId}/status`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ status: selectedStatus }),
    });

    if (res.ok) {
      const msg = document.getElementById("statusMsg");
      msg.textContent = `✓ Status updated to "${selectedStatus.replace("_", " ")}"`;
      msg.classList.remove("hidden");

      // Refresh table + stats silently
      loadReports();
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
    const btn = document.getElementById("modalCopyBtn");
    btn.textContent = "✓ Copied";
    setTimeout(() => btn.textContent = "⊕ Copy", 2000);
  });
}

// ─────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────

function urgencyEmoji(u) { return { urgent: "🔴", medium: "🟠", low: "🟢" }[u] || "⚪"; }
function intentEmoji(i)  { return { complaint: "😤", query: "❓", booking: "📅" }[i] || "📌"; }

function statusClass(s) {
  return { pending_review: "sb-pending", escalated: "sb-escalated", resolved: "sb-resolved" }[s] || "sb-pending";
}

function statusLabel(s) {
  return { pending_review: "🕐 Pending", escalated: "🔺 Escalated", resolved: "✅ Resolved" }[s] || s;
}