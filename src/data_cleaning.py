"""
Data cleaning and transformation module for NBA Player Efficiency Analysis.

Processes raw shot chart and stats data into analysis-ready formats
optimized for Tableau visualization.
"""

from pathlib import Path

import numpy as np
import pandas as pd

EXPORTS_DIR = Path(__file__).resolve().parent.parent / "data" / "exports"
CLEANED_DIR = Path(__file__).resolve().parent.parent / "data" / "cleaned"

# Court dimensions (in tenths of feet, matching nba_api coordinate system)
COURT_HALF_WIDTH = 250   # -250 to 250 (50 ft total)
COURT_LENGTH = 470       # 0 to ~470 (47 ft from baseline to half-court)


# ---------------------------------------------------------------------------
# Era classification
# ---------------------------------------------------------------------------

ERA_BINS = {
    "Pre-Three-Point": (1996, 1999),
    "Early 2000s": (2000, 2004),
    "Mid 2000s": (2005, 2009),
    "Early 2010s": (2010, 2014),
    "Three-Point Revolution": (2015, 2019),
    "Modern Era": (2020, 2030),
}


def classify_era(season_str: str) -> str:
    """
    Classify a season string (e.g. '2004-05') into an era label.
    """
    try:
        year = int(season_str[:4])
    except (ValueError, TypeError):
        return "Unknown"
    for era, (start, end) in ERA_BINS.items():
        if start <= year <= end:
            return era
    return "Unknown"


# ---------------------------------------------------------------------------
# Shot chart cleaning
# ---------------------------------------------------------------------------

def clean_shot_chart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and enrich a raw shot chart DataFrame.

    Steps:
    - Drop rows missing critical coordinate or result data.
    - Normalize coordinate columns to numeric types.
    - Add era classification.
    - Add shot distance in feet (from tenths-of-feet coordinates).
    - Add a human-readable result column.
    """
    df = df.copy()

    # Drop rows missing essential fields
    required = ["LOC_X", "LOC_Y", "SHOT_MADE_FLAG"]
    df = df.dropna(subset=[c for c in required if c in df.columns])

    # Ensure numeric types
    for col in ["LOC_X", "LOC_Y", "SHOT_DISTANCE", "SHOT_MADE_FLAG"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Classify era
    if "GAME_DATE" in df.columns:
        df["SEASON_START_YEAR"] = df["GAME_DATE"].astype(str).str[:4].astype(int)
    if "SEASON_START_YEAR" in df.columns:
        # Approximate season string from year; not perfect but functional
        df["ERA"] = df.get("SEASON_ID", df.get("HTM", pd.Series(dtype=str)))
    # If we have a proper season column, use it
    for candidate in ["SEASON_ID", "SEASON"]:
        if candidate in df.columns:
            # SEASON_ID often looks like "22023" — strip leading digit
            raw = df[candidate].astype(str)
            if raw.str.len().max() > 5:
                raw = raw.str[1:]  # e.g. "22023" -> "2023"
            # Build proper season string
            df["SEASON_STR"] = raw.str[:4] + "-" + (
                (raw.str[:4].astype(int) + 1) % 100
            ).astype(str).str.zfill(2)
            df["ERA"] = df["SEASON_STR"].apply(classify_era)
            break

    # Human-readable result
    if "SHOT_MADE_FLAG" in df.columns:
        df["RESULT"] = df["SHOT_MADE_FLAG"].map({1: "Made", 0: "Missed"})

    # Computed distance from coordinates (feet)
    if "LOC_X" in df.columns and "LOC_Y" in df.columns:
        df["CALC_DISTANCE_FT"] = np.sqrt(df["LOC_X"] ** 2 + df["LOC_Y"] ** 2) / 10.0

    return df


# ---------------------------------------------------------------------------
# Zone aggregation (for heatmaps)
# ---------------------------------------------------------------------------

def aggregate_by_zone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate shooting stats by SHOT_ZONE_BASIC and SHOT_ZONE_AREA.

    Returns a DataFrame with attempts, makes, and FG% per zone.
    """
    if "SHOT_ZONE_BASIC" not in df.columns:
        raise ValueError("DataFrame missing SHOT_ZONE_BASIC column")

    group_cols = ["SHOT_ZONE_BASIC", "SHOT_ZONE_AREA"]
    group_cols = [c for c in group_cols if c in df.columns]

    agg = (
        df.groupby(group_cols)
        .agg(
            FGA=("SHOT_MADE_FLAG", "count"),
            FGM=("SHOT_MADE_FLAG", "sum"),
        )
        .reset_index()
    )
    agg["FG_PCT"] = (agg["FGM"] / agg["FGA"]).round(4)
    return agg


def aggregate_by_grid(
    df: pd.DataFrame, bin_size: int = 20
) -> pd.DataFrame:
    """
    Bin shots into a grid for heatmap generation.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned shot chart data.
    bin_size : int
        Size of each grid cell in coordinate units (tenths of feet).

    Returns
    -------
    pd.DataFrame with grid_x, grid_y, FGA, FGM, FG_PCT columns.
    """
    df = df.copy()
    df["grid_x"] = (df["LOC_X"] // bin_size) * bin_size + bin_size // 2
    df["grid_y"] = (df["LOC_Y"] // bin_size) * bin_size + bin_size // 2

    agg = (
        df.groupby(["grid_x", "grid_y"])
        .agg(
            FGA=("SHOT_MADE_FLAG", "count"),
            FGM=("SHOT_MADE_FLAG", "sum"),
        )
        .reset_index()
    )
    agg["FG_PCT"] = (agg["FGM"] / agg["FGA"]).round(4)
    return agg


# ---------------------------------------------------------------------------
# Player comparison helpers
# ---------------------------------------------------------------------------

def prepare_comparison(
    df1: pd.DataFrame, df2: pd.DataFrame,
    player1_name: str, player2_name: str,
) -> pd.DataFrame:
    """
    Combine two cleaned shot chart DataFrames with a PLAYER column for
    side-by-side Tableau comparison.
    """
    d1 = df1.copy()
    d2 = df2.copy()
    d1["PLAYER"] = player1_name
    d2["PLAYER"] = player2_name
    return pd.concat([d1, d2], ignore_index=True)


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_for_tableau(df: pd.DataFrame, filename: str) -> Path:
    """Save a DataFrame as CSV to data/exports/ for Tableau import."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / filename
    df.to_csv(path, index=False)
    return path


def export_cleaned(df: pd.DataFrame, filename: str) -> Path:
    """Save a cleaned DataFrame to data/cleaned/."""
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    path = CLEANED_DIR / filename
    df.to_csv(path, index=False)
    return path
