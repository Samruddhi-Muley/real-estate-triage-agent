from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TriageReport(db.Model):
    __tablename__ = "triage_reports"

    # ── Primary Key ──
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Metadata ──
    report_id     = db.Column(db.String(30),  unique=True, nullable=False)
    timestamp     = db.Column(db.DateTime,    default=datetime.utcnow)
    status        = db.Column(db.String(20),  default="pending_review")

    # ── Input ──
    original_message = db.Column(db.Text, nullable=False)

    # ── Classification ──
    urgency       = db.Column(db.String(10), nullable=False)
    intent        = db.Column(db.String(15), nullable=False)

    # ── Entities (stored as comma-separated strings) ──
    property_ids  = db.Column(db.String(200), default="")
    names         = db.Column(db.String(200), default="")
    dates         = db.Column(db.String(200), default="")
    phone_numbers = db.Column(db.String(200), default="")
    locations     = db.Column(db.String(200), default="")
    amounts       = db.Column(db.String(200), default="")

    # ── Routing ──
    assigned_to   = db.Column(db.String(100), default="")
    sla           = db.Column(db.String(50),  default="")

    # ── Draft Response ──
    draft_response = db.Column(db.Text, default="")

    def to_dict(self):
        """Converts the DB row back into the same JSON structure as before."""
        return {
            "triage_report": {
                "metadata": {
                    "report_id": self.report_id,
                    "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "status":    self.status,
                },
                "input": {
                    "original_message": self.original_message,
                    "message_length":   len(self.original_message),
                },
                "classification": {
                    "urgency": self.urgency,
                    "intent":  self.intent,
                },
                "entities": {
                    "property_ids":  self.property_ids.split(",")  if self.property_ids  else [],
                    "names":         self.names.split(",")          if self.names          else [],
                    "dates":         self.dates.split(",")          if self.dates          else [],
                    "phone_numbers": self.phone_numbers.split(",")  if self.phone_numbers  else [],
                    "locations":     self.locations.split(",")      if self.locations      else [],
                    "amounts":       self.amounts.split(",")        if self.amounts        else [],
                },
                "routing": {
                    "assigned_to": self.assigned_to,
                    "sla":         self.sla,
                },
                "draft_response": self.draft_response,
            }
        }

    def __repr__(self):
        return f"<TriageReport {self.report_id} | {self.urgency} {self.intent}>"