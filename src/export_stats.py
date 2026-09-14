"""
Export expanded stats as Tableau-ready CSVs.

Reads raw data collected by collect_stats.py, applies cleaning
transformations, and writes to data/exports/.

Usage:
    python -m src.export_stats
"""

import pandas as pd
from src.data_collection import load_dataframe
from src.data_cleaning import (
    clean_game_logs,
    clean_league_stats,
    clean_year_over_year,
    clean_team_stats,
    export_for_tableau,
)


def export_game_logs():
    print("1. Game logs ...", end=" ", flush=True)
    try:
        df = load_dataframe("all_players_game_logs.csv")
        cleaned = clean_game_logs(df)
        export_for_tableau(cleaned, "player_game_logs.csv")
        print(f"{len(cleaned)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def export_year_over_year():
    print("2. Year-over-year splits ...", end=" ", flush=True)
    try:
        df = load_dataframe("all_players_year_over_year.csv")
        cleaned = clean_year_over_year(df)
        export_for_tableau(cleaned, "player_year_over_year.csv")
        print(f"{len(cleaned)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def export_shooting_splits():
    print("3. Shooting splits ...", end=" ", flush=True)
    try:
        df = load_dataframe("all_players_shooting_splits.csv")
        export_for_tableau(df, "player_shooting_splits.csv")
        print(f"{len(df)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def export_league_stats():
    print("4. League player stats ...", end=" ", flush=True)
    try:
        df = load_dataframe("league_player_stats.csv")
        cleaned = clean_league_stats(df)
        export_for_tableau(cleaned, "league_player_stats.csv")
        print(f"{len(cleaned)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def export_league_leaders():
    print("5. League leaders ...", end=" ", flush=True)
    try:
        df = load_dataframe("league_leaders_pts.csv")
        export_for_tableau(df, "league_leaders_pts.csv")
        print(f"{len(df)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def export_team_stats():
    print("6. Team stats ...", end=" ", flush=True)
    try:
        df = load_dataframe("team_stats_by_season.csv")
        cleaned = clean_team_stats(df)
        export_for_tableau(cleaned, "team_stats_by_season.csv")
        print(f"{len(cleaned)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def export_comparisons():
    print("7. NBA player comparisons ...", end=" ", flush=True)
    try:
        df = load_dataframe("nba_player_comparisons.csv")
        export_for_tableau(df, "nba_player_comparisons.csv")
        print(f"{len(df)} rows")
    except FileNotFoundError:
        print("SKIP (not collected)")


def main():
    print("=" * 60)
    print("Exporting expanded stats for Tableau")
    print("=" * 60)

    export_game_logs()
    export_year_over_year()
    export_shooting_splits()
    export_league_stats()
    export_league_leaders()
    export_team_stats()
    export_comparisons()

    print("\n" + "=" * 60)
    print("All expanded exports complete. Check data/exports/")
    print("=" * 60)


if __name__ == "__main__":
    main()
