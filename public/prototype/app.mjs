import { mockRequest, playerEvents, percent, zonesFor, ZONES } from './model.mjs';
const $ = id => document.getElementById(id);
const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = value => value == null ? 'No data' : Number(value).toFixed(1);
let db, view = 'player', plan;
function table(rows, unit = '') {
  return `<details><summary>View chart values</summary><table class="chart-table"><thead><tr><th scope="col">Category</th><th scope="col">Value</th></tr></thead><tbody>${rows.map(([label, value]) => `<tr><th scope="row">${esc(label)}</th><td>${fmt(value)}${unit}</td></tr>`).join('')}</tbody></table></details>`;
}
function bars(title, rows, unit = '', max = null, note = '') {
  const ceiling = max || Math.max(1, ...rows.map(r => Math.abs(r[1] || 0)));
  return `<article class="chart-card"><h3>${title}</h3><p>${note || 'All eight sample sessions.'}</p><div class="bars">${rows.map(([label, value]) => `<div><div class="bar-label"><span>${esc(label)}</span><strong>${fmt(value)}${unit}</strong></div><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100, Math.abs(value || 0) / ceiling * 100)}%;background:${value < 0 ? 'var(--orange)' : 'var(--accent)'}"></div></div></div>`).join('')}</div>${table(rows, unit)}</article>`;
}
function line(title, rows, unit = '', max = 100, note = '') {
  const points = rows.map((r, i) => [35 + i * 390 / Math.max(1, rows.length - 1), 170 - (r[1] || 0) / max * 140]);
  return `<article class="chart-card"><h3>${title}</h3><p>${note || 'Session order, September 2026. Hover or open values below.'}</p><svg viewBox="0 0 460 215" role="img" aria-label="${esc(title)}"><text x="4" y="32" fill="#b3c0b5" font-size="10">${max}</text><text x="8" y="174" fill="#b3c0b5" font-size="10">0</text><path d="M30 30V170H435" fill="none" stroke="#526458"/><polyline points="${points.map(p => p.join(',')).join(' ')}" fill="none" stroke="#c8f47b" stroke-width="3"/>${points.map((p, i) => `<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="#c8f47b"><title>${esc(rows[i][0])}: ${fmt(rows[i][1])}${unit}</title></circle><text x="${p[0]}" y="194" text-anchor="middle" font-size="10" fill="#b3c0b5">${i + 1}</text>`).join('')}</svg>${table(rows, unit)}</article>`;
}
function court(events) {
  return `<article class="chart-card"><h3>04 / Shot location map</h3><p>Latest session only · circles = made, crosses = missed · feet from hoop.</p><svg viewBox="0 0 500 310" role="img" aria-label="Latest session shot map"><rect x="10" y="10" width="480" height="280" fill="none" stroke="#526458"/><path d="M173 10V142H327V10 M39 10V60 M461 10V60 M39 60Q250 365 461 60" fill="none" stroke="#526458"/><circle cx="250" cy="40" r="7" fill="none" stroke="#c8f47b"/>${events.map(e => {
    const x = 250 + e.x * 9.3, y = 40 + e.y * 9.3;
    return e.made ? `<circle cx="${x}" cy="${y}" r="4" fill="#c8f47b"><title>${esc(e.zone)}: made</title></circle>` : `<path d="M${x-3} ${y-3}l6 6m0 -6l-6 6" stroke="#eead79" stroke-width="2"><title>${esc(e.zone)}: missed</title></path>`;
  }).join('')}</svg>${table(zonesFor(events).map(z => [z.zone + ' attempts', z.attempts]))}</article>`;
}
function matrix() {
  return `<article class="chart-card"><h3>10 / Player × zone accuracy</h3><p>Percent made; all sample sessions. Darker cells indicate lower accuracy.</p><table class="chart-table"><thead><tr><th>Player</th>${ZONES.map(z => `<th>${z}</th>`).join('')}</tr></thead><tbody>${db.players.map(p => `<tr><th scope="row">${esc(p.name)}</th>${zonesFor(playerEvents(db, p.id)).map(z => `<td style="background:rgba(200,244,123,${z.accuracy / 160})">${fmt(z.accuracy)}%</td>`).join('')}</tr>`).join('')}</tbody></table></article>`;
}
function render() {
  const id = $('player').value;
  const player = db.players.find(p => p.id === id);
  const sessions = mockRequest(db, 'GET', `/api/sessions?player_id=${id}`).data;
  const events = mockRequest(db, 'GET', `/api/shot-maps?player_id=${id}`).data.events;
  const ratings = mockRequest(db, 'GET', `/api/ratings?player_id=${id}`).data;
  const zones = zonesFor(events);
  const selectedEvents = s => events.filter(e => e.session_id === s.id);
  $('status').textContent = '';
  $('planner').hidden = view !== 'training';
  $('summary').innerHTML = (view === 'coach'
    ? [[db.players.length, 'players'], [db.sessions.length, 'sessions'], [db.events.length, 'attempts'], [fmt(percent(db.events)) + '%', 'roster accuracy']]
    : [[events.length, 'tracked attempts'], [fmt(percent(events)) + '%', 'shooting accuracy'], [sessions.length, 'practice sessions'], [fmt(ratings.at(-1)?.score), 'latest shooting index']])
    .map(([n, label]) => `<div><strong>${n}</strong><span>${label}</span></div>`).join('');
  $('view-label').textContent = view === 'coach' ? 'MORGAN LEE / DEMO DEVELOPMENT SQUAD' : player.name.toUpperCase() + ' / ' + player.position.toUpperCase();
  $('view-title').textContent = { player: 'See where the work is landing.', coach: 'One roster. A clearer picture.', training: 'Turn the pattern into practice.' }[view];
  $('view-note').textContent = view === 'coach' ? 'Roster charts cover all three players; the player selector applies to the other dashboards and API inspector.' : 'Eight fictional sessions. All metrics are descriptive; improvement is not a measured product outcome.';
  let html = '';
  if (view === 'player') {
    html += line('01 / Session shooting accuracy', sessions.map(s => [s.date, percent(selectedEvents(s))]), '%');
    html += bars('02 / Attempts by session', sessions.map(s => [s.date, selectedEvents(s).length]), '', null, 'Volume, not shooting quality.');
    html += bars('03 / Accuracy by court zone', zones.map(z => [z.zone, z.accuracy]), '%', 100, 'All zones have 120 attempts per player.');
    html += court(selectedEvents(sessions.at(-1)));
    html += line('05 / Descriptive shooting index', ratings.map(r => [r.session_id, r.score]), '', 100, 'Index = session FG% on a 0–100 scale. Not an independent or validated skill score.');
  } else if (view === 'coach') {
    html += bars('06 / Roster accuracy', db.players.map(p => [p.name, percent(playerEvents(db, p.id))]), '%', 100);
    html += bars('07 / Practice volume', db.players.map(p => [p.name, playerEvents(db, p.id).length]), ' shots');
    html += bars('08 / Latest vs first session', db.players.map(p => { const ss = db.sessions.filter(s => s.player_id === p.id); return [p.name, percent(db.events.filter(e => e.session_id === ss.at(-1).id)) - percent(db.events.filter(e => e.session_id === ss[0].id))]; }), ' pp', null, 'Percentage-point change; bars show magnitude, orange indicates a decline. Not a causal effect.');
    html += bars('09 / Time invested', db.players.map(p => [p.name, db.sessions.filter(s => s.player_id === p.id).reduce((n, s) => n + s.minutes, 0)]), ' min');
    html += matrix();
  } else {
    const result = mockRequest(db, 'POST', '/api/plans', { player_id: id, minutes: +$('minutes').value });
    if (result.status !== 201) throw new Error(result.error);
    plan = result.data;
    $('plan').innerHTML = `<p class="eyebrow">RULES-BASED PRACTICE PLAN</p><h3>${esc(plan.focus)} · ${plan.minutes} minutes</h3><p>${esc(plan.explanation)}</p><p>${plan.drills.map(d => `${esc(d.name)}: <strong>${d.minutes} min</strong>`).join(' → ')}</p>`;
    html += bars('11 / Gap to a demo 60% target', zones.map(z => [z.zone, Math.max(0, 60 - z.accuracy)]), ' pp', 60, 'Illustrative target only; not a validated benchmark and not used to rank zones.');
    html += bars('12 / Practice distribution', zones.map(z => [z.zone, 100 * z.attempts / events.length]), '%', 100);
    html += line('13 / Cumulative shooting accuracy', sessions.map((s, i) => [s.date, percent(sessions.slice(0, i + 1).flatMap(selectedEvents))]), '%', 100, 'Running total makes ÷ running total attempts.');
    html += bars('14 / Made vs missed', [['Made', events.filter(e => e.made).length], ['Missed', events.filter(e => !e.made).length]], ' shots');
    html += bars('15 / Recommended practice allocation', plan.drills.map(d => [d.name, d.minutes]), ' min', plan.minutes, '60% focus, 20% warm-up rounded down; remainder mixed review.');
  }
  $('charts').innerHTML = html;
}
function safeRender() { try { render(); } catch (e) { $('status').textContent = `Unable to render: ${e.message}. Reload to retry.`; } }
try {
  const response = await fetch('./db.json');
  if (!response.ok) throw new Error(`Data request returned ${response.status}`);
  db = await response.json();
  $('player').innerHTML = mockRequest(db, 'GET', '/api/players').data.map(p => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
  $('player').onchange = () => { $('response').textContent = 'Player changed. Run a request to inspect this player.'; safeRender(); };
  document.querySelectorAll('[data-view]').forEach(button => button.onclick = () => {
    view = button.dataset.view;
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    safeRender();
  });
  $('generate').onclick = safeRender;
  $('minutes').onchange = safeRender;
  $('download').onclick = () => {
    if (!plan) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(plan, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${plan.id}.json`; anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  $('request').onclick = () => {
    const endpoint = $('endpoint').value;
    const post = endpoint === 'plans';
    const path = `/api/${endpoint}` + (post || endpoint === 'players' ? '' : `?player_id=${$('player').value}`);
    $('response').textContent = `${post ? 'POST' : 'GET'} ${path}\n` + JSON.stringify(mockRequest(db, post ? 'POST' : 'GET', path, { player_id: $('player').value, minutes: +$('minutes').value }), null, 2);
  };
  safeRender();
} catch (error) { $('status').textContent = `Cannot load the demo: ${error.message}. Serve the public folder over HTTP and reload.`; }
