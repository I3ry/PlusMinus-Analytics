PRAGMA foreign_keys = ON;
CREATE TABLE coaches (id TEXT PRIMARY KEY, name TEXT NOT NULL, team TEXT NOT NULL);
CREATE TABLE players (id TEXT PRIMARY KEY, coach_id TEXT NOT NULL REFERENCES coaches(id), name TEXT NOT NULL, position TEXT NOT NULL);
CREATE TABLE sessions (
  id TEXT PRIMARY KEY, player_id TEXT NOT NULL REFERENCES players(id), date TEXT NOT NULL,
  minutes INTEGER NOT NULL CHECK(minutes > 0), UNIQUE(id, player_id)
);
CREATE TABLE shot_maps (
  id TEXT PRIMARY KEY, session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id),
  coordinate_system TEXT NOT NULL, source TEXT NOT NULL, UNIQUE(id, session_id)
);
CREATE TABLE events (
  id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), shot_map_id TEXT NOT NULL,
  zone TEXT NOT NULL CHECK(zone IN ('Paint','Mid-range','Corner 3','Above-break 3')),
  x REAL NOT NULL, y REAL NOT NULL, made INTEGER NOT NULL CHECK(made IN (0,1)),
  FOREIGN KEY(shot_map_id, session_id) REFERENCES shot_maps(id, session_id)
);
CREATE TABLE ratings (
  id TEXT PRIMARY KEY, player_id TEXT NOT NULL REFERENCES players(id), session_id TEXT NOT NULL UNIQUE,
  score REAL NOT NULL CHECK(score BETWEEN 0 AND 100), method TEXT NOT NULL,
  FOREIGN KEY(session_id, player_id) REFERENCES sessions(id, player_id)
);
CREATE TABLE plans (
  id TEXT PRIMARY KEY, player_id TEXT NOT NULL REFERENCES players(id),
  minutes INTEGER NOT NULL CHECK(minutes BETWEEN 15 AND 60), engine TEXT NOT NULL,
  focus TEXT NOT NULL, explanation TEXT NOT NULL, drills TEXT NOT NULL CHECK(json_valid(drills))
);
