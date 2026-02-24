"""
Batch data collection script for NBA Player Efficiency Analysis.

Pulls shot chart data and career stats for representative players
across multiple NBA eras. Includes rate limiting and progress reporting.

Usage:
    python -m src.batch_collect
"""

import sys
import time
from pathlib import Path

import pandas as pd

from src.data_collection import (
    find_player,
    get_shot_chart,
    get_shot_charts_multi_season,
    get_career_stats,
    get_player_info,
    save_dataframe,
    season_range,
    make_season_string,
)

# Players and their active season ranges (shot chart data from 1996-97 onward)
PLAYERS = {
    "Michael Jordan": (1996, 2002),    # Last stint with Bulls + Wizards
    "Kobe Bryant": (1996, 2015),       # Full career (shot data era)
    "Allen Iverson": (1996, 2009),     # Sixers through late career
    "Dirk Nowitzki": (1998, 2018),     # Full Mavs career
    "LeBron James": (2003, 2024),      # Full career to date
    "Stephen Curry": (2009, 2024),     # Full career to date
    "Kevin Durant": (2007, 2024),      # Full career to date
    "James Harden": (2009, 2024),      # Full career to date
    "Luka Doncic": (2018, 2024),       # Full career to date
    "Nikola Jokic": (2015, 2024),      # Full career to date
}


def collect_all(players: dict | None = None):
    """
    Collect shot chart and career data for all configured players.

    Parameters
    ----------
    players : dict or None
        Override the default PLAYERS dict. Keys are player names,
        values are (start_year, end_year) tuples.
    """
    if players is None:
        players = PLAYERS

    all_shots = []
    all_careers = []

    total = len(players)
    for i, (name, (start, end)) in enumerate(players.items(), 1):
        print(f"\n[{i}/{total}] Collecting data for {name} ({start}-{end}) ...")

        player = find_player(name)
        if player is None:
            print(f"  WARNING: Player '{name}' not found, skipping.")
            continue

        pid = player["id"]
        safe_name = player["full_name"].replace(" ", "_").lower()
        # Handle special characters in names
        safe_name = safe_name.replace("č", "c").replace("ć", "c")

        # --- Player info ---
        try:
            info = get_player_info(pid)
            save_dataframe(info, f"{safe_name}_info.csv")
            print(f"  Saved player info.")
        except Exception as e:
            print(f"  WARNING: Could not get player info: {e}")

        # --- Career stats ---
        try:
            career = get_career_stats(pid)
            save_dataframe(career, f"{safe_name}_career_stats.csv")
            career["PLAYER_NAME"] = player["full_name"]
            all_careers.append(career)
            print(f"  Saved career stats ({len(career)} seasons).")
        except Exception as e:
            print(f"  WARNING: Could not get career stats: {e}")

        # --- Shot chart ---
        # Try a single call first (works for active players); if empty,
        # fall back to pulling season-by-season (needed for retired players).
        try:
            print(f"  Pulling shot chart ...")
            shots = get_shot_chart(pid)
            if shots.empty:
                seasons = season_range(start, end)
                print(f"  Single-call returned 0 rows; pulling {len(seasons)} seasons individually ...")
                shots = get_shot_charts_multi_season(pid, seasons)
            if not shots.empty:
                save_dataframe(shots, f"{safe_name}_shot_chart.csv")
                shots["PLAYER_NAME_LABEL"] = player["full_name"]
                all_shots.append(shots)
                print(f"  Saved shot chart ({len(shots)} shots).")
            else:
                print(f"  No shot chart data returned.")
        except Exception as e:
            print(f"  WARNING: Could not get shot chart: {e}")

    # --- Save combined datasets ---
    if all_shots:
        combined_shots = pd.concat(all_shots, ignore_index=True)
        save_dataframe(combined_shots, "all_players_shots.csv")
        print(f"\nCombined shot chart: {len(combined_shots)} total shots saved.")

    if all_careers:
        combined_careers = pd.concat(all_careers, ignore_index=True)
        save_dataframe(combined_careers, "all_players_career_stats.csv")
        print(f"Combined career stats: {len(combined_careers)} season rows saved.")

    print("\nData collection complete.")
    return combined_shots if all_shots else pd.DataFrame()


if __name__ == "__main__":
    collect_all()
