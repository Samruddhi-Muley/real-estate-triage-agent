from flask import Flask, request, jsonify
from flask_cors import CORS
from output.report_builder import build_triage_report, save_report

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Real Estate Triage Agent is running ✅"})

@app.route("/triage", methods=["POST"])
def triage():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        report = build_triage_report(message)
        save_report(report)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)