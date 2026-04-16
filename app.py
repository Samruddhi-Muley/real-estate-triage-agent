from flask import Flask, request, jsonify
from flask_cors import CORS
from database.models import db
from database.db_manager import (
    get_all_reports,
    get_report_by_id,
    update_report_status,
    get_stats,
)
from output.report_builder import build_triage_report, save_report

app = Flask(__name__)
CORS(app)

# ── Database config ──
app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///triage.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Auto-create tables on first run
with app.app_context():
    db.create_all()
    print("✅ Database ready → triage.db")


# ─────────────────────────────────────────
# EXISTING ENDPOINTS
# ─────────────────────────────────────────

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Real Estate Triage Agent is running ✅"})


@app.route("/triage", methods=["POST"])
def triage():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field in request body"}), 400

    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        report = build_triage_report(message)
        save_report(report)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# NEW DATABASE ENDPOINTS
# ─────────────────────────────────────────

@app.route("/reports", methods=["GET"])
def list_reports():
    """
    GET /reports
    GET /reports?urgency=urgent
    GET /reports?intent=complaint
    GET /reports?status=pending_review
    """
    urgency = request.args.get("urgency")
    intent  = request.args.get("intent")
    status  = request.args.get("status")

    reports = get_all_reports(urgency=urgency, intent=intent, status=status)
    return jsonify({"reports": reports, "count": len(reports)}), 200


@app.route("/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    """GET /reports/TRG-20250416143022"""
    report = get_report_by_id(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(report), 200


@app.route("/reports/<report_id>/status", methods=["PATCH"])
def update_status(report_id):
    """
    PATCH /reports/TRG-20250416143022/status
    Body: {"status": "resolved"}
    Valid: pending_review / escalated / resolved
    """
    data = request.get_json()
    new_status = data.get("status")

    valid_statuses = ["pending_review", "escalated", "resolved"]
    if new_status not in valid_statuses:
        return jsonify({
            "error": f"Invalid status. Must be one of: {valid_statuses}"
        }), 400

    updated = update_report_status(report_id, new_status)
    if not updated:
        return jsonify({"error": "Report not found"}), 404

    return jsonify(updated), 200


@app.route("/stats", methods=["GET"])
def stats():
    """GET /stats — summary counts for dashboard"""
    return jsonify(get_stats()), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)