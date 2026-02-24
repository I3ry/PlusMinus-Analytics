"""
Data collection module for NBA Player Efficiency Analysis.

Uses nba_api to pull shot chart data, player stats, and team information.
Includes rate limiting to respect API constraints.
"""

import os
import time
import json
from pathlib import Path

import pandas as pd
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import (
    shotchartdetail,
    playercareerstats,
    commonplayerinfo,
)

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
REQUEST_DELAY = 0.6  # seconds between API calls


def _ensure_dirs():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _delay():
    time.sleep(REQUEST_DELAY)


# ---------------------------------------------------------------------------
# Player lookup
# ---------------------------------------------------------------------------

def find_player(name: str) -> dict | None:
    """Search for a player by full or partial name. Returns the first match."""
    matches = players.find_players_by_full_name(name)
    if not matches:
        matches = players.find_players_by_last_name(name)
    return matches[0] if matches else None


def find_players_by_name(name: str) -> list[dict]:
    """Return all players matching a full or partial name."""
    results = players.find_players_by_full_name(name)
    if not results:
        results = players.find_players_by_last_name(name)
    return results


def get_all_players(only_active: bool = False) -> list[dict]:
    """Return every player in the nba_api static list."""
    all_p = players.get_players()
    if only_active:
        all_p = [p for p in all_p if p["is_active"]]
    return all_p


# ---------------------------------------------------------------------------
# Team lookup
# ---------------------------------------------------------------------------

def find_team(name: str) -> dict | None:
    """Search for a team by full name, city, or abbreviation."""
    matches = teams.find_teams_by_full_name(name)
    if not matches:
        matches = teams.find_teams_by_city(name)
    if not matches:
        matches = teams.find_teams_by_abbreviation(name)
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# Shot chart data
# ---------------------------------------------------------------------------

def get_shot_chart(
    player_id: int,
    season: str | None = None,
    season_type: str = "Regular Season",
    team_id: int = 0,
) -> pd.DataFrame:
    """
    Pull shot chart detail for a player.

    Parameters
    ----------
    player_id : int
        NBA player ID.
    season : str or None
        Season string like '2023-24'. None returns all available data.
    season_type : str
        'Regular Season' or 'Playoffs'.
    team_id : int
        Filter by team. 0 = all teams.

    Returns
    -------
    pd.DataFrame with columns including LOC_X, LOC_Y, SHOT_MADE_FLAG, etc.
    """
    params = dict(
        player_id=player_id,
        team_id=team_id,
        season_type_all_star=season_type,
        context_measure_simple="FGA",
    )
    if season:
        params["season_nullable"] = season

    _delay()
    response = shotchartdetail.ShotChartDetail(**params)
    df = response.get_data_frames()[0]
    return df


def get_shot_charts_multi_season(
    player_id: int,
    seasons: list[str],
    season_type: str = "Regular Season",
) -> pd.DataFrame:
    """Pull shot charts across multiple seasons and concatenate."""
    frames = []
    for season in seasons:
        df = get_shot_chart(player_id, season=season, season_type=season_type)
        if not df.empty:
            frames.append(df)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Career / season stats
# ---------------------------------------------------------------------------

def get_career_stats(player_id: int) -> pd.DataFrame:
    """Return per-season regular-season stats for a player."""
    _delay()
    response = playercareerstats.PlayerCareerStats(player_id=player_id)
    return response.get_data_frames()[0]


def get_player_info(player_id: int) -> pd.DataFrame:
    """Return biographical / draft info for a player."""
    _delay()
    response = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    return response.get_data_frames()[0]


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def save_dataframe(df: pd.DataFrame, filename: str, subdir: str = "raw") -> Path:
    """Save a DataFrame as CSV under data/<subdir>/."""
    target_dir = Path(__file__).resolve().parent.parent / "data" / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename
    df.to_csv(path, index=False)
    return path


def load_dataframe(filename: str, subdir: str = "raw") -> pd.DataFrame:
    """Load a CSV from data/<subdir>/ into a DataFrame."""
    path = Path(__file__).resolve().parent.parent / "data" / subdir / filename
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Convenience: collect & save for a player
# ---------------------------------------------------------------------------

def collect_player_data(
    player_name: str,
    seasons: list[str] | None = None,
    save: bool = True,
) -> dict[str, pd.DataFrame]:
    """
    End-to-end collection for a single player.

    Returns a dict with keys 'info', 'career_stats', and 'shot_chart'.
    Optionally saves each as CSV to data/raw/.
    """
    player = find_player(player_name)
    if player is None:
        raise ValueError(f"Player not found: {player_name}")

    pid = player["id"]
    safe_name = player["full_name"].replace(" ", "_").lower()

    info = get_player_info(pid)
    career = get_career_stats(pid)

    if seasons:
        shots = get_shot_charts_multi_season(pid, seasons)
    else:
        shots = get_shot_chart(pid)

    result = {"info": info, "career_stats": career, "shot_chart": shots}

    if save:
        _ensure_dirs()
        save_dataframe(info, f"{safe_name}_info.csv")
        save_dataframe(career, f"{safe_name}_career_stats.csv")
        save_dataframe(shots, f"{safe_name}_shot_chart.csv")

    return result


# ---------------------------------------------------------------------------
# Season string helpers
# ---------------------------------------------------------------------------

def make_season_string(start_year: int) -> str:
    """Convert a start year (e.g. 2023) to NBA season format '2023-24'."""
    end = (start_year + 1) % 100
    return f"{start_year}-{end:02d}"


def season_range(start_year: int, end_year: int) -> list[str]:
    """Generate a list of season strings from start_year to end_year (inclusive)."""
    return [make_season_string(y) for y in range(start_year, end_year + 1)]
