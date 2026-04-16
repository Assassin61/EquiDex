/**
 * api.js — FairProbe API service layer
 *
 * Single source of truth for the backend URL.
 * Change API_BASE to your Cloud Run URL before deploying.
 */

const API_BASE = window.FAIRPROBE_API_BASE || 'http://127.0.0.1:8000';

// ── Low-level fetch wrapper ─────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json', ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({ detail: res.statusText }));
  if (!res.ok) {
    const msg = data?.detail || `HTTP ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return data;
}

// ── Health ──────────────────────────────────────────────────────────────────

async function apiHealth() {
  return apiFetch('/');
}

// ── Audit ───────────────────────────────────────────────────────────────────

async function apiRunAudit() {
  return apiFetch('/audit/run', { method: 'POST' });
}

async function apiUploadDataset(file) {
  const body = new FormData();
  body.append('file', file);
  // Don't set Content-Type — browser sets it with the boundary
  return apiFetch('/audit/upload', { method: 'POST', body });
}

async function apiGetLatestAudit() {
  return apiFetch('/audit/latest');
}

async function apiGetAllStats() {
  return apiFetch('/audit/all/stats');
}

async function apiGetAuditStats(auditId, period = 'all_time') {
  return apiFetch(`/audit/${auditId}/stats?period=${period}`);
}

async function apiGetAuditLogs() {
  return apiFetch('/audit/all/stats'); // returns total_audits
}

async function apiGetAllApplications() {
  return apiFetch('/audit/all/applications');
}

async function apiGetAuditApplications(auditId) {
  return apiFetch(`/audit/${auditId}/applications`);
}

// ── Actions ─────────────────────────────────────────────────────────────────

async function apiAnalyse(auditId) {
  return apiFetch(`/action/analyse/${auditId}`, { method: 'POST' });
}

async function apiReport(auditId) {
  return apiFetch(`/action/report/${auditId}`, { method: 'POST' });
}

async function apiSummarize(auditId) {
  return apiFetch(`/action/summarize/${auditId}`, { method: 'POST' });
}

// ── Stats by dimension ───────────────────────────────────────────────────────

async function apiGetDimensionStats(auditId, dimension) {
  return apiFetch(`/stats/${auditId}/${dimension}`);
}

// ── Shared UI helpers ────────────────────────────────────────────────────────

function severityPill(sev) {
  return `<span class="severity-pill severity-${sev}">${sev}</span>`;
}

function rateBar(rate) {
  const pct = Math.min(rate, 100);
  let color = '#22c55e';
  if (pct < 40) color = '#ef4444';
  else if (pct < 60) color = '#f59e0b';
  return `
    <div class="rate-bar-wrap">
      <span>${rate}%</span>
      <div class="rate-bar">
        <div class="rate-bar-fill" style="width:${pct}%;background:${color}"></div>
      </div>
    </div>`;
}

function vsAvgCell(val) {
  const cls = val >= 0 ? 'text-success' : 'text-danger';
  const sign = val >= 0 ? '+' : '';
  return `<span class="${cls} mono">${sign}${val}%</span>`;
}

function buildStatsRows(rows) {
  if (!rows || !rows.length) {
    return '<tr><td colspan="6" class="empty-row">No data available</td></tr>';
  }
  return rows.map(r => `
    <tr class="row-${r.severity.toLowerCase()}">
      <td><strong>${r.group}</strong></td>
      <td class="mono">${r.total}</td>
      <td class="mono">${r.accepted}</td>
      <td>${rateBar(r.acceptance_rate)}</td>
      <td>${vsAvgCell(r.vs_average)}</td>
      <td>${severityPill(r.severity)}</td>
    </tr>`).join('');
}

function buildDimensionTabs(dimensions, activeIdx, onClickFn) {
  return dimensions.map((dim, i) =>
    `<button class="tab-btn ${i === activeIdx ? 'active' : ''}"
      onclick="${onClickFn}(${i})">${dim.replace('_', ' ')}</button>`
  ).join('');
}

function showResult(elId, content, isError = false) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.style.display = 'block';
  el.className = 'result-box' + (isError ? ' is-error' : '');
  el.textContent = content;
}

function showResultHTML(elId, html) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.style.display = 'block';
  el.className = 'result-box';
  el.innerHTML = html;
}

function setLoading(btnId, labelId, iconId, loading, defaultLabel, defaultIcon = '▷') {
  const btn  = document.getElementById(btnId);
  const lbl  = document.getElementById(labelId);
  const icon = document.getElementById(iconId);
  if (!btn) return;
  btn.disabled = loading;
  if (lbl) lbl.textContent = loading ? 'Working…' : defaultLabel;
  if (icon) icon.textContent = loading ? '⟳' : defaultIcon;
}

// ── API Status indicator (shared across all pages) ───────────────────────────

async function initApiStatus() {
  const dot   = document.getElementById('api-status-dot');
  const label = document.getElementById('api-status-label');
  if (!dot || !label) return;
  try {
    await apiHealth();
    dot.className   = 'status-dot online';
    label.textContent = 'API connected';
  } catch {
    dot.className   = 'status-dot offline';
    label.textContent = 'API offline';
  }
}

document.addEventListener('DOMContentLoaded', initApiStatus);
