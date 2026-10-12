export const ZONES = ['Paint', 'Mid-range', 'Corner 3', 'Above-break 3'];
export const percent = events => events.length ? 100 * events.filter(e => e.made).length / events.length : null;
export function playerEvents(db, playerId) {
  const ids = new Set(db.sessions.filter(s => s.player_id === playerId).map(s => s.id));
  return db.events.filter(e => ids.has(e.session_id));
}
export function zonesFor(events) {
  return ZONES.map(zone => {
    const shots = events.filter(e => e.zone === zone);
    return { zone, attempts: shots.length, accuracy: percent(shots) };
  });
}
export function createPlan(db, playerId, minutes = 30) {
  if (!db.players.some(p => p.id === playerId)) throw new Error('Unknown player');
  if (!Number.isInteger(minutes) || minutes < 15 || minutes > 60) throw new Error('Minutes must be an integer from 15 to 60');
  const zones = zonesFor(playerEvents(db, playerId)).filter(z => z.attempts >= 20);
  if (!zones.length) throw new Error('At least 20 attempts in one zone are required');
  const weakest = [...zones].sort((a, b) => a.accuracy - b.accuracy || a.zone.localeCompare(b.zone))[0];
  const focus = Math.floor(minutes * 0.6);
  const warmup = Math.floor(minutes * 0.2);
  return {
    id: `plan-${playerId}-${minutes}`, player_id: playerId, minutes,
    engine: 'deterministic-rules-v1', focus: weakest.zone,
    explanation: `${weakest.zone} is the lowest-accuracy eligible zone: ${weakest.accuracy.toFixed(1)}% across ${weakest.attempts} attempts. This is a practice heuristic, not an AI assessment.`,
    drills: [{ name: 'Form warm-up', minutes: warmup }, { name: `${weakest.zone} repetitions`, minutes: focus }, { name: 'Mixed-zone review', minutes: minutes - warmup - focus }]
  };
}
// Five simulated route contracts, executed inside the browser. No HTTP backend.
export function mockRequest(db, method, path, body = {}) {
  const url = new URL(path, 'https://mock.local');
  const playerId = url.searchParams.get('player_id');
  const routes = ['/api/players', '/api/sessions', '/api/shot-maps', '/api/ratings', '/api/plans'];
  if (!routes.includes(url.pathname)) return { status: 404, error: 'Route not found' };
  if (method !== (url.pathname === '/api/plans' ? 'POST' : 'GET')) return { status: 405, error: 'Method not allowed' };
  if (url.pathname === '/api/players') return { status: 200, data: db.players };
  const id = url.pathname === '/api/plans' ? body.player_id : playerId;
  if (!id) return { status: 400, error: 'player_id is required' };
  if (!db.players.some(p => p.id === id)) return { status: 404, error: 'Player not found' };
  if (url.pathname === '/api/plans') {
    try { return { status: 201, data: createPlan(db, id, body.minutes) }; }
    catch (error) { return { status: 400, error: error.message }; }
  }
  if (url.pathname === '/api/sessions') return { status: 200, data: db.sessions.filter(s => s.player_id === id) };
  if (url.pathname === '/api/ratings') return { status: 200, data: db.ratings.filter(r => r.player_id === id) };
  const ids = new Set(db.sessions.filter(s => s.player_id === id).map(s => s.id));
  return { status: 200, data: { maps: db.shot_maps.filter(m => ids.has(m.session_id)), events: playerEvents(db, id) } };
}
