"""
Expanded stats collection script for NBA Player Efficiency Analysis.

Pulls game logs, advanced metrics, league-wide stats, shooting splits,
and team data beyond the base shot charts already collected.

Usage:
    python -m src.collect_stats
"""

import time
import pandas as pd

from src.data_collection import (
    find_player,
    get_player_game_logs_multi,
    get_player_year_over_year,
    get_player_shooting_splits,
    get_player_estimated_metrics,
    get_league_player_stats,
    get_league_leaders,
    get_league_bio_stats,
    get_team_stats,
    get_player_comparison,
    save_dataframe,
    season_range,
)

# Same player set as batch_collect.py
PLAYERS = {
    "Michael Jordan": {"seasons": (1996, 2002), "recent": "2001-02"},
    "Kobe Bryant":    {"seasons": (1996, 2015), "recent": "2015-16"},
    "Allen Iverson":  {"seasons": (1996, 2009), "recent": "2009-10"},
    "Dirk Nowitzki":  {"seasons": (1998, 2018), "recent": "2018-19"},
    "LeBron James":   {"seasons": (2003, 2024), "recent": "2024-25"},
    "Stephen Curry":  {"seasons": (2009, 2024), "recent": "2024-25"},
    "Kevin Durant":   {"seasons": (2007, 2024), "recent": "2024-25"},
    "James Harden":   {"seasons": (2009, 2024), "recent": "2024-25"},
    "Luka Doncic":    {"seasons": (2018, 2024), "recent": "2024-25"},
    "Nikola Jokic":   {"seasons": (2015, 2024), "recent": "2024-25"},
}

# Key seasons to pull league-wide data for (spanning eras)
LEAGUE_SEASONS = [
    "1996-97", "1999-00", "2003-04", "2006-07",
    "2009-10", "2012-13", "2015-16", "2018-19",
    "2021-22", "2023-24", "2024-25",
]


def _safe(name: str) -> str:
    return (
        name.replace(" ", "_").lower()
        .replace("č", "c").replace("ć", "c")
    )


def collect_game_logs():
    """Pull game-by-game logs for all players across their careers."""
    print("\n" + "=" * 60)
    print("Collecting player game logs")
    print("=" * 60)

    all_logs = []
    for name, info in PLAYERS.items():
        player = find_player(name)
        if not player:
            print(f"  {name}: NOT FOUND, skipping")
            continue

        pid = player["id"]
        safe = _safe(player["full_name"])
        start, end = info["seasons"]
        seasons = season_range(start, end)

        print(f"  {player['full_name']}: {len(seasons)} seasons ...", end=" ", flush=True)
        logs = get_player_game_logs_multi(pid, seasons)

        if not logs.empty:
            logs["PLAYER_NAME_LABEL"] = player["full_name"]
            save_dataframe(logs, f"{safe}_game_logs.csv")
            all_logs.append(logs)
            print(f"{len(logs)} games")
        else:
            print("0 games")

    if all_logs:
        combined = pd.concat(all_logs, ignore_index=True)
        save_dataframe(combined, "all_players_game_logs.csv")
        print(f"\nCombined game logs: {len(combined)} rows")
    return combined if all_logs else pd.DataFrame()


def collect_year_over_year():
    """Pull year-over-year dashboard stats for each player."""
    print("\n" + "=" * 60)
    print("Collecting year-over-year splits")
    print("=" * 60)

    all_yoy = []
    for name, info in PLAYERS.items():
        player = find_player(name)
        if not player:
            continue

        safe = _safe(player["full_name"])
        print(f"  {player['full_name']} ...", end=" ", flush=True)
        try:
            yoy = get_player_year_over_year(player["id"])
            if not yoy.empty:
                yoy["PLAYER_NAME_LABEL"] = player["full_name"]
                save_dataframe(yoy, f"{safe}_year_over_year.csv")
                all_yoy.append(yoy)
                print(f"{len(yoy)} season rows")
            else:
                print("empty")
        except Exception as e:
            print(f"ERROR: {e}")

    if all_yoy:
        combined = pd.concat(all_yoy, ignore_index=True)
        save_dataframe(combined, "all_players_year_over_year.csv")
        print(f"\nCombined YoY: {len(combined)} rows")
    return combined if all_yoy else pd.DataFrame()


def collect_shooting_splits():
    """Pull shooting splits (by distance) for active players' recent seasons."""
    print("\n" + "=" * 60)
    print("Collecting shooting splits")
    print("=" * 60)

    all_splits = []
    for name, info in PLAYERS.items():
        player = find_player(name)
        if not player:
            continue

        safe = _safe(player["full_name"])
        season = info["recent"]
        print(f"  {player['full_name']} ({season}) ...", end=" ", flush=True)
        try:
            splits = get_player_shooting_splits(player["id"], season=season)
            if not splits.empty:
                splits["PLAYER_NAME_LABEL"] = player["full_name"]
                splits["SEASON"] = season
                save_dataframe(splits, f"{safe}_shooting_splits.csv")
                all_splits.append(splits)
                print(f"{len(splits)} rows")
            else:
                print("empty")
        except Exception as e:
            print(f"ERROR: {e}")

    if all_splits:
        combined = pd.concat(all_splits, ignore_index=True)
        save_dataframe(combined, "all_players_shooting_splits.csv")
        print(f"\nCombined splits: {len(combined)} rows")
    return combined if all_splits else pd.DataFrame()


def collect_league_stats():
    """Pull league-wide player stats and leaders across key seasons."""
    print("\n" + "=" * 60)
    print("Collecting league-wide stats")
    print("=" * 60)

    # --- League player stats (per game) ---
    all_league = []
    for season in LEAGUE_SEASONS:
        print(f"  League stats {season} ...", end=" ", flush=True)
        try:
            df = get_league_player_stats(season, per_mode="PerGame")
            if not df.empty:
                df["SEASON"] = season
                all_league.append(df)
                print(f"{len(df)} players")
            else:
                print("empty")
        except Exception as e:
            print(f"ERROR: {e}")

    if all_league:
        combined = pd.concat(all_league, ignore_index=True)
        save_dataframe(combined, "league_player_stats.csv")
        print(f"  Combined league stats: {len(combined)} rows")

    # --- League leaders (points) across eras ---
    all_leaders = []
    for season in LEAGUE_SEASONS:
        print(f"  League leaders {season} ...", end=" ", flush=True)
        try:
            df = get_league_leaders(season, stat_category="PTS")
            if not df.empty:
                df["SEASON"] = season
                all_leaders.append(df)
                print(f"{len(df)} players")
            else:
                print("empty")
        except Exception as e:
            print(f"ERROR: {e}")

    if all_leaders:
        combined = pd.concat(all_leaders, ignore_index=True)
        save_dataframe(combined, "league_leaders_pts.csv")
        print(f"  Combined leaders: {len(combined)} rows")

    return (
        pd.concat(all_league, ignore_index=True) if all_league else pd.DataFrame(),
        pd.concat(all_leaders, ignore_index=True) if all_leaders else pd.DataFrame(),
    )


def collect_team_stats():
    """Pull team-level stats for key seasons."""
    print("\n" + "=" * 60)
    print("Collecting team stats")
    print("=" * 60)

    all_teams = []
    for season in LEAGUE_SEASONS:
        print(f"  Team stats {season} ...", end=" ", flush=True)
        try:
            df = get_team_stats(season, per_mode="PerGame")
            if not df.empty:
                df["SEASON"] = season
                all_teams.append(df)
                print(f"{len(df)} teams")
            else:
                print("empty")
        except Exception as e:
            print(f"ERROR: {e}")

    if all_teams:
        combined = pd.concat(all_teams, ignore_index=True)
        save_dataframe(combined, "team_stats_by_season.csv")
        print(f"\nCombined team stats: {len(combined)} rows")
    return combined if all_teams else pd.DataFrame()


def collect_player_comparisons():
    """Pull head-to-head comparisons via the NBA PlayerCompare endpoint."""
    print("\n" + "=" * 60)
    print("Collecting player comparisons (NBA endpoint)")
    print("=" * 60)

    pairs = [
        ("LeBron James", "Stephen Curry", "2024-25"),
        ("Kevin Durant", "James Harden", "2024-25"),
        ("Luka Doncic", "Nikola Jokic", "2024-25"),
    ]

    all_comparisons = []
    for p1_name, p2_name, season in pairs:
        p1 = find_player(p1_name)
        p2 = find_player(p2_name)
        if not p1 or not p2:
            print(f"  {p1_name} vs {p2_name}: player not found, skipping")
            continue

        print(f"  {p1['full_name']} vs {p2['full_name']} ({season}) ...", end=" ", flush=True)
        try:
            result = get_player_comparison(p1["id"], p2["id"], season=season)
            overall = result["overall"]
            if not overall.empty:
                overall["COMPARISON"] = f"{p1['full_name']} vs {p2['full_name']}"
                all_comparisons.append(overall)
                print("OK")
            else:
                print("empty")
        except Exception as e:
            print(f"ERROR: {e}")

    if all_comparisons:
        combined = pd.concat(all_comparisons, ignore_index=True)
        save_dataframe(combined, "nba_player_comparisons.csv")
        print(f"\nCombined comparisons: {len(combined)} rows")
    return combined if all_comparisons else pd.DataFrame()


def main():
    print("NBA Player Efficiency Analysis — Expanded Stats Collection")
    print("=" * 60)

    collect_game_logs()
    collect_year_over_year()
    collect_shooting_splits()
    collect_league_stats()
    collect_team_stats()
    collect_player_comparisons()

    print("\n" + "=" * 60)
    print("Expanded stats collection complete.")
    print("Raw data saved to data/raw/")
    print("=" * 60)


if __name__ == "__main__":
    main()
