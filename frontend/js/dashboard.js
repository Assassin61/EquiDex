/**
 * dashboard.js — FairProbe Dashboard page
 */

let dashDimensions = [];
let dashStats      = {};
let dashActiveDim  = 0;
let latestAuditId  = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadDashboard();
});

async function loadDashboard() {
  try {
    const data    = await apiGetAllStats();
    const overall = data.stats?.overall || {};

    // ── KPI Cards ──────────────────────────────────────────────────────
    document.getElementById('kpi-total').textContent =
      overall.total_applications?.toLocaleString() ?? '0';
    document.getElementById('kpi-rate').textContent =
      overall.acceptance_rate != null ? `${overall.acceptance_rate}%` : '—';
    document.getElementById('kpi-audits').textContent =
      data.total_audits?.toLocaleString() ?? '0';

    const allRows = Object.values(data.stats?.dimensions ?? {}).flat();
    const maxSev  = getMaxSeverity(allRows);
    const biasEl  = document.getElementById('kpi-bias');
    biasEl.textContent = maxSev;
    biasEl.className   = `kpi-value text-${sevToClass(maxSev)}`;
    document.getElementById('kpi-bias-card').style.borderColor = sevToBorderColor(maxSev);

    // ── Charts ──────────────────────────────────────────────────────────
    const accepted = overall.total_accepted ?? 0;
    const total    = overall.total_applications ?? 0;
    createDonutChart('donut-chart', accepted, total);
    createRadarChart('radar-chart', data.stats?.dimensions ?? {});

    // ── Dimension tabs & bar chart ──────────────────────────────────────
    dashDimensions = Object.keys(data.stats?.dimensions ?? {});
    dashStats      = data.stats?.dimensions ?? {};

    if (dashDimensions.length) {
      renderDimensionTabs();
      renderStatsTable(dashActiveDim);
      renderBarChart(dashActiveDim);
    } else {
      document.getElementById('no-data-banner').style.display = 'flex';
    }

    // ── Trend Line Chart ────────────────────────────────────────────────
    try {
      const appsResponse = await apiGetAllApplications();
      const apps = appsResponse.applications || [];
      const groupedByDay = {};

      apps.forEach(app => {
        if (!app.timestamp) return;
        const day = app.timestamp.substring(0, 10);
        if (!groupedByDay[day]) groupedByDay[day] = { total: 0, accepted: 0 };
        groupedByDay[day].total++;
        if (app.decision === 'accepted') groupedByDay[day].accepted++;
      });

      const trendData = Object.keys(groupedByDay).sort().map(day => {
        const d = groupedByDay[day];
        return {
          date: day,
          rate: d.total > 0 ? parseFloat(((d.accepted / d.total) * 100).toFixed(1)) : 0
        };
      });

      if (trendData.length > 0) {
        createLineChart('trend-line-chart', trendData);
      }
    } catch (e) {
      console.error('Failed to load trend line data', e);
    }

    // ── Latest audit ────────────────────────────────────────────────────
    const latest = await apiGetLatestAudit();
    latestAuditId = latest.audit_id;
    const auditBadge = document.getElementById('latest-audit-id');
    if (auditBadge) auditBadge.textContent = latestAuditId ? `#${latestAuditId}` : 'None';

  } catch (err) {
    document.getElementById('no-data-banner').style.display = 'flex';
    console.error('Dashboard load error:', err);
  }
}

// ── Dimension tabs ─────────────────────────────────────────────────────────────

function renderDimensionTabs() {
  const el = document.getElementById('dimension-tabs');
  if (el) el.innerHTML = buildDimensionTabs(dashDimensions, dashActiveDim, 'switchDashDimension');
}

function switchDashDimension(idx) {
  dashActiveDim = idx;
  renderDimensionTabs();
  renderStatsTable(idx);
  renderBarChart(idx);
}

function renderStatsTable(idx) {
  const rows = dashStats[dashDimensions[idx]] ?? [];
  document.getElementById('stats-body').innerHTML = buildStatsRows(rows);
}

function renderBarChart(idx) {
  const dim  = dashDimensions[idx];
  const rows = dashStats[dim] ?? [];
  const titleEl = document.getElementById('bar-chart-title');
  if (titleEl) titleEl.textContent = `Acceptance Rate — ${dim.replace('_', ' ')}`;
  createBarChart('bar-chart', rows);
}

// ── Severity helpers ───────────────────────────────────────────────────────────

function getMaxSeverity(rows) {
  if (rows.some(r => r.severity === 'HIGH'))   return 'HIGH';
  if (rows.some(r => r.severity === 'MEDIUM')) return 'MEDIUM';
  if (rows.some(r => r.severity === 'LOW'))    return 'LOW';
  return 'NONE';
}
function sevToClass(s)       { return { HIGH:'danger', MEDIUM:'warning', LOW:'success', NONE:'info' }[s] ?? 'muted'; }
function sevToBorderColor(s) {
  return { HIGH:'rgba(239,68,68,0.4)', MEDIUM:'rgba(245,158,11,0.4)', LOW:'rgba(34,197,94,0.3)', NONE:'rgba(56,189,248,0.3)' }[s] ?? 'var(--border)';
}

// ── Quick Actions ──────────────────────────────────────────────────────────────

async function runAction(type) {
  if (!latestAuditId) {
    showResult('action-result', '⚠ No audits found. Run or upload one first.', true);
    return;
  }
  const resEl = document.getElementById('action-result');
  resEl.style.display = 'block';
  resEl.className     = 'result-box is-loading';
  resEl.textContent   = `Calling AI for "${type}"… this may take 10–20 seconds.`;

  const btnMap = { analyse:'btn-analyse', report:'btn-report', summarize:'btn-summarize' };
  const btn = document.getElementById(btnMap[type]);
  if (btn) btn.style.opacity = '0.5';

  try {
    let result;
    if      (type === 'analyse')   result = await apiAnalyse(latestAuditId);
    else if (type === 'report')    result = await apiReport(latestAuditId);
    else if (type === 'summarize') result = await apiSummarize(latestAuditId);

    const display = type === 'analyse'
      ? formatAnalysis(result.analysis)
      : (result.report || result.summary || JSON.stringify(result, null, 2));
    showResult('action-result', display);
  } catch (err) {
    showResult('action-result', `Error: ${err.message}`, true);
  } finally {
    if (btn) btn.style.opacity = '1';
  }
}

function formatAnalysis(analysis) {
  if (!analysis) return 'No analysis returned.';
  let out = `Bias Detected: ${analysis.bias_detected ? 'YES ⚠' : 'NO ✓'}\n`;
  out    += `Overall Severity: ${analysis.overall_severity}\n\n`;
  out    += `Summary:\n${analysis.summary}\n\n`;
  if (analysis.findings?.length) {
    out += 'Findings:\n';
    analysis.findings.forEach((f, i) => {
      out += `\n  ${i+1}. [${f.severity}] ${f.dimension}\n`;
      out += `     Affected: ${f.affected_group}\n`;
      out += `     ${f.evidence}\n`;
    });
  }
  return out;
}
