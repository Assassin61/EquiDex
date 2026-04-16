/**
 * charts.js — FairProbe shared Chart.js utilities
 * Uses Chart.js 4.x loaded via CDN
 */

// ── Global Chart.js defaults (dark theme) ─────────────────────────────────────

Chart.defaults.color            = '#8892aa';
Chart.defaults.borderColor      = '#1e2535';
Chart.defaults.font.family      = "'Inter', system-ui, sans-serif";
Chart.defaults.font.size        = 12;
Chart.defaults.plugins.legend.labels.boxWidth  = 12;
Chart.defaults.plugins.legend.labels.padding   = 16;

// ── Color palette ─────────────────────────────────────────────────────────────

const COLORS = {
  accent:  '#4f6ef7',
  accent2: '#7c3aed',
  success: '#22c55e',
  warning: '#f59e0b',
  danger:  '#ef4444',
  info:    '#38bdf8',
  muted:   '#505a72',
};

const SEV_COLOR = {
  HIGH:   COLORS.danger,
  MEDIUM: COLORS.warning,
  LOW:    COLORS.success,
  NONE:   COLORS.info,
};

/** Returns a color based on acceptance rate (low=red, mid=yellow, high=green) */
function rateColor(rate) {
  if (rate >= 60) return COLORS.success;
  if (rate >= 35) return COLORS.warning;
  return COLORS.danger;
}

/** Build semi-transparent fill from a hex color */
function alpha(hex, a) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
}

/** Create a linear gradient on a canvas 2D context */
function makeGradient(ctx, color, direction = 'horizontal') {
  const w = ctx.canvas.width, h = ctx.canvas.height;
  const grad = direction === 'horizontal'
    ? ctx.createLinearGradient(0, 0, w, 0)
    : ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, alpha(color, 0.9));
  grad.addColorStop(1, alpha(color, 0.4));
  return grad;
}

// ── Shared plugin: center text for doughnut charts ───────────────────────────

const centerTextPlugin = {
  id: 'centerText',
  afterDraw(chart) {
    if (!chart.config._centerText) return;
    const { ctx, chartArea } = chart;
    const { top, bottom, left, right } = chartArea;
    const cx = (left + right) / 2;
    const cy = (top + bottom) / 2;
    const { line1, line2, color1, color2 } = chart.config._centerText;
    ctx.save();
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle    = color1 || '#f0f4ff';
    ctx.font         = `800 28px 'Inter', sans-serif`;
    ctx.fillText(line1, cx, cy - 10);
    if (line2) {
      ctx.fillStyle = color2 || '#8892aa';
      ctx.font      = `500 12px 'Inter', sans-serif`;
      ctx.fillText(line2, cx, cy + 16);
    }
    ctx.restore();
  }
};

Chart.register(centerTextPlugin);

// ── 1. Donut Chart (Accepted vs Rejected) ─────────────────────────────────────

function createDonutChart(canvasId, accepted, total) {
  const el = document.getElementById(canvasId);
  if (!el) return null;

  const rejected = total - accepted;
  const rate     = total ? Math.round((accepted / total) * 100) : 0;

  // Destroy prior instance if it exists
  if (el._chartInstance) el._chartInstance.destroy();

  const chart = new Chart(el, {
    type: 'doughnut',
    _centerText: {
      line1:  `${rate}%`,
      line2:  'Acceptance',
      color1: '#f0f4ff',
      color2: '#8892aa',
    },
    data: {
      labels: ['Accepted', 'Rejected'],
      datasets: [{
        data: [accepted, rejected],
        backgroundColor: [
          alpha(COLORS.success, 0.85),
          alpha(COLORS.danger,  0.75),
        ],
        borderColor: [
          COLORS.success,
          COLORS.danger,
        ],
        borderWidth: 2,
        hoverOffset: 8,
      }],
    },
    options: {
      cutout: '72%',
      animation: { animateRotate: true, duration: 700, easing: 'easeOutQuart' },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} (${Math.round(ctx.raw / total * 100)}%)`,
          },
        },
      },
      responsive: true,
      maintainAspectRatio: true,
    },
  });

  el._chartInstance = chart;
  return chart;
}

// ── 2. Horizontal Bar Chart (Acceptance rate by group) ───────────────────────

function createBarChart(canvasId, rows) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  if (el._chartInstance) el._chartInstance.destroy();

  const labels = rows.map(r => r.group);
  const rates  = rows.map(r => r.acceptance_rate);
  const colors = rows.map(r => rateColor(r.acceptance_rate));
  const bgs    = colors.map(c => alpha(c, 0.75));

  const chart = new Chart(el, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Acceptance Rate (%)',
        data: rates,
        backgroundColor: bgs,
        borderColor: colors,
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      animation: { duration: 600, easing: 'easeOutQuart' },
      scales: {
        x: {
          min: 0,
          max: 100,
          grid: { color: '#1e2535' },
          ticks: { callback: v => `${v}%` },
        },
        y: {
          grid: { display: false },
          ticks: { font: { weight: '600' } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const row = rows[ctx.dataIndex];
              return [
                ` Acceptance: ${ctx.raw}%`,
                ` Accepted: ${row.accepted} / ${row.total}`,
                ` vs Average: ${row.vs_average > 0 ? '+' : ''}${row.vs_average}%`,
              ];
            },
          },
        },
      },
      responsive: true,
      maintainAspectRatio: false,
    },
  });

  el._chartInstance = chart;
  return chart;
}

// ── 3. Stacked Bar — Accepted vs Rejected per group ──────────────────────────

function createStackedBarChart(canvasId, rows) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  if (el._chartInstance) el._chartInstance.destroy();

  const labels   = rows.map(r => r.group);
  const accepted = rows.map(r => r.accepted);
  const rejected = rows.map(r => r.total - r.accepted);

  const chart = new Chart(el, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Accepted',
          data: accepted,
          backgroundColor: alpha(COLORS.success, 0.75),
          borderColor: COLORS.success,
          borderWidth: 1.5,
          borderRadius: { topLeft: 6, topRight: 6 },
          borderSkipped: 'bottom',
          stack: 's',
        },
        {
          label: 'Rejected',
          data: rejected,
          backgroundColor: alpha(COLORS.danger, 0.65),
          borderColor: COLORS.danger,
          borderWidth: 1.5,
          stack: 's',
        },
      ],
    },
    options: {
      animation: { duration: 600, easing: 'easeOutQuart' },
      scales: {
        x: { grid: { display: false }, ticks: { font: { weight: '600' } } },
        y: { grid: { color: '#1e2535' }, stacked: true },
      },
      plugins: {
        legend: { position: 'top' },
        tooltip: { mode: 'index' },
      },
      responsive: true,
      maintainAspectRatio: false,
    },
  });

  el._chartInstance = chart;
  return chart;
}

// ── 4. Radar Chart — severity across all dimensions ──────────────────────────

function createRadarChart(canvasId, dimensionsData) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  if (el._chartInstance) el._chartInstance.destroy();

  const labels = Object.keys(dimensionsData);

  // For each dimension, get the max disparity (absolute vs_average)
  const maxDisparity = labels.map(dim => {
    const rows = dimensionsData[dim] || [];
    return rows.length ? Math.max(...rows.map(r => Math.abs(r.vs_average))) : 0;
  });

  const chart = new Chart(el, {
    type: 'radar',
    data: {
      labels: labels.map(l => l.replace('_', ' ')),
      datasets: [{
        label: 'Max Bias Disparity (%)',
        data: maxDisparity,
        fill: true,
        backgroundColor: alpha(COLORS.accent, 0.2),
        borderColor: COLORS.accent,
        pointBackgroundColor: maxDisparity.map(v => v >= 30 ? COLORS.danger : v >= 15 ? COLORS.warning : COLORS.success),
        pointBorderColor: '#0a0d14',
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2,
      }],
    },
    options: {
      animation: { duration: 700 },
      scales: {
        r: {
          min: 0,
          suggestedMax: 50,
          angleLines:    { color: '#1e2535' },
          grid:          { color: '#1e2535' },
          pointLabels:   { color: '#8892aa', font: { size: 12, weight: '600' } },
          ticks:         { color: '#505a72', backdropColor: 'transparent', callback: v => `${v}%` },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` Max disparity: ${ctx.raw}%`,
          },
        },
      },
      responsive: true,
      maintainAspectRatio: true,
    },
  });

  el._chartInstance = chart;
  return chart;
}

// ── 5. Severity Donut (for report page) ──────────────────────────────────────

function createSeverityDonut(canvasId, findings) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  if (el._chartInstance) el._chartInstance.destroy();

  const counts = { HIGH: 0, MEDIUM: 0, LOW: 0 };
  (findings || []).forEach(f => { if (counts[f.severity] !== undefined) counts[f.severity]++; });

  const labels = Object.keys(counts).filter(k => counts[k] > 0);
  const data   = labels.map(k => counts[k]);
  const colors = labels.map(k => SEV_COLOR[k]);

  const chart = new Chart(el, {
    type: 'doughnut',
    _centerText: {
      line1:  findings?.length || '0',
      line2:  'Findings',
      color1: '#f0f4ff',
      color2: '#8892aa',
    },
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.map(c => alpha(c, 0.8)),
        borderColor: colors,
        borderWidth: 2,
        hoverOffset: 8,
      }],
    },
    options: {
      cutout: '68%',
      animation: { duration: 700 },
      plugins: {
        legend: { position: 'right' },
      },
      responsive: true,
      maintainAspectRatio: true,
    },
  });

  el._chartInstance = chart;
  return chart;
}

// ── 6. Trend Line Chart (Acceptance Rate Over Time) ─────────────────────────

function createLineChart(canvasId, data) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  if (el._chartInstance) el._chartInstance.destroy();

  const labels = data.map(d => d.date);
  const rates  = data.map(d => d.rate);

  // Gradient fill under the line
  const ctx = el.getContext('2d');
  const gradient = makeGradient(ctx, COLORS.accent, 'vertical');

  const chart = new Chart(el, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Acceptance Rate (%)',
        data: rates,
        backgroundColor: gradient,
        borderColor: COLORS.accent,
        borderWidth: 2,
        pointBackgroundColor: COLORS.info,
        pointBorderColor: '#0a0d14',
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: true,
        tension: 0.4 // smoothed curves
      }],
    },
    options: {
      animation: { duration: 800, easing: 'easeOutQuart' },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#8892aa' } },
        y: {
          min: 0,
          max: 100,
          grid: { color: '#1e2535' },
          ticks: { color: '#8892aa', callback: v => `${v}%` },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` Acceptance Rate: ${ctx.raw}%`
          }
        }
      },
      responsive: true,
      maintainAspectRatio: false,
    },
  });

  el._chartInstance = chart;
  return chart;
}
