/**
 * history.js — Audit History page
 */

let allAuditLogs    = [];
let activeDetailId  = null;
let detailDimensions = [];
let detailStats     = {};
let detailActiveDim = 0;

document.addEventListener('DOMContentLoaded', async () => {
  await loadHistory();
});

async function loadHistory() {
  try {
    const appsData = await apiGetAllApplications();
    const allApps  = appsData.applications || [];

    if (!allApps.length) {
      document.getElementById('no-audits-banner').style.display = 'flex';
      document.getElementById('history-body').innerHTML =
        '<tr><td colspan="7" class="empty-row">No audits found. Run your first audit above.</td></tr>';
      return;
    }

    const auditMap = {};
    for (const app of allApps) {
      const id = app.audit_id;
      if (!auditMap[id]) auditMap[id] = { audit_id: id, total: 0, accepted: 0, source: app.source, timestamp: app.timestamp };
      auditMap[id].total++;
      if (app.decision === 'accepted') auditMap[id].accepted++;
    }

    allAuditLogs = Object.values(auditMap).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    renderHistoryTable();
  } catch (err) {
    document.getElementById('history-body').innerHTML =
      `<tr><td colspan="7" class="empty-row text-danger">Error: ${err.message}</td></tr>`;
  }
}

function renderHistoryTable() {
  const tbody = document.getElementById('history-body');
  tbody.innerHTML = allAuditLogs.map(a => {
    const rate      = a.total ? ((a.accepted / a.total) * 100).toFixed(1) : 0;
    const dateFmt   = new Date(a.timestamp).toLocaleString();
    const srcBadge  = a.source === 'uploaded'
      ? '<span class="badge badge-info">uploaded</span>'
      : '<span class="badge badge-accent">demo</span>';
    return `
      <tr>
        <td><span class="mono" style="color:var(--accent)">#${a.audit_id}</span></td>
        <td>${srcBadge}</td>
        <td class="mono">${a.total}</td>
        <td>${rateBar(parseFloat(rate))}</td>
        <td id="bias-${a.audit_id}"><span class="text-muted">—</span></td>
        <td class="text-muted" style="font-size:0.78rem">${dateFmt}</td>
        <td><button class="btn btn-ghost btn-sm" onclick="openDetail('${a.audit_id}')">View →</button></td>
      </tr>`;
  }).join('');

  allAuditLogs.forEach(a => fetchBiasForRow(a.audit_id));
}

async function fetchBiasForRow(auditId) {
  try {
    const data = await apiGetAuditStats(auditId);
    const rows = Object.values(data.stats?.dimensions ?? {}).flat();
    const sev  = getMaxSeverity(rows);
    const el   = document.getElementById(`bias-${auditId}`);
    if (el) el.innerHTML = `<span class="severity-pill severity-${sev}">${sev}</span>`;
  } catch { /* silent */ }
}

// ── Detail Panel ───────────────────────────────────────────────────────────────

async function openDetail(auditId) {
  activeDetailId  = auditId;
  detailActiveDim = 0;

  const panel = document.getElementById('detail-panel');
  document.getElementById('detail-id').textContent       = `#${auditId}`;
  document.getElementById('detail-result').style.display = 'none';
  document.getElementById('detail-stats-body').innerHTML =
    '<tr><td colspan="6" class="empty-row">Loading…</td></tr>';
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth' });

  try {
    const data       = await apiGetAuditStats(auditId);
    detailDimensions = Object.keys(data.stats?.dimensions ?? {});
    detailStats      = data.stats?.dimensions ?? {};
    renderDetailTabs();
    renderDetailTable(0);
    renderDetailCharts(0);
  } catch (err) {
    document.getElementById('detail-stats-body').innerHTML =
      `<tr><td colspan="6" class="empty-row text-danger">Error: ${err.message}</td></tr>`;
  }
}

function closeDetail() {
  document.getElementById('detail-panel').style.display = 'none';
  activeDetailId = null;
}

function renderDetailTabs() {
  const el = document.getElementById('detail-dimension-tabs');
  if (el && detailDimensions.length)
    el.innerHTML = buildDimensionTabs(detailDimensions, detailActiveDim, 'switchDetailDimension');
}

function switchDetailDimension(idx) {
  detailActiveDim = idx;
  renderDetailTabs();
  renderDetailTable(idx);
  renderDetailCharts(idx);
}

function renderDetailTable(idx) {
  const rows = detailStats[detailDimensions[idx]] ?? [];
  document.getElementById('detail-stats-body').innerHTML = buildStatsRows(rows);
}

function renderDetailCharts(idx) {
  const rows = detailStats[detailDimensions[idx]] ?? [];
  createStackedBarChart('detail-stacked-chart', rows);
  createBarChart('detail-bar-chart', rows);
}

// ── Detail Actions ──────────────────────────────────────────────────────────────

async function runDetailAction(type) {
  if (!activeDetailId) return;
  const resEl = document.getElementById('detail-result');
  resEl.style.display = 'block';
  resEl.className     = 'result-box is-loading';
  resEl.textContent   = `Calling AI for "${type}"… this may take 10–20 seconds.`;
  try {
    let result;
    if      (type === 'analyse')   result = await apiAnalyse(activeDetailId);
    else if (type === 'report')    result = await apiReport(activeDetailId);
    else if (type === 'summarize') result = await apiSummarize(activeDetailId);

    let display;
    if (type === 'analyse') {
      const a = result.analysis;
      display  = `Bias Detected: ${a.bias_detected ? 'YES ⚠' : 'NO ✓'}\nOverall Severity: ${a.overall_severity}\n\n${a.summary}\n\n`;
      a.findings?.forEach((f, i) => {
        display += `${i+1}. [${f.severity}] ${f.dimension} — ${f.affected_group}\n   ${f.evidence}\n\n`;
      });
    } else {
      display = result.report || result.summary;
    }
    showResult('detail-result', display);
  } catch (err) {
    showResult('detail-result', `Error: ${err.message}`, true);
  }
}

function getMaxSeverity(rows) {
  if (rows.some(r => r.severity === 'HIGH'))   return 'HIGH';
  if (rows.some(r => r.severity === 'MEDIUM')) return 'MEDIUM';
  if (rows.some(r => r.severity === 'LOW'))    return 'LOW';
  return 'NONE';
}
