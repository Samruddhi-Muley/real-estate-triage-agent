import requests

BASE = "http://127.0.0.1:5000"

# ── 1. Run a triage (saves to DB automatically) ──
print("\n1️⃣  Running triage...")
r = requests.post(f"{BASE}/triage", json={
    "message": "Hi I'm Priya Sharma. Ceiling in APT-2047 is leaking badly. Call 9876543210."
})
report_id = r.json()["triage_report"]["metadata"]["report_id"]
print(f"   Saved report: {report_id}")

# ── 2. Fetch all reports ──
print("\n2️⃣  Fetching all reports...")
r = requests.get(f"{BASE}/reports")
print(f"   Total reports in DB: {r.json()['count']}")

# ── 3. Fetch one report by ID ──
print(f"\n3️⃣  Fetching report {report_id}...")
r = requests.get(f"{BASE}/reports/{report_id}")
print(f"   Urgency: {r.json()['triage_report']['classification']['urgency']}")

# ── 4. Update status ──
print(f"\n4️⃣  Updating status to 'resolved'...")
r = requests.patch(f"{BASE}/reports/{report_id}/status",
                   json={"status": "resolved"})
print(f"   New status: {r.json()['triage_report']['metadata']['status']}")

# ── 5. Filter by urgency ──
print("\n5️⃣  Filtering urgent reports...")
r = requests.get(f"{BASE}/reports?urgency=urgent")
print(f"   Urgent reports: {r.json()['count']}")

# ── 6. Stats ──
print("\n6️⃣  Fetching stats...")
r = requests.get(f"{BASE}/stats")
print(f"   Stats: {r.json()}")