/**
 * config.js — EquiDex Frontend Configuration
 *
 * In development: leave EQUIDEX_API_BASE unset → defaults to localhost:8000
 * In production:  set this to your Cloud Run / Vercel service URL BEFORE api.js loads,
 *                 OR just edit the line below directly.
 */

window.EQUIDEX_API_BASE = 'http://127.0.0.1:8000'; // Local backend (no TLS for dev)
