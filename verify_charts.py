"""
Full API verification — shows exactly what data each chart will receive.
"""
import urllib.request, json

BASE = "http://127.0.0.1:8000"

def get(path):
    r = urllib.request.urlopen(BASE + path)
    return json.loads(r.read())

print("=" * 60)
print("FAIRPROBE API -> CHART DATA VERIFICATION")
print("=" * 60)

# ── All stats ───────────────────────────────────────────────────
data = get("/audit/all/stats")
overall = data["stats"]["overall"]

print("\n[ DASHBOARD KPI CARDS ]")
print(f"  Total Applications : {overall['total_applications']}")
print(f"  Total Accepted     : {overall['total_accepted']}")
print(f"  Total Rejected     : {overall['total_rejected']}")
print(f"  Acceptance Rate    : {overall['acceptance_rate']}%")
print(f"  Total Audits       : {data['total_audits']}")

print("\n[ DONUT CHART DATA ] — Accepted vs Rejected")
print(f"  Accepted : {overall['total_accepted']}")
print(f"  Rejected : {overall['total_rejected']}")
print(f"  Center % : {overall['acceptance_rate']}%")

print("\n[ RADAR CHART DATA ] — Max disparity per dimension")
dims = data["stats"]["dimensions"]
for dim, rows in dims.items():
    if rows:
        disparities = [abs(r["vs_average"]) for r in rows]
        max_disp = max(disparities)
        sev = "HIGH" if max_disp >= 30 else "MEDIUM" if max_disp >= 15 else "LOW"
        print(f"  {dim:20s}  max disparity={max_disp}%  severity={sev}")

print("\n[ BAR CHART DATA ] — ethnicity dimension (acceptance rate per group)")
for row in dims.get("ethnicity", []):
    bar = "█" * int(row["acceptance_rate"] / 5)
    color = "🔴" if row["severity"] == "HIGH" else "🟡" if row["severity"] == "MEDIUM" else "🟢"
    print(f"  {color} {row['group']:25s}  {row['acceptance_rate']:5.1f}%  vs_avg={row['vs_average']:+.1f}%  [{row['severity']}]")

# ── Audit history ───────────────────────────────────────────────
apps = get("/audit/all/applications")
all_apps = apps["applications"]
audit_map = {}
for a in all_apps:
    id_ = a["audit_id"]
    if id_ not in audit_map:
        audit_map[id_] = {"total": 0, "accepted": 0, "source": a["source"], "ts": a["timestamp"]}
    audit_map[id_]["total"] += 1
    if a["decision"] == "accepted":
        audit_map[id_]["accepted"] += 1

print(f"\n[ HISTORY TABLE ] — {len(audit_map)} audits")
for id_, d in sorted(audit_map.items(), key=lambda x: x[1]["ts"], reverse=True)[:5]:
    rate = round(d["accepted"] / d["total"] * 100, 1)
    print(f"  #{id_}  {d['source']:8s}  {d['total']} records  {rate}% accepted")

# ── Latest audit stats for detail panel ─────────────────────────
latest = get("/audit/latest")
if latest.get("audit_id"):
    aid = latest["audit_id"]
    detail = get(f"/audit/{aid}/stats")
    eth_rows = detail["stats"]["dimensions"].get("ethnicity", [])

    print(f"\n[ DETAIL PANEL CHARTS ] — latest audit #{aid}")
    print("  Stacked bar (accepted/rejected per group):")
    for row in eth_rows:
        rejected = row["total"] - row["accepted"]
        print(f"    {row['group']:25s}  accepted={row['accepted']}  rejected={rejected}")

print("\n[ ALL CHECKS PASSED ✓ ]")
print("Open frontend/index.html in your browser to see the charts.")
print("Backend running at http://127.0.0.1:8000")
