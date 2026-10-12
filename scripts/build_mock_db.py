"""Materialize and validate the seven-entity fixture in an inspectable SQLite file."""
import json
import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
db = json.loads((root / 'public/prototype/db.json').read_text(encoding='utf-8'))
connection = sqlite3.connect(':memory:')
connection.executescript((root / 'docs/recruiter/schema.sql').read_text(encoding='utf-8'))
for name in ['coaches', 'players', 'sessions', 'shot_maps', 'events', 'ratings', 'plans']:
    rows = db[name]
    columns = list(rows[0])
    values = [[json.dumps(row[c]) if isinstance(row[c], (dict, list)) else row[c] for c in columns] for row in rows]
    connection.executemany(f"INSERT INTO {name} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", values)
connection.commit()
assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
with sqlite3.connect(root / 'docs/recruiter/mock.sqlite') as output:
    connection.backup(output)
print('SQLite: seven tables populated; integrity_check=ok; foreign_key_check=0 violations')
