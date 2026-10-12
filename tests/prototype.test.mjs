import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createPlan, mockRequest, percent, playerEvents, zonesFor } from '../public/prototype/model.mjs';
const db = JSON.parse(readFileSync(new URL('../public/prototype/db.json', import.meta.url)));
test('seven collections have unique keys and valid foreign keys', () => {
  assert.equal(Object.keys(db).length, 7);
  for (const rows of Object.values(db)) assert.equal(new Set(rows.map(r => r.id)).size, rows.length);
  const exists = (key, id) => db[key].some(r => r.id === id);
  for (const p of db.players) assert.ok(exists('coaches', p.coach_id));
  for (const s of db.sessions) assert.ok(exists('players', s.player_id));
  for (const m of db.shot_maps) assert.ok(exists('sessions', m.session_id));
  for (const e of db.events) {
    assert.ok(exists('sessions', e.session_id));
    assert.equal(db.shot_maps.find(m => m.id === e.shot_map_id)?.session_id, e.session_id);
    assert.equal(typeof e.made, 'boolean');
  }
  for (const r of db.ratings) assert.equal(db.sessions.find(s => s.id === r.session_id)?.player_id, r.player_id);
  for (const p of db.plans) assert.ok(exists('players', p.player_id));
});
test('metrics reconcile to shot events; empty denominators stay unknown', () => {
  assert.equal(percent([]), null);
  assert.equal(percent([{ made: true }, { made: false }]), 50);
  assert.equal(db.events.length, 1440);
  for (const p of db.players) {
    const events = playerEvents(db, p.id);
    assert.equal(events.length, 480);
    assert.equal(zonesFor(events).reduce((sum, z) => sum + z.attempts, 0), events.length);
  }
  for (const r of db.ratings) assert.equal(r.score, +percent(db.events.filter(e => e.session_id === r.session_id)).toFixed(1));
});
test('plans focus on weakest eligible zone and preserve requested duration', () => {
  for (const p of db.players) for (const minutes of [15, 30, 45, 60]) {
    const plan = createPlan(db, p.id, minutes);
    const weakest = Math.min(...zonesFor(playerEvents(db, p.id)).map(z => z.accuracy));
    assert.equal(zonesFor(playerEvents(db, p.id)).find(z => z.zone === plan.focus).accuracy, weakest);
    assert.equal(plan.drills.reduce((sum, d) => sum + d.minutes, 0), minutes);
  }
  assert.throws(() => createPlan(db, 'p1', 0));
  assert.throws(() => createPlan({ ...db, events: [] }, 'p1', 30));
});
test('all five route contracts and error cases', () => {
  assert.equal(mockRequest(db, 'GET', '/api/players').data.length, 3);
  assert.equal(mockRequest(db, 'GET', '/api/sessions?player_id=p1').data.length, 8);
  assert.equal(mockRequest(db, 'GET', '/api/shot-maps?player_id=p2').data.events.length, 480);
  assert.equal(mockRequest(db, 'GET', '/api/ratings?player_id=p3').data.length, 8);
  assert.equal(mockRequest(db, 'POST', '/api/plans', { player_id: 'p1', minutes: 30 }).status, 201);
  assert.equal(mockRequest(db, 'GET', '/api/sessions').status, 400);
  assert.equal(mockRequest(db, 'GET', '/api/sessions?player_id=missing').status, 404);
  assert.equal(mockRequest(db, 'DELETE', '/api/players').status, 405);
  assert.equal(mockRequest(db, 'GET', '/api/missing').status, 404);
  assert.equal(mockRequest(db, 'POST', '/api/plans', { player_id: 'p1', minutes: '30' }).status, 400);
});
