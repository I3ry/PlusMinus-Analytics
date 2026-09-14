"""
Batch data cleaning and export script for NBA Player Efficiency Analysis.

Reads raw shot chart and career data, applies cleaning/transformation,
generates aggregations, and exports Tableau-ready CSVs.

Usage:
    python -m src.batch_clean
"""

import pandas as pd
import numpy as np
from pathlib import Path

from src.data_collection import load_dataframe, save_dataframe
from src.data_cleaning import (
    clean_shot_chart,
    classify_era,
    aggregate_by_zone,
    aggregate_by_grid,
    prepare_comparison,
    export_for_tableau,
    export_cleaned,
)


def _safe_name(name: str) -> str:
    return (
        name.replace(" ", "_")
        .lower()
        .replace("č", "c")
        .replace("ć", "c")
    )


def clean_all_shots():
    """Clean the combined shot chart and export."""
    print("=" * 60)
    print("Phase 3: Data Cleaning & Transformation")
    print("=" * 60)

    # Load combined raw data
    print("\n1. Loading combined shot chart ...")
    raw = load_dataframe("all_players_shots.csv")
    print(f"   Raw rows: {len(raw)}")

    # Clean
    print("2. Cleaning shot chart data ...")
    cleaned = clean_shot_chart(raw)

    # Ensure PLAYER_NAME_LABEL is preserved
    if "PLAYER_NAME_LABEL" not in cleaned.columns and "PLAYER_NAME" in cleaned.columns:
        cleaned["PLAYER_NAME_LABEL"] = cleaned["PLAYER_NAME"]

    # If PLAYER_NAME_LABEL still missing, reconstruct from raw
    if "PLAYER_NAME_LABEL" not in cleaned.columns:
        cleaned["PLAYER_NAME_LABEL"] = raw["PLAYER_NAME_LABEL"]

    print(f"   Cleaned rows: {len(cleaned)}")
    print(f"   Columns: {list(cleaned.columns)}")

    # Save cleaned master dataset
    export_cleaned(cleaned, "all_players_shots_cleaned.csv")
    print("   Saved to data/cleaned/all_players_shots_cleaned.csv")

    return cleaned


def generate_aggregations(cleaned: pd.DataFrame):
    """Generate zone and grid aggregations per player and overall."""
    print("\n3. Generating aggregations ...")

    # --- Per-player zone aggregation ---
    zone_frames = []
    for player_name, group in cleaned.groupby("PLAYER_NAME_LABEL"):
        try:
            zones = aggregate_by_zone(group)
            zones["PLAYER"] = player_name
            zone_frames.append(zones)
        except Exception as e:
            print(f"   WARNING: Zone agg failed for {player_name}: {e}")

    if zone_frames:
        all_zones = pd.concat(zone_frames, ignore_index=True)
        export_for_tableau(all_zones, "all_players_zone_stats.csv")
        print(f"   Zone stats: {len(all_zones)} rows -> data/exports/all_players_zone_stats.csv")

    # --- Per-player grid heatmap data ---
    grid_frames = []
    for player_name, group in cleaned.groupby("PLAYER_NAME_LABEL"):
        grid = aggregate_by_grid(group, bin_size=25)
        grid["PLAYER"] = player_name
        grid_frames.append(grid)

    if grid_frames:
        all_grids = pd.concat(grid_frames, ignore_index=True)
        export_for_tableau(all_grids, "all_players_grid_heatmap.csv")
        print(f"   Grid heatmap: {len(all_grids)} rows -> data/exports/all_players_grid_heatmap.csv")

    # --- Era-level aggregation (overall shooting trends) ---
    if "ERA" in cleaned.columns:
        era_stats = (
            cleaned.groupby("ERA")
            .agg(
                FGA=("SHOT_MADE_FLAG", "count"),
                FGM=("SHOT_MADE_FLAG", "sum"),
                AVG_DISTANCE=("CALC_DISTANCE_FT", "mean"),
            )
            .reset_index()
        )
        era_stats["FG_PCT"] = (era_stats["FGM"] / era_stats["FGA"]).round(4)
        export_for_tableau(era_stats, "era_shooting_trends.csv")
        print(f"   Era trends: {len(era_stats)} rows -> data/exports/era_shooting_trends.csv")

    # --- Per-player + era breakdown ---
    if "ERA" in cleaned.columns:
        player_era = (
            cleaned.groupby(["PLAYER_NAME_LABEL", "ERA"])
            .agg(
                FGA=("SHOT_MADE_FLAG", "count"),
                FGM=("SHOT_MADE_FLAG", "sum"),
                AVG_DISTANCE=("CALC_DISTANCE_FT", "mean"),
            )
            .reset_index()
        )
        player_era["FG_PCT"] = (player_era["FGM"] / player_era["FGA"]).round(4)
        export_for_tableau(player_era, "player_era_breakdown.csv")
        print(f"   Player-era: {len(player_era)} rows -> data/exports/player_era_breakdown.csv")


def build_comparisons(cleaned: pd.DataFrame):
    """Build predefined player comparison datasets for Tableau."""
    print("\n4. Building player comparison datasets ...")

    comparisons = [
        ("Michael Jordan", "Kobe Bryant", "jordan_vs_kobe.csv"),
        ("Stephen Curry", "James Harden", "curry_vs_harden.csv"),
        ("LeBron James", "Kevin Durant", "lebron_vs_durant.csv"),
        ("Luka Dončić", "Stephen Curry", "doncic_vs_curry.csv"),
        ("Michael Jordan", "LeBron James", "jordan_vs_lebron.csv"),
    ]

    for p1, p2, filename in comparisons:
        df1 = cleaned[cleaned["PLAYER_NAME_LABEL"] == p1]
        df2 = cleaned[cleaned["PLAYER_NAME_LABEL"] == p2]

        if df1.empty or df2.empty:
            missing = p1 if df1.empty else p2
            print(f"   SKIP {filename}: no data for {missing}")
            continue

        combined = prepare_comparison(df1, df2, p1, p2)
        export_for_tableau(combined, filename)
        print(f"   {p1} vs {p2}: {len(combined)} shots -> data/exports/{filename}")


def export_master_tableau(cleaned: pd.DataFrame):
    """Export the full cleaned dataset for Tableau."""
    print("\n5. Exporting master Tableau dataset ...")

    # Select the most useful columns for Tableau
    tableau_cols = [
        "PLAYER_NAME_LABEL", "PLAYER_NAME",
        "LOC_X", "LOC_Y", "SHOT_MADE_FLAG", "RESULT",
        "SHOT_ZONE_BASIC", "SHOT_ZONE_AREA", "SHOT_ZONE_RANGE",
        "SHOT_DISTANCE", "CALC_DISTANCE_FT",
        "SHOT_TYPE", "ACTION_TYPE",
        "GAME_DATE", "HTM", "VTM",
    ]
    # Add era columns if present
    for col in ["ERA", "SEASON_STR", "SEASON_ID"]:
        if col in cleaned.columns:
            tableau_cols.append(col)

    # Keep only columns that exist
    available = [c for c in tableau_cols if c in cleaned.columns]
    master = cleaned[available].copy()
    export_for_tableau(master, "master_shot_chart.csv")
    print(f"   Master dataset: {len(master)} rows, {len(available)} columns")
    print(f"   -> data/exports/master_shot_chart.csv")


def export_career_stats():
    """Clean and export the combined career stats for Tableau."""
    print("\n6. Exporting career stats ...")
    try:
        careers = load_dataframe("all_players_career_stats.csv")
        export_for_tableau(careers, "career_stats.csv")
        print(f"   Career stats: {len(careers)} rows -> data/exports/career_stats.csv")
    except FileNotFoundError:
        print("   WARNING: all_players_career_stats.csv not found, skipping.")


def main():
    cleaned = clean_all_shots()
    generate_aggregations(cleaned)
    build_comparisons(cleaned)
    export_master_tableau(cleaned)
    export_career_stats()

    print("\n" + "=" * 60)
    print("All exports complete. Check data/exports/ for Tableau CSVs.")
    print("=" * 60)


if __name__ == "__main__":
    main()
