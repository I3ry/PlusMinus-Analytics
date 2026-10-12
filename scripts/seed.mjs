import { writeFileSync } from 'node:fs';
import { createPlan, percent, zonesFor } from '../public/prototype/model.mjs';
let seed = 42;
const random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
const db = { players: [], sessions: [], shot_maps: [], events: [], coaches: [{ id: 'c1', name: 'Morgan Lee', team: 'Demo development squad' }], ratings: [], plans: [] };
['Alex Rivera', 'Jordan Ellis', 'Sam Parker'].forEach((name, pi) => {
  const id = `p${pi + 1}`;
  db.players.push({ id, coach_id: 'c1', name, position: ['Guard', 'Wing', 'Forward'][pi] });
  for (let si = 0; si < 8; si++) {
    const sid = `${id}-s${si + 1}`;
    db.sessions.push({ id: sid, player_id: id, date: `2026-09-${String(2 + si * 3).padStart(2, '0')}`, minutes: 25 + si * 2 + pi });
    db.shot_maps.push({ id: `map-${sid}`, session_id: sid, coordinate_system: 'feet-relative-to-hoop', source: 'synthetic-seed-42' });
    for (let n = 0; n < 60; n++) {
      const zi = n % 4;
      const zone = ['Paint', 'Mid-range', 'Corner 3', 'Above-break 3'][zi];
      const angle = 0.35 + random() * 2.44;
      const radius = zi === 0 ? 2 + random() * 5 : zi === 1 ? 10 + random() * 8 : 24;
      const x = zi === 2 ? (n % 8 === 2 ? -22 : 22) : radius * Math.cos(angle);
      const y = zi === 2 ? random() * 5 : radius * Math.sin(angle);
      db.events.push({ id: `${sid}-e${n}`, session_id: sid, shot_map_id: `map-${sid}`, zone, x: +x.toFixed(2), y: +y.toFixed(2), made: random() < [0.68, 0.42, 0.38, 0.30][zi] + pi * 0.045 + si * 0.008 });
    }
    const events = db.events.filter(e => e.session_id === sid);
    db.ratings.push({ id: `rating-${sid}`, player_id: id, session_id: sid, score: +percent(events).toFixed(1), method: '100 * makes / attempts; descriptive shooting index, not validated skill' });
  }
  db.plans.push(createPlan(db, id, 30));
});
writeFileSync(new URL('../public/prototype/db.json', import.meta.url), JSON.stringify(db, null, 2) + '\n');
console.log(Object.fromEntries(Object.entries(db).map(([key, value]) => [key, value.length])));
