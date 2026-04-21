import sqlite3

conn = sqlite3.connect('fairprobe.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('SELECT COUNT(*) as cnt FROM audit_logs')
print('Total audits:', cur.fetchone()['cnt'])

cur.execute('SELECT COUNT(*) as cnt FROM applications')
total = cur.fetchone()['cnt']

cur.execute("SELECT COUNT(*) as cnt FROM applications WHERE decision='accepted'")
accepted = cur.fetchone()['cnt']
print('Total applications:', total)
print('Accepted:', accepted, '(' + str(round(accepted/total*100,1)) + '%)')
print('Rejected:', total - accepted)

cur.execute("SELECT ethnicity, decision, COUNT(*) as cnt FROM applications GROUP BY ethnicity, decision ORDER BY ethnicity")
rows = cur.fetchall()
print()
print('--- Ethnicity breakdown ---')
eth = {}
for r in rows:
    e = r['ethnicity']
    if e not in eth:
        eth[e] = {'accepted': 0, 'total': 0}
    eth[e]['total'] += r['cnt']
    if r['decision'] == 'accepted':
        eth[e]['accepted'] += r['cnt']

for e, d in sorted(eth.items()):
    rate = round(d['accepted'] / d['total'] * 100, 1)
    bar = '#' * int(rate / 5)
    print(f"  {e:25s}  {d['accepted']:3d}/{d['total']:3d} = {rate:5.1f}%  {bar}")

cur.execute("SELECT source, COUNT(DISTINCT audit_id) as cnt FROM applications GROUP BY source")
print()
print('--- Audit sources ---')
for r in cur.fetchall():
    print(f"  {r['source']}: {r['cnt']} audit(s)")

cur.execute("SELECT audit_id, COUNT(*) as cnt, timestamp FROM applications GROUP BY audit_id ORDER BY timestamp DESC LIMIT 5")
print()
print('--- Latest 5 audits ---')
for r in cur.fetchall():
    print(f"  #{r['audit_id']}  {r['cnt']} records  {r['timestamp'][:19]}")

conn.close()
