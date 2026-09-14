// NBA Player Efficiency Analysis — Frontend
// Loads CSV data via fetch, renders Plotly charts

const DATA_CACHE = {};
const PLOTLY_DARK = {
    paper_bgcolor: '#0e1117',
    plot_bgcolor: '#0e1117',
    font: { color: '#c9d1d9', family: '-apple-system, sans-serif' },
    xaxis: { gridcolor: '#21262d', zerolinecolor: '#30363d' },
    yaxis: { gridcolor: '#21262d', zerolinecolor: '#30363d' },
    margin: { l: 50, r: 20, t: 40, b: 40 },
};

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

async function loadCSV(filename) {
    if (DATA_CACHE[filename]) return DATA_CACHE[filename];

    const resp = await fetch(`/data/${filename}.csv`);
    if (!resp.ok) throw new Error(`Failed to load ${filename}`);
    const text = await resp.text();
    const data = parseCSV(text);
    DATA_CACHE[filename] = data;
    return data;
}

function parseCSV(text) {
    const lines = text.split('\n');
    if (lines.length < 2) return [];
    const headers = parseCSVLine(lines[0]);
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        const values = parseCSVLine(line);
        const obj = {};
        headers.forEach((h, j) => { obj[h] = values[j] || ''; });
        rows.push(obj);
    }
    return rows;
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (inQuotes) {
            if (ch === '"' && line[i + 1] === '"') { current += '"'; i++; }
            else if (ch === '"') { inQuotes = false; }
            else { current += ch; }
        } else {
            if (ch === '"') { inQuotes = true; }
            else if (ch === ',') { result.push(current); current = ''; }
            else { current += ch; }
        }
    }
    result.push(current);
    return result;
}

function toNum(val) {
    const n = parseFloat(val);
    return isNaN(n) ? null : n;
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById('page-' + btn.dataset.page).classList.add('active');
        renderCurrentPage(btn.dataset.page);
    });
});

// ---------------------------------------------------------------------------
// Court drawing helper
// ---------------------------------------------------------------------------

function courtShapes(color = '#30363d') {
    const shapes = [
        // Hoop
        { type: 'circle', x0: -7.5, y0: -7.5, x1: 7.5, y1: 7.5, line: { color, width: 1 } },
        // Backboard
        { type: 'line', x0: -30, y0: -7.5, x1: 30, y1: -7.5, line: { color, width: 1 } },
        // Outer paint
        { type: 'rect', x0: -80, y0: -47.5, x1: 80, y1: 142.5, line: { color, width: 1 } },
        // Inner paint
        { type: 'rect', x0: -60, y0: -47.5, x1: 60, y1: 142.5, line: { color, width: 1 } },
        // Free throw circle
        { type: 'circle', x0: -60, y0: 77.5, x1: 60, y1: 197.5, line: { color, width: 1 } },
        // Restricted area
        { type: 'circle', x0: -40, y0: -40, x1: 40, y1: 40, line: { color, width: 1 } },
        // Corner 3 left
        { type: 'line', x0: -220, y0: -47.5, x1: -220, y1: 45, line: { color, width: 1 } },
        // Corner 3 right
        { type: 'line', x0: 220, y0: -47.5, x1: 220, y1: 45, line: { color, width: 1 } },
        // Baseline
        { type: 'line', x0: -250, y0: -47.5, x1: 250, y1: -47.5, line: { color, width: 1 } },
    ];
    return shapes;
}

function threePointArc(color = '#30363d') {
    const x = [], y = [];
    for (let a = 22; a <= 158; a += 1.5) {
        const rad = a * Math.PI / 180;
        x.push(237.5 * Math.cos(rad));
        y.push(237.5 * Math.sin(rad));
    }
    return { x, y, mode: 'lines', line: { color, width: 1 }, showlegend: false, hoverinfo: 'skip' };
}

function courtLayout() {
    return {
        shapes: courtShapes(),
        xaxis: { range: [-250, 250], showgrid: false, zeroline: false, showticklabels: false, ...PLOTLY_DARK.xaxis },
        yaxis: { range: [-50, 420], showgrid: false, zeroline: false, showticklabels: false, scaleanchor: 'x', ...PLOTLY_DARK.yaxis },
    };
}

// ---------------------------------------------------------------------------
// Metric card helper
// ---------------------------------------------------------------------------

function renderMetrics(containerId, metrics) {
    const el = document.getElementById(containerId);
    el.innerHTML = metrics.map(m =>
        `<div class="metric-card"><div class="label">${m.label}</div><div class="value">${m.value}</div></div>`
    ).join('');
}

// ---------------------------------------------------------------------------
// Table helper
// ---------------------------------------------------------------------------

function renderTable(containerId, headers, rows) {
    const el = document.getElementById(containerId);
    const ths = headers.map(h => `<th>${h}</th>`).join('');
    const trs = rows.map(r =>
        '<tr>' + r.map(c => `<td>${c ?? ''}</td>`).join('') + '</tr>'
    ).join('');
    el.innerHTML = `<table><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`;
}

// ---------------------------------------------------------------------------
// Populate select helpers
// ---------------------------------------------------------------------------

function populateSelect(id, options, defaultVal) {
    const sel = document.getElementById(id);
    sel.innerHTML = options.map(o => `<option value="${o}"${o === defaultVal ? ' selected' : ''}>${o}</option>`).join('');
}

function getPlayers(data) {
    const set = new Set();
    data.forEach(r => set.add(r.PLAYER_NAME_LABEL || r.PLAYER));
    return [...set].sort();
}

// ---------------------------------------------------------------------------
// Page: Shot Chart
// ---------------------------------------------------------------------------

async function renderShotChart() {
    const data = await loadCSV('master_shot_chart');
    const zones = await loadCSV('all_players_zone_stats');
    const players = getPlayers(data);

    populateSelect('sc-player', players, 'Stephen Curry');

    async function draw() {
        const player = document.getElementById('sc-player').value;
        const filter = document.getElementById('sc-filter').value;

        let pData = data.filter(r => r.PLAYER_NAME_LABEL === player);
        const totalShots = pData.length;
        const fgPct = pData.length > 0 ? (pData.filter(r => r.SHOT_MADE_FLAG === '1').length / pData.length * 100).toFixed(1) : 0;
        const avgDist = pData.length > 0 ? (pData.reduce((s, r) => s + (toNum(r.CALC_DISTANCE_FT) || 0), 0) / pData.length).toFixed(1) : 0;

        if (filter === 'made') pData = pData.filter(r => r.SHOT_MADE_FLAG === '1');
        else if (filter === 'missed') pData = pData.filter(r => r.SHOT_MADE_FLAG === '0');

        renderMetrics('sc-metrics', [
            { label: 'Total Shots', value: totalShots.toLocaleString() },
            { label: 'FG%', value: fgPct + '%' },
            { label: 'Avg Distance', value: avgDist + ' ft' },
            { label: 'Showing', value: pData.length.toLocaleString() },
        ]);

        const colors = pData.map(r => r.RESULT === 'Made' ? '#2ecc71' : '#e74c3c');

        const traces = [
            {
                x: pData.map(r => toNum(r.LOC_X)),
                y: pData.map(r => toNum(r.LOC_Y)),
                mode: 'markers',
                marker: { size: 4, color: colors, opacity: 0.5 },
                text: pData.map(r => `${r.ACTION_TYPE || ''}<br>${r.SHOT_ZONE_BASIC || ''}<br>${r.RESULT || ''}`),
                hoverinfo: 'text',
                showlegend: false,
            },
            threePointArc(),
        ];

        Plotly.newPlot('sc-chart', traces, {
            ...PLOTLY_DARK, ...courtLayout(),
            height: 550, title: `${player} — Shot Chart`,
        }, { responsive: true });

        // Zone bars
        const pZones = zones.filter(r => r.PLAYER === player).sort((a, b) => toNum(b.FGA) - toNum(a.FGA));
        if (pZones.length > 0) {
            Plotly.newPlot('sc-zones', [{
                x: pZones.map(r => r.SHOT_ZONE_BASIC),
                y: pZones.map(r => toNum(r.FGA)),
                text: pZones.map(r => (toNum(r.FG_PCT) * 100).toFixed(1) + '%'),
                textposition: 'outside',
                type: 'bar',
                marker: {
                    color: pZones.map(r => toNum(r.FG_PCT)),
                    colorscale: 'RdYlGn', cmin: 0.2, cmax: 0.7,
                },
            }], { ...PLOTLY_DARK, height: 350, yaxis: { title: 'FGA', ...PLOTLY_DARK.yaxis } }, { responsive: true });
        }
    }

    document.getElementById('sc-player').onchange = draw;
    document.getElementById('sc-filter').onchange = draw;
    draw();
}

// ---------------------------------------------------------------------------
// Page: Heatmap
// ---------------------------------------------------------------------------

async function renderHeatmap() {
    const data = await loadCSV('all_players_grid_heatmap');
    const players = getPlayers(data);
    populateSelect('hm-player', players, 'Stephen Curry');

    function draw() {
        const player = document.getElementById('hm-player').value;
        const pData = data.filter(r => r.PLAYER === player && toNum(r.FGA) >= 3);

        const traces = [
            {
                x: pData.map(r => toNum(r.grid_x)),
                y: pData.map(r => toNum(r.grid_y)),
                mode: 'markers',
                marker: {
                    size: pData.map(r => Math.min(toNum(r.FGA), 50) * 0.8 + 4),
                    color: pData.map(r => toNum(r.FG_PCT)),
                    colorscale: 'RdYlGn', cmin: 0.2, cmax: 0.7,
                    colorbar: { title: 'FG%' },
                    opacity: 0.75,
                    line: { width: 0.5, color: 'gray' },
                },
                text: pData.map(r => `FG%: ${(toNum(r.FG_PCT) * 100).toFixed(1)}%<br>FGA: ${r.FGA}<br>FGM: ${r.FGM}`),
                hoverinfo: 'text',
                showlegend: false,
            },
            threePointArc(),
        ];

        Plotly.newPlot('hm-chart', traces, {
            ...PLOTLY_DARK, ...courtLayout(),
            height: 600, title: `${player} — Efficiency Heatmap`,
        }, { responsive: true });
    }

    document.getElementById('hm-player').onchange = draw;
    draw();
}

// ---------------------------------------------------------------------------
// Page: Player Comparison
// ---------------------------------------------------------------------------

async function renderComparison() {
    const shots = await loadCSV('master_shot_chart');
    const zones = await loadCSV('all_players_zone_stats');
    const players = getPlayers(shots);

    populateSelect('cmp-p1', players, 'Stephen Curry');
    populateSelect('cmp-p2', players, 'LeBron James');

    function draw() {
        const p1 = document.getElementById('cmp-p1').value;
        const p2 = document.getElementById('cmp-p2').value;

        const d1 = shots.filter(r => r.PLAYER_NAME_LABEL === p1);
        const d2 = shots.filter(r => r.PLAYER_NAME_LABEL === p2);

        // Side by side
        const traces = [
            { x: d1.map(r => toNum(r.LOC_X)), y: d1.map(r => toNum(r.LOC_Y)), mode: 'markers', marker: { size: 3, color: d1.map(r => r.RESULT === 'Made' ? '#2ecc71' : '#e74c3c'), opacity: 0.5 }, showlegend: false, hoverinfo: 'skip', xaxis: 'x', yaxis: 'y' },
            { x: d2.map(r => toNum(r.LOC_X)), y: d2.map(r => toNum(r.LOC_Y)), mode: 'markers', marker: { size: 3, color: d2.map(r => r.RESULT === 'Made' ? '#2ecc71' : '#e74c3c'), opacity: 0.5 }, showlegend: false, hoverinfo: 'skip', xaxis: 'x2', yaxis: 'y2' },
        ];

        const layout = {
            ...PLOTLY_DARK,
            height: 450,
            grid: { rows: 1, columns: 2, pattern: 'independent' },
            annotations: [
                { text: p1, xref: 'x domain', yref: 'y domain', x: 0.5, y: 1.08, showarrow: false, font: { size: 16, color: '#58a6ff' } },
                { text: p2, xref: 'x2 domain', yref: 'y2 domain', x: 0.5, y: 1.08, showarrow: false, font: { size: 16, color: '#58a6ff' } },
            ],
            xaxis: { range: [-250, 250], showgrid: false, showticklabels: false },
            yaxis: { range: [-50, 420], showgrid: false, showticklabels: false, scaleanchor: 'x' },
            xaxis2: { range: [-250, 250], showgrid: false, showticklabels: false },
            yaxis2: { range: [-50, 420], showgrid: false, showticklabels: false, scaleanchor: 'x2' },
        };

        Plotly.newPlot('cmp-charts', traces, layout, { responsive: true });

        // Stats table
        function pStats(d, name) {
            const made = d.filter(r => r.SHOT_MADE_FLAG === '1').length;
            const threes = d.filter(r => r.SHOT_TYPE === '3PT Field Goal').length;
            const avg = d.length > 0 ? (d.reduce((s, r) => s + (toNum(r.CALC_DISTANCE_FT) || 0), 0) / d.length).toFixed(1) : 'N/A';
            return [name, d.length, d.length > 0 ? (made / d.length * 100).toFixed(1) + '%' : 'N/A', avg + ' ft', threes];
        }
        renderTable('cmp-table', ['Player', 'Shots', 'FG%', 'Avg Dist', '3PT Shots'], [pStats(d1, p1), pStats(d2, p2)]);

        // Zone comparison
        const z1 = zones.filter(r => r.PLAYER === p1);
        const z2 = zones.filter(r => r.PLAYER === p2);
        if (z1.length > 0 && z2.length > 0) {
            const allZones = [...new Set([...z1, ...z2].map(r => r.SHOT_ZONE_BASIC))];
            Plotly.newPlot('cmp-zones', [
                { x: allZones, y: allZones.map(z => { const r = z1.find(x => x.SHOT_ZONE_BASIC === z); return r ? toNum(r.FG_PCT) : 0; }), name: p1, type: 'bar', marker: { color: '#3498db' }, text: allZones.map(z => { const r = z1.find(x => x.SHOT_ZONE_BASIC === z); return r ? (toNum(r.FG_PCT) * 100).toFixed(1) + '%' : ''; }), textposition: 'outside' },
                { x: allZones, y: allZones.map(z => { const r = z2.find(x => x.SHOT_ZONE_BASIC === z); return r ? toNum(r.FG_PCT) : 0; }), name: p2, type: 'bar', marker: { color: '#e74c3c' }, text: allZones.map(z => { const r = z2.find(x => x.SHOT_ZONE_BASIC === z); return r ? (toNum(r.FG_PCT) * 100).toFixed(1) + '%' : ''; }), textposition: 'outside' },
            ], { ...PLOTLY_DARK, barmode: 'group', height: 400, yaxis: { title: 'FG%', ...PLOTLY_DARK.yaxis } }, { responsive: true });
        }
    }

    document.getElementById('cmp-go').onclick = draw;
    draw();
}

// ---------------------------------------------------------------------------
// Page: Game Logs
// ---------------------------------------------------------------------------

async function renderGameLogs() {
    const data = await loadCSV('player_game_logs');
    const players = getPlayers(data);
    populateSelect('gl-player', players, 'Stephen Curry');

    function draw() {
        const player = document.getElementById('gl-player').value;
        const stat = document.getElementById('gl-stat').value;
        const pData = data.filter(r => r.PLAYER_NAME_LABEL === player).sort((a, b) => a.GAME_DATE?.localeCompare(b.GAME_DATE));

        if (pData.length === 0) return;

        const avg = (pData.reduce((s, r) => s + (toNum(r[stat]) || 0), 0) / pData.length).toFixed(1);
        const max = Math.max(...pData.map(r => toNum(r[stat]) || 0)).toFixed(0);
        const wins = pData.filter(r => r.WL === 'W').length;
        const winPct = (wins / pData.length * 100).toFixed(1);

        renderMetrics('gl-metrics', [
            { label: 'Games', value: pData.length.toLocaleString() },
            { label: `Avg ${stat}`, value: avg },
            { label: `Max ${stat}`, value: max },
            { label: 'Win%', value: winPct + '%' },
        ]);

        const traces = [
            { x: pData.map(r => r.GAME_DATE), y: pData.map(r => toNum(r[stat])), mode: 'markers', name: stat, marker: { size: 3, opacity: 0.3, color: '#3498db' } },
        ];

        const rollCol = stat + '_ROLL10';
        if (pData[0][rollCol] !== undefined) {
            traces.push({ x: pData.map(r => r.GAME_DATE), y: pData.map(r => toNum(r[rollCol])), mode: 'lines', name: '10-Game Avg', line: { width: 2.5, color: '#e74c3c' } });
        }

        Plotly.newPlot('gl-chart', traces, {
            ...PLOTLY_DARK, height: 400,
            title: `${player} — ${stat} Over Time`,
            xaxis: { title: 'Date', ...PLOTLY_DARK.xaxis },
            yaxis: { title: stat, ...PLOTLY_DARK.yaxis },
            hovermode: 'x unified',
        }, { responsive: true });

        // Season averages table
        const seasons = {};
        pData.forEach(r => {
            const s = r.SEASON || 'Unknown';
            if (!seasons[s]) seasons[s] = { gp: 0, pts: 0, ast: 0, reb: 0, fg: 0, pm: 0 };
            seasons[s].gp++;
            seasons[s].pts += toNum(r.PTS) || 0;
            seasons[s].ast += toNum(r.AST) || 0;
            seasons[s].reb += toNum(r.REB) || 0;
            seasons[s].fg += toNum(r.FG_PCT) || 0;
            seasons[s].pm += toNum(r.PLUS_MINUS) || 0;
        });

        const rows = Object.entries(seasons).map(([s, v]) => [
            s, v.gp, (v.pts / v.gp).toFixed(1), (v.ast / v.gp).toFixed(1),
            (v.reb / v.gp).toFixed(1), (v.fg / v.gp * 100).toFixed(1) + '%', (v.pm / v.gp).toFixed(1),
        ]);
        renderTable('gl-table', ['Season', 'GP', 'PPG', 'APG', 'RPG', 'FG%', '+/-'], rows);
    }

    document.getElementById('gl-player').onchange = draw;
    document.getElementById('gl-stat').onchange = draw;
    draw();
}

// ---------------------------------------------------------------------------
// Page: Career Stats
// ---------------------------------------------------------------------------

async function renderCareerStats() {
    const data = await loadCSV('player_year_over_year');
    const players = getPlayers(data);
    populateSelect('cs-player', players, 'LeBron James');

    function draw() {
        const player = document.getElementById('cs-player').value;
        const stat = document.getElementById('cs-stat').value;
        const pData = data.filter(r => r.PLAYER_NAME_LABEL === player);

        if (pData.length === 0) return;

        // Trajectory
        Plotly.newPlot('cs-chart', [{
            x: pData.map(r => r.GROUP_VALUE),
            y: pData.map(r => toNum(r[stat])),
            mode: 'lines+markers+text',
            text: pData.map(r => toNum(r[stat])?.toFixed(1)),
            textposition: 'top center',
            textfont: { size: 10, color: '#8b949e' },
            marker: { size: 8, color: '#58a6ff' },
            line: { color: '#58a6ff', width: 2 },
            showlegend: false,
        }], {
            ...PLOTLY_DARK, height: 400,
            title: `${player} — ${stat} by Season`,
            xaxis: { title: 'Season', ...PLOTLY_DARK.xaxis },
            yaxis: { title: stat, ...PLOTLY_DARK.yaxis },
        }, { responsive: true });

        // Table
        const cols = ['GROUP_VALUE', 'GP', 'PTS', 'AST', 'REB', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'STL', 'BLK'];
        const headers = ['Season', 'GP', 'PTS', 'AST', 'REB', 'FG%', '3PT%', 'FT%', 'STL', 'BLK'];
        const rows = pData.map(r => cols.map(c => {
            const v = toNum(r[c]);
            return v !== null ? (c.includes('PCT') ? (v * 100).toFixed(1) + '%' : v.toFixed(1)) : r[c] || '';
        }));
        renderTable('cs-table', headers, rows);

        // Advanced metrics
        const advCols = ['TS_PCT', 'EFG_PCT', 'THREE_RATE', 'AST_TOV'].filter(c => pData[0][c] !== undefined);
        if (advCols.length > 0) {
            const traces = advCols.map(col => ({
                x: pData.map(r => r.GROUP_VALUE),
                y: pData.map(r => toNum(r[col])),
                mode: 'lines+markers',
                name: col.replace(/_/g, ' '),
            }));
            Plotly.newPlot('cs-advanced', traces, {
                ...PLOTLY_DARK, height: 400,
                xaxis: { title: 'Season', ...PLOTLY_DARK.xaxis },
                yaxis: { title: 'Value', ...PLOTLY_DARK.yaxis },
            }, { responsive: true });
        }
    }

    document.getElementById('cs-player').onchange = draw;
    document.getElementById('cs-stat').onchange = draw;
    draw();
}

// ---------------------------------------------------------------------------
// Page: Era Analysis
// ---------------------------------------------------------------------------

async function renderEraAnalysis() {
    const eraTrends = await loadCSV('era_shooting_trends');
    const playerEra = await loadCSV('player_era_breakdown');

    const eraOrder = ['Pre-Three-Point', 'Early 2000s', 'Mid 2000s', 'Early 2010s', 'Three-Point Revolution', 'Modern Era'];
    const sorted = eraOrder.filter(e => eraTrends.some(r => r.ERA === e));

    // FG% by era
    Plotly.newPlot('era-fg', [{
        x: sorted,
        y: sorted.map(e => { const r = eraTrends.find(x => x.ERA === e); return r ? toNum(r.FG_PCT) : 0; }),
        text: sorted.map(e => { const r = eraTrends.find(x => x.ERA === e); return r ? (toNum(r.FG_PCT) * 100).toFixed(1) + '%' : ''; }),
        textposition: 'outside',
        type: 'bar',
        marker: { color: sorted.map((_, i) => `hsl(210, 70%, ${40 + i * 8}%)`) },
    }], { ...PLOTLY_DARK, height: 400, title: 'FG% by Era', yaxis: { title: 'FG%', ...PLOTLY_DARK.yaxis } }, { responsive: true });

    // Distance by era
    Plotly.newPlot('era-dist', [{
        x: sorted,
        y: sorted.map(e => { const r = eraTrends.find(x => x.ERA === e); return r ? toNum(r.AVG_DISTANCE) : 0; }),
        text: sorted.map(e => { const r = eraTrends.find(x => x.ERA === e); return r ? toNum(r.AVG_DISTANCE).toFixed(1) + ' ft' : ''; }),
        textposition: 'outside',
        type: 'bar',
        marker: { color: sorted.map((_, i) => `hsl(25, 80%, ${40 + i * 8}%)`) },
    }], { ...PLOTLY_DARK, height: 400, title: 'Avg Shot Distance by Era', yaxis: { title: 'Distance (ft)', ...PLOTLY_DARK.yaxis } }, { responsive: true });

    // Player era multi-select
    const players = getPlayers(playerEra);
    const sel = document.getElementById('era-players');
    sel.innerHTML = players.map((p, i) => `<option value="${p}"${i < 4 ? ' selected' : ''}>${p}</option>`).join('');

    function drawPlayers() {
        const selected = [...sel.selectedOptions].map(o => o.value);
        const filtered = playerEra.filter(r => selected.includes(r.PLAYER_NAME_LABEL));

        const traces = selected.map(p => {
            const pd = filtered.filter(r => r.PLAYER_NAME_LABEL === p);
            return {
                x: eraOrder.filter(e => pd.some(r => r.ERA === e)),
                y: eraOrder.filter(e => pd.some(r => r.ERA === e)).map(e => toNum(pd.find(r => r.ERA === e)?.FG_PCT)),
                name: p,
                type: 'bar',
            };
        });

        Plotly.newPlot('era-players-chart', traces, {
            ...PLOTLY_DARK, barmode: 'group', height: 450,
            yaxis: { title: 'FG%', ...PLOTLY_DARK.yaxis },
        }, { responsive: true });
    }

    sel.onchange = drawPlayers;
    drawPlayers();
}

// ---------------------------------------------------------------------------
// Page: League Overview
// ---------------------------------------------------------------------------

async function renderLeague() {
    const league = await loadCSV('league_player_stats');
    const teams = await loadCSV('team_stats_by_season');

    const seasons = [...new Set(league.map(r => r.SEASON))].sort().reverse();
    populateSelect('lg-season', seasons, seasons[0]);

    function draw() {
        const season = document.getElementById('lg-season').value;
        const sData = league.filter(r => r.SEASON === season);

        // Top 15
        const top = sData.sort((a, b) => toNum(b.PTS) - toNum(a.PTS)).slice(0, 15);
        renderTable('lg-table',
            ['Player', 'Team', 'GP', 'PTS', 'AST', 'REB', 'FG%', '3PT%'],
            top.map(r => [r.PLAYER_NAME, r.TEAM_ABBREVIATION, r.GP,
                toNum(r.PTS)?.toFixed(1), toNum(r.AST)?.toFixed(1), toNum(r.REB)?.toFixed(1),
                (toNum(r.FG_PCT) * 100).toFixed(1) + '%', (toNum(r.FG3_PCT) * 100).toFixed(1) + '%'
            ])
        );

        // Histogram
        const qualified = sData.filter(r => toNum(r.GP) >= 20);
        Plotly.newPlot('lg-hist', [{
            x: qualified.map(r => toNum(r.PTS)),
            type: 'histogram',
            nbinsx: 30,
            marker: { color: '#58a6ff' },
        }], {
            ...PLOTLY_DARK, height: 350,
            title: `PPG Distribution (min 20 GP) — ${season}`,
            xaxis: { title: 'Points Per Game', ...PLOTLY_DARK.xaxis },
        }, { responsive: true });

        // Team stats
        const tData = teams.filter(r => r.SEASON === season).sort((a, b) => toNum(b.W_PCT) - toNum(a.W_PCT));
        renderTable('lg-teams',
            ['Team', 'W', 'L', 'W%', 'PTS', 'FG%', '3PT%', 'REB', 'AST'],
            tData.map(r => [r.TEAM_NAME, r.W, r.L,
                (toNum(r.W_PCT) * 100).toFixed(1) + '%',
                toNum(r.PTS)?.toFixed(1),
                (toNum(r.FG_PCT) * 100).toFixed(1) + '%',
                (toNum(r.FG3_PCT) * 100).toFixed(1) + '%',
                toNum(r.REB)?.toFixed(1),
                toNum(r.AST)?.toFixed(1),
            ])
        );
    }

    // 3PT evolution (always shown)
    const teamAvg = {};
    teams.forEach(r => {
        if (!teamAvg[r.SEASON]) teamAvg[r.SEASON] = { fg3a: 0, fga: 0, n: 0 };
        teamAvg[r.SEASON].fg3a += toNum(r.FG3A) || 0;
        teamAvg[r.SEASON].fga += toNum(r.FGA) || 0;
        teamAvg[r.SEASON].n++;
    });
    const seasonKeys = Object.keys(teamAvg).sort();
    Plotly.newPlot('lg-three', [{
        x: seasonKeys,
        y: seasonKeys.map(s => (teamAvg[s].fg3a / teamAvg[s].fga * 100).toFixed(1)),
        mode: 'lines+markers+text',
        text: seasonKeys.map(s => (teamAvg[s].fg3a / teamAvg[s].fga * 100).toFixed(1) + '%'),
        textposition: 'top center',
        textfont: { size: 10, color: '#8b949e' },
        marker: { size: 8, color: '#ff6b35' },
        line: { color: '#ff6b35', width: 2 },
        showlegend: false,
    }], {
        ...PLOTLY_DARK, height: 400,
        title: 'Average Team 3-Point Attempt Rate by Season',
        xaxis: { title: 'Season', ...PLOTLY_DARK.xaxis },
        yaxis: { title: '3PA as % of FGA', ...PLOTLY_DARK.yaxis },
    }, { responsive: true });

    document.getElementById('lg-season').onchange = draw;
    draw();
}

// ---------------------------------------------------------------------------
// Page router
// ---------------------------------------------------------------------------

const PAGE_RENDERERS = {
    'shot-chart': renderShotChart,
    'heatmap': renderHeatmap,
    'comparison': renderComparison,
    'game-logs': renderGameLogs,
    'career': renderCareerStats,
    'era': renderEraAnalysis,
    'league': renderLeague,
};

const rendered = new Set();

async function renderCurrentPage(page) {
    if (rendered.has(page)) return;
    const loading = document.getElementById('loading');
    loading.classList.add('visible');
    try {
        await PAGE_RENDERERS[page]();
        rendered.add(page);
    } catch (err) {
        console.error(`Error rendering ${page}:`, err);
    }
    loading.classList.remove('visible');
}

// Initial render
renderCurrentPage('shot-chart');
