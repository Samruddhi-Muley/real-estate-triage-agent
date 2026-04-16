import json
import re
from datetime import datetime

from agent.tools.classifier import classify_message
from agent.tools.ner_extractor import extract_entities
from agent.tools.response_generator import generate_response


# ─────────────────────────────────────────
# 1. PRIORITY ROUTING RULES
# ─────────────────────────────────────────

ROUTING_RULES = {
    ("urgent", "complaint"):  "🔴 Escalate immediately → Senior Support Team",
    ("urgent", "query"):      "🔴 Escalate immediately → Senior Support Team",
    ("urgent", "booking"):    "🟠 Fast-track → Field Operations Team",
    ("medium", "complaint"):  "🟠 Assign → Standard Support Queue",
    ("medium", "query"):      "🟡 Assign → Info Desk Team",
    ("medium", "booking"):    "🟡 Assign → Scheduling Team",
    ("low",    "complaint"):  "🟡 Assign → Standard Support Queue",
    ("low",    "query"):      "🟢 Auto-reply eligible → Bot Response",
    ("low",    "booking"):    "🟢 Assign → Scheduling Team",
}

SLA_RULES = {
    "urgent": "Response within 1 hour",
    "medium": "Response within 24 hours",
    "low":    "Response within 72 hours",
}


# ─────────────────────────────────────────
# 2. REPORT BUILDER
# ─────────────────────────────────────────

def build_triage_report(message: str) -> dict:
    """
    Runs all 3 tools directly and assembles a
    clean structured JSON triage report.
    """

    print("\n⚙️  Running triage pipeline...\n")

    # --- Run all 3 tools ---
    print("  [1/3] Classifying message...")
    classification = classify_message(message)

    print("  [2/3] Extracting entities...")
    entities = extract_entities(message)

    print("  [3/3] Generating draft response...")
    draft_response = generate_response(message, classification, entities)

    # --- Routing & SLA ---
    urgency = classification.get("urgency", "medium")
    intent  = classification.get("intent",  "query")
    routing = ROUTING_RULES.get((urgency, intent), "🟡 Assign → Standard Support Queue")
    sla     = SLA_RULES.get(urgency, "Response within 24 hours")

    # --- Assemble report ---
    report = {
        "triage_report": {
            "metadata": {
                "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "report_id":      f"TRG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status":         "pending_review",
            },
            "input": {
                "original_message": message,
                "message_length":   len(message),
            },
            "classification": {
                "urgency": urgency,
                "intent":  intent,
            },
            "entities": {
                "property_ids":   entities.get("property_ids",   []),
                "names":          entities.get("names",          []),
                "dates":          entities.get("dates",          []),
                "phone_numbers":  entities.get("phone_numbers",  []),
                "locations":      entities.get("locations",      []),
                "amounts":        entities.get("amounts",        []),
            },
            "routing": {
                "assigned_to": routing,
                "sla":         sla,
            },
            "draft_response": draft_response,
        }
    }

    return report


# ─────────────────────────────────────────
# 3. PRETTY PRINTER
# ─────────────────────────────────────────

def print_report(report: dict):
    """Prints a human-readable version of the triage report."""

    r  = report["triage_report"]
    m  = r["metadata"]
    cl = r["classification"]
    en = r["entities"]
    ro = r["routing"]

    urgency_emoji = {"urgent": "🔴", "medium": "🟠", "low": "🟢"}.get(cl["urgency"], "⚪")
    intent_emoji  = {"complaint": "😤", "query": "❓", "booking": "📅"}.get(cl["intent"], "📌")

    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "   📋 REAL ESTATE SUPPORT TRIAGE REPORT".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    print(f"\n🆔  Report ID  : {m['report_id']}")
    print(f"🕐  Timestamp  : {m['timestamp']}")
    print(f"📌  Status     : {m['status']}")

    print("\n" + "─" * 60)
    print("📨  ORIGINAL MESSAGE")
    print("─" * 60)
    print(f"  {r['input']['original_message']}")

    print("\n" + "─" * 60)
    print("🏷️   CLASSIFICATION")
    print("─" * 60)
    print(f"  Urgency : {urgency_emoji} {cl['urgency'].upper()}")
    print(f"  Intent  : {intent_emoji} {cl['intent'].upper()}")

    print("\n" + "─" * 60)
    print("🔍  EXTRACTED ENTITIES")
    print("─" * 60)
    for key, val in en.items():
        label = key.replace("_", " ").title().ljust(16)
        print(f"  {label}: {', '.join(val) if val else '—'}")

    print("\n" + "─" * 60)
    print("📡  ROUTING & SLA")
    print("─" * 60)
    print(f"  {ro['assigned_to']}")
    print(f"  ⏱️  SLA : {ro['sla']}")

    print("\n" + "─" * 60)
    print("✉️   DRAFT RESPONSE")
    print("─" * 60)
    print(f"  {r['draft_response']}")
    print("\n" + "═" * 60)


def save_report(report: dict, filename: str = None):
    """
    Saves report to BOTH:
    - SQLite database (primary)
    - JSON file in output/reports/ (backup)
    """
    # ── Save to database ──
    from database.db_manager import save_report_to_db
    save_report_to_db(report)

    # ── Save JSON backup ──
    import os, json
    os.makedirs("output/reports", exist_ok=True)

    if not filename:
        report_id = report["triage_report"]["metadata"]["report_id"]
        filename  = f"output/reports/{report_id}.json"

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Report saved → Database + {filename}")
    return filename
