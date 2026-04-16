from database.models import db, TriageReport


# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────

def save_report_to_db(report: dict) -> TriageReport:
    """Takes the full triage report dict and saves it as a DB row."""

    r  = report["triage_report"]
    m  = r["metadata"]
    cl = r["classification"]
    en = r["entities"]
    ro = r["routing"]

    record = TriageReport(
        report_id        = m["report_id"],
        status           = m["status"],
        original_message = r["input"]["original_message"],
        urgency          = cl["urgency"],
        intent           = cl["intent"],
        property_ids     = ",".join(en.get("property_ids",  [])),
        names            = ",".join(en.get("names",          [])),
        dates            = ",".join(en.get("dates",          [])),
        phone_numbers    = ",".join(en.get("phone_numbers",  [])),
        locations        = ",".join(en.get("locations",      [])),
        amounts          = ",".join(en.get("amounts",        [])),
        assigned_to      = ro["assigned_to"],
        sla              = ro["sla"],
        draft_response   = r["draft_response"],
    )

    db.session.add(record)
    db.session.commit()
    return record


# ─────────────────────────────────────────
# FETCH ALL
# ─────────────────────────────────────────

def get_all_reports(urgency=None, intent=None, status=None) -> list:
    """
    Fetches all reports from DB.
    Optional filters: urgency, intent, status
    """
    query = TriageReport.query

    if urgency:
        query = query.filter_by(urgency=urgency)
    if intent:
        query = query.filter_by(intent=intent)
    if status:
        query = query.filter_by(status=status)

    reports = query.order_by(TriageReport.timestamp.desc()).all()
    return [r.to_dict() for r in reports]


# ─────────────────────────────────────────
# FETCH ONE
# ─────────────────────────────────────────

def get_report_by_id(report_id: str) -> dict | None:
    """Fetches a single report by its report_id string."""
    record = TriageReport.query.filter_by(report_id=report_id).first()
    return record.to_dict() if record else None


# ─────────────────────────────────────────
# UPDATE STATUS
# ─────────────────────────────────────────

def update_report_status(report_id: str, new_status: str) -> dict | None:
    """
    Updates the status of a report.
    Valid statuses: pending_review / escalated / resolved
    """
    record = TriageReport.query.filter_by(report_id=report_id).first()

    if not record:
        return None

    record.status = new_status
    db.session.commit()
    return record.to_dict()


# ─────────────────────────────────────────
# STATS
# ─────────────────────────────────────────

def get_stats() -> dict:
    """Returns summary statistics for the dashboard."""
    from sqlalchemy import func

    total = TriageReport.query.count()

    urgency_counts = dict(
        db.session.query(
            TriageReport.urgency,
            func.count(TriageReport.urgency)
        ).group_by(TriageReport.urgency).all()
    )

    intent_counts = dict(
        db.session.query(
            TriageReport.intent,
            func.count(TriageReport.intent)
        ).group_by(TriageReport.intent).all()
    )

    status_counts = dict(
        db.session.query(
            TriageReport.status,
            func.count(TriageReport.status)
        ).group_by(TriageReport.status).all()
    )

    return {
        "total_reports":  total,
        "by_urgency":     urgency_counts,
        "by_intent":      intent_counts,
        "by_status":      status_counts,
    }