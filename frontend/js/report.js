/**
 * report.js — Reports page
 */

let selectedAuditId = null;

document.addEventListener('DOMContentLoaded', async () => {
  await populateAuditSelector();
});

async function populateAuditSelector() {
  const select = document.getElementById('audit-select');
  try {
    const appsData = await apiGetAllApplications();
    const apps     = appsData.applications || [];

    if (!apps.length) {
      select.innerHTML = '<option value="">No audits found — run one first</option>';
      return;
    }

    const seen = new Set();
    const auditMap = {};
    for (const app of apps) {
      if (!seen.has(app.audit_id)) { seen.add(app.audit_id); auditMap[app.audit_id] = app.timestamp; }
    }

    const sorted = [...seen].sort((a, b) => new Date(auditMap[b]) - new Date(auditMap[a]));
    select.innerHTML = sorted.map((id, i) => {
      const ts = new Date(auditMap[id]).toLocaleString();
      return `<option value="${id}" ${i === 0 ? 'selected' : ''}>#${id}  (${ts})</option>`;
    }).join('');

    selectedAuditId = sorted[0];
  } catch (err) {
    select.innerHTML = `<option value="">Error loading audits: ${err.message}</option>`;
  }
}

async function loadReport() {
  const select = document.getElementById('audit-select');
  selectedAuditId = select.value;
  if (!selectedAuditId) return;

  document.getElementById('report-loading').style.display   = 'flex';
  document.getElementById('report-content').style.display   = 'none';
  document.getElementById('no-report-prompt').style.display = 'none';
  document.getElementById('findings-charts').style.display  = 'none';

  try {
    const analysisRes = await apiAnalyse(selectedAuditId);
    const reportRes   = await apiReport(selectedAuditId);
    const summaryRes  = await apiSummarize(selectedAuditId);
    renderReport(analysisRes.analysis, reportRes.report, summaryRes.summary);
  } catch (err) {
    document.getElementById('report-loading').style.display   = 'none';
    document.getElementById('no-report-prompt').style.display = 'block';
    document.getElementById('no-report-prompt').innerHTML     = `
      <div class="empty-icon">⚠</div>
      <p class="text-danger">Error: ${err.message}</p>
      <p style="margin-top:0.5rem;color:var(--text-3);font-size:0.8rem">Make sure the backend is running and your AI key is set.</p>`;
  }
}

function renderReport(analysis, report, summary) {
  document.getElementById('report-loading').style.display = 'none';
  document.getElementById('report-content').style.display = 'block';

  // ── Bias Analysis ─────────────────────────────────────────────────────
  const biasDetected = analysis?.bias_detected ?? false;
  const overallSev   = analysis?.overall_severity ?? 'NONE';

  const biasBadgeEl = document.getElementById('bias-badge');
  biasBadgeEl.textContent = biasDetected ? `BIAS DETECTED · ${overallSev}` : 'NO BIAS DETECTED';
  biasBadgeEl.className   = `badge badge-${biasDetected ? sevToBadge(overallSev) : 'success'}`;

  document.getElementById('analysis-summary').textContent = analysis?.summary ?? '';

  // ── Findings charts ───────────────────────────────────────────────────
  const findings = analysis?.findings ?? [];
  if (findings.length) {
    document.getElementById('findings-charts').style.display = 'grid';
    createSeverityDonut('severity-donut', findings);
    renderFindingsBarChart(findings);
  }

  // Findings list
  const findingsEl = document.getElementById('findings-list');
  findingsEl.innerHTML = findings.length
    ? findings.map(f => `
        <div class="finding-card">
          <div class="finding-header">
            <span class="severity-pill severity-${f.severity}">${f.severity}</span>
            <span class="finding-dim">${f.dimension}</span>
            <span class="finding-group">— ${f.affected_group}</span>
          </div>
          <p class="finding-evidence">${f.evidence}</p>
        </div>`).join('')
    : '<p class="text-muted" style="font-size:0.85rem">No specific findings.</p>';

  // ── Formal Report ─────────────────────────────────────────────────────
  document.getElementById('formal-report-text').textContent = report ?? 'No report generated.';

  // ── Summary ───────────────────────────────────────────────────────────
  document.getElementById('summary-text').textContent = summary ?? 'No summary generated.';
}

function renderFindingsBarChart(findings) {
  const el = document.getElementById('findings-bar');
  if (!el) return;
  if (el._chartInstance) el._chartInstance.destroy();

  // Count findings per dimension
  const dimCounts = {};
  const dimColors = {};
  findings.forEach(f => {
    dimCounts[f.dimension] = (dimCounts[f.dimension] || 0) + 1;
    // Use the worst severity color for that dimension
    const current = dimColors[f.dimension];
    const newColor = SEV_COLOR[f.severity];
    if (!current || f.severity === 'HIGH') dimColors[f.dimension] = newColor;
  });

  const labels = Object.keys(dimCounts);
  const data   = labels.map(l => dimCounts[l]);
  const colors = labels.map(l => dimColors[l] || SEV_COLOR.MEDIUM);

  const chart = new Chart(el, {
    type: 'bar',
    data: {
      labels: labels.map(l => l.replace('_', ' ')),
      datasets: [{
        label: 'Findings',
        data,
        backgroundColor: colors.map(c => alpha(c, 0.75)),
        borderColor: colors,
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      animation: { duration: 600 },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#1e2535' },
          ticks: { stepSize: 1 },
        },
        x: { grid: { display: false } },
      },
      plugins: { legend: { display: false } },
      responsive: true,
      maintainAspectRatio: false,
    },
  });
  el._chartInstance = chart;
}

function copyReport() {
  const text = document.getElementById('formal-report-text').textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector('[onclick="copyReport()"]');
    if (btn) { btn.textContent = '✓ Copied'; setTimeout(() => btn.textContent = 'Copy', 2000); }
  });
}

async function rerunActions() { await loadReport(); }

function sevToBadge(s) {
  return { HIGH:'danger', MEDIUM:'warning', LOW:'warning', NONE:'success' }[s] ?? 'ghost';
}
