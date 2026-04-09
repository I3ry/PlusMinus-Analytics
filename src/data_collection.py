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
    playergamelog,
    playerestimatedmetrics,
    playerdashboardbyyearoveryear,
    playerdashboardbyshootingsplits,
    leaguedashplayerstats,
    leagueleaders,
    leaguedashplayerbiostats,
    leaguedashteamstats,
    teamgamelog,
    playercompare,
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
# Game logs (game-by-game stats)
# ---------------------------------------------------------------------------

def get_player_game_log(
    player_id: int, season: str, season_type: str = "Regular Season"
) -> pd.DataFrame:
    """Return game-by-game stats for a player in a given season."""
    _delay()
    response = playergamelog.PlayerGameLog(
        player_id=player_id, season=season, season_type_all_star=season_type
    )
    return response.get_data_frames()[0]


def get_player_game_logs_multi(
    player_id: int, seasons: list[str], season_type: str = "Regular Season"
) -> pd.DataFrame:
    """Pull game logs across multiple seasons and concatenate."""
    frames = []
    for season in seasons:
        try:
            df = get_player_game_log(player_id, season, season_type)
            if not df.empty:
                df["SEASON"] = season
                frames.append(df)
        except Exception:
            continue
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Advanced / estimated metrics
# ---------------------------------------------------------------------------

def get_player_estimated_metrics(
    player_id: int, season: str
) -> pd.DataFrame:
    """
    Return estimated advanced metrics for a player-season.

    Includes offensive/defensive rating, net rating, usage, pace, etc.
    """
    _delay()
    response = playerestimatedmetrics.PlayerEstimatedMetrics(season=season)
    df = response.get_data_frames()[0]
    return df[df["PLAYER_ID"] == player_id]


def get_player_year_over_year(player_id: int) -> pd.DataFrame:
    """Return year-over-year dashboard splits for a player."""
    _delay()
    response = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(
        player_id=player_id
    )
    return response.get_data_frames()[1]  # ByYearPlayerDashboard


def get_player_shooting_splits(
    player_id: int, season: str = "2024-25"
) -> pd.DataFrame:
    """Return shooting splits by distance, area, and assisted/unassisted."""
    _delay()
    response = playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits(
        player_id=player_id, season=season
    )
    # Index 1 = ByDistancePlayerDashboard
    return response.get_data_frames()[1]


# ---------------------------------------------------------------------------
# League-wide stats
# ---------------------------------------------------------------------------

def get_league_player_stats(
    season: str, season_type: str = "Regular Season",
    per_mode: str = "PerGame",
) -> pd.DataFrame:
    """
    Return league-wide player stats for a season.

    per_mode: 'Totals', 'PerGame', 'Per36', 'Per48'.
    """
    _delay()
    response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star=season_type,
        per_mode_detailed=per_mode,
    )
    return response.get_data_frames()[0]


def get_league_leaders(
    season: str, stat_category: str = "PTS",
    per_mode: str = "PerGame",
) -> pd.DataFrame:
    """
    Return league leaders for a stat category.

    stat_category: 'PTS', 'REB', 'AST', 'STL', 'BLK', 'EFF', 'FG_PCT', etc.
    """
    _delay()
    response = leagueleaders.LeagueLeaders(
        season=season,
        stat_category_abbreviation=stat_category,
        per_mode48=per_mode,
    )
    return response.get_data_frames()[0]


def get_league_bio_stats(season: str) -> pd.DataFrame:
    """Return player bio stats (height, weight, age, draft, country)."""
    _delay()
    response = leaguedashplayerbiostats.LeagueDashPlayerBioStats(season=season)
    return response.get_data_frames()[0]


# ---------------------------------------------------------------------------
# Team stats
# ---------------------------------------------------------------------------

def get_team_stats(
    season: str, season_type: str = "Regular Season",
    per_mode: str = "PerGame",
) -> pd.DataFrame:
    """Return team-level stats for a season."""
    _delay()
    response = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        season_type_all_star=season_type,
        per_mode_detailed=per_mode,
    )
    return response.get_data_frames()[0]


def get_team_game_log(
    team_id: int, season: str, season_type: str = "Regular Season"
) -> pd.DataFrame:
    """Return game-by-game results for a team in a given season."""
    _delay()
    response = teamgamelog.TeamGameLog(
        team_id=team_id, season=season, season_type_all_star=season_type
    )
    return response.get_data_frames()[0]


# ---------------------------------------------------------------------------
# Head-to-head player comparison (NBA's own comparison endpoint)
# ---------------------------------------------------------------------------

def get_player_comparison(
    player1_id: int, player2_id: int, season: str = "2024-25"
) -> dict[str, pd.DataFrame]:
    """
    Use the NBA's PlayerCompare endpoint to get head-to-head stats.

    Returns dict with 'individual' and 'overall' DataFrames.
    """
    _delay()
    response = playercompare.PlayerCompare(
        player_id_list=str(player1_id),
        vs_player_id_list=str(player2_id),
        season=season,
    )
    frames = response.get_data_frames()
    return {
        "overall": frames[0],   # OverallCompare
        "individual": frames[1] if len(frames) > 1 else pd.DataFrame(),
    }


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
