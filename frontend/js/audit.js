/**
 * audit.js — Run/Upload Audit page
 */

let selectedFile  = null;
let currentMode   = 'demo';

// ── Mode Toggle ───────────────────────────────────────────────────────────────

function switchMode(mode) {
  currentMode = mode;
  document.getElementById('panel-demo').style.display   = mode === 'demo'   ? 'block' : 'none';
  document.getElementById('panel-upload').style.display = mode === 'upload' ? 'block' : 'none';
  document.getElementById('tab-demo').className   = 'mode-btn' + (mode === 'demo'   ? ' mode-btn--active' : '');
  document.getElementById('tab-upload').className = 'mode-btn' + (mode === 'upload' ? ' mode-btn--active' : '');
}

// Check URL hash on load to allow direct deep links (#upload)
document.addEventListener('DOMContentLoaded', () => {
  if (window.location.hash === '#upload') switchMode('upload');
});

// ── Format Tabs (in upload panel) ────────────────────────────────────────────

function showFmt(type) {
  document.getElementById('fmt-csv').style.display  = type === 'csv'  ? 'block' : 'none';
  document.getElementById('fmt-json').style.display = type === 'json' ? 'block' : 'none';
  document.querySelectorAll('.fmt-tab').forEach(btn => {
    btn.className = btn.textContent.toLowerCase().includes(type)
      ? 'fmt-tab fmt-tab--active'
      : 'fmt-tab';
  });
}

// ── Demo Audit ────────────────────────────────────────────────────────────────

async function runDemoAudit() {
  setLoading('btn-run-demo', 'run-label', 'run-icon', true, 'Run Demo Audit', '▷');
  const resEl = document.getElementById('demo-result');
  resEl.style.display = 'block';
  resEl.className     = 'result-box is-loading';
  resEl.textContent   = 'Running 500 candidates through the demo hiring AI…';

  try {
    const data = await apiRunAudit();
    resEl.className = 'result-box';
    resEl.innerHTML = `
      <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:0.75rem">
        <span>✅ Audit complete</span>
        <span class="mono" style="color:var(--accent)">#${data.audit_id}</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.5rem;margin-bottom:0.75rem">
        <div><span style="color:var(--text-3)">Processed:</span> <strong>${data.total_processed}</strong></div>
        <div><span style="color:var(--text-3)">Status:</span> <strong>${data.status}</strong></div>
        <div><span style="color:var(--text-3)">Source:</span> <strong>demo</strong></div>
      </div>
      <p style="color:var(--text-2);font-size:0.82rem">
        Next → <a class="inline-link" href="index.html">Dashboard</a> to view stats,
        or <a class="inline-link" href="report.html">Reports</a> to generate an AI analysis.
      </p>`;
  } catch (err) {
    resEl.className  = 'result-box is-error';
    resEl.textContent = `Error: ${err.message}`;
  } finally {
    setLoading('btn-run-demo', 'run-label', 'run-icon', false, 'Run Demo Audit', '▷');
  }
}

// ── File Input / Drop Zone ────────────────────────────────────────────────────

function handleDragOver(e) {
  e.preventDefault();
  document.getElementById('dropzone').classList.add('drag-over');
}

function handleDragLeave(e) {
  document.getElementById('dropzone').classList.remove('drag-over');
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropzone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

function processFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['csv', 'json'].includes(ext)) {
    alert('Please upload a .csv or .json file.');
    return;
  }
  selectedFile = file;

  // Show preview panel
  document.getElementById('file-preview').style.display = 'block';
  document.getElementById('file-name').textContent = file.name;
  document.getElementById('file-meta').textContent =
    `${ext.toUpperCase()} · ${(file.size / 1024).toFixed(1)} KB`;

  // Enable upload button
  document.getElementById('btn-upload').disabled = false;

  // Read and preview
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    if (ext === 'csv') previewCSV(content);
    if (ext === 'json') previewJSON(content);
  };
  reader.readAsText(file);
}

function previewCSV(text) {
  const lines  = text.trim().split('\n').slice(0, 6); // header + 5 rows
  if (lines.length < 2) return;

  const headers = parseCSVLine(lines[0]);
  const rows    = lines.slice(1).map(parseCSVLine);

  const headHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
  const bodyHTML = rows.map(r =>
    `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`
  ).join('');

  document.getElementById('csv-preview-wrap').style.display = 'block';
  document.getElementById('preview-head').innerHTML = headHTML;
  document.getElementById('preview-body').innerHTML = bodyHTML;
}

function previewJSON(text) {
  try {
    const data    = JSON.parse(text);
    const sample  = Array.isArray(data) ? data.slice(0, 5) : [data];
    const headers = Object.keys(sample[0] || {});
    const headHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
    const bodyHTML = sample.map(row =>
      `<tr>${headers.map(h => `<td>${row[h] ?? ''}</td>`).join('')}</tr>`
    ).join('');
    document.getElementById('csv-preview-wrap').style.display = 'block';
    document.getElementById('preview-head').innerHTML = headHTML;
    document.getElementById('preview-body').innerHTML = bodyHTML;
  } catch {
    // Invalid JSON — backend will handle proper error
  }
}

function parseCSVLine(line) {
  // Simple CSV parser (handles quoted fields)
  const result = [];
  let cur = '', inQuote = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') { inQuote = !inQuote; continue; }
    if (ch === ',' && !inQuote) { result.push(cur.trim()); cur = ''; continue; }
    cur += ch;
  }
  result.push(cur.trim());
  return result;
}

function clearFile() {
  selectedFile = null;
  document.getElementById('file-input').value = '';
  document.getElementById('file-preview').style.display = 'none';
  document.getElementById('csv-preview-wrap').style.display = 'none';
  document.getElementById('btn-upload').disabled = true;
  document.getElementById('upload-result').style.display = 'none';
}

// ── Upload Dataset ────────────────────────────────────────────────────────────

async function uploadDataset() {
  if (!selectedFile) return;

  setLoading('btn-upload', 'upload-label', 'upload-icon', true, 'Upload & Analyse', '⬆');
  const resEl = document.getElementById('upload-result');
  resEl.style.display = 'block';
  resEl.className     = 'result-box is-loading';
  resEl.textContent   = `Uploading "${selectedFile.name}"…`;

  try {
    const data = await apiUploadDataset(selectedFile);
    resEl.className = 'result-box';
    resEl.innerHTML = `
      <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:0.75rem">
        <span>✅ Upload successful</span>
        <span class="mono" style="color:var(--accent)">#${data.audit_id}</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.5rem;margin-bottom:0.75rem">
        <div><span style="color:var(--text-3)">Saved:</span> <strong>${data.total_processed} records</strong></div>
        <div><span style="color:var(--text-3)">Skipped:</span> <strong>${data.skipped}</strong></div>
        <div><span style="color:var(--text-3)">File:</span> <strong>${data.filename}</strong></div>
        <div><span style="color:var(--text-3)">Source:</span> <strong>uploaded</strong></div>
      </div>
      <p style="color:var(--text-2);font-size:0.82rem">
        Next → <a class="inline-link" href="index.html">Dashboard</a> to view bias stats,
        or <a class="inline-link" href="report.html">Reports</a> to run an AI analysis on this data.
      </p>`;
  } catch (err) {
    resEl.className   = 'result-box is-error';
    resEl.textContent = `Error: ${err.message}`;
  } finally {
    setLoading('btn-upload', 'upload-label', 'upload-icon', false, 'Upload & Analyse', '⬆');
  }
}
