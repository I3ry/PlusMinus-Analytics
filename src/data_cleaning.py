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


# ---------------------------------------------------------------------------
# Game log cleaning
# ---------------------------------------------------------------------------

def clean_game_logs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean player game logs for analysis.

    Parses dates, computes game score, adds rolling averages, and
    classifies era.
    """
    df = df.copy()

    # Parse game date
    if "GAME_DATE" in df.columns:
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")
        df["YEAR"] = df["GAME_DATE"].dt.year
        df["MONTH"] = df["GAME_DATE"].dt.month

    # Ensure numeric stat columns
    stat_cols = [
        "PTS", "REB", "AST", "STL", "BLK", "TOV",
        "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
        "FTM", "FTA", "FT_PCT", "MIN", "PLUS_MINUS",
    ]
    for col in stat_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Game Score (John Hollinger formula)
    if all(c in df.columns for c in ["PTS", "FGM", "FGA", "FTM", "FTA",
                                      "REB", "AST", "STL", "BLK", "TOV"]):
        # Approximate OREB/DREB split if not available
        oreb = df.get("OREB", 0)
        dreb = df.get("DREB", 0)
        df["GAME_SCORE"] = (
            df["PTS"]
            + 0.4 * df["FGM"]
            - 0.7 * df["FGA"]
            - 0.4 * (df["FTA"] - df["FTM"])
            + 0.7 * oreb
            + 0.3 * dreb
            + df["STL"]
            + 0.7 * df["AST"]
            + 0.7 * df["BLK"]
            - 0.4 * df.get("PF", 0)
            - df["TOV"]
        ).round(1)

    # Rolling averages (10-game window) per player
    if "PLAYER_NAME_LABEL" in df.columns:
        df = df.sort_values(["PLAYER_NAME_LABEL", "GAME_DATE"])
        for col in ["PTS", "AST", "REB", "GAME_SCORE"]:
            if col in df.columns:
                df[f"{col}_ROLL10"] = (
                    df.groupby("PLAYER_NAME_LABEL")[col]
                    .transform(lambda x: x.rolling(10, min_periods=1).mean())
                    .round(1)
                )

    return df


# ---------------------------------------------------------------------------
# League stats cleaning
# ---------------------------------------------------------------------------

def clean_league_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean league-wide player stats.

    Computes true shooting %, effective FG%, and usage estimate.
    """
    df = df.copy()

    numeric_cols = [
        "GP", "MIN", "PTS", "FGM", "FGA", "FG_PCT",
        "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
        "REB", "AST", "STL", "BLK", "TOV", "PLUS_MINUS",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # True Shooting %
    if all(c in df.columns for c in ["PTS", "FGA", "FTA"]):
        tsa = 2 * (df["FGA"] + 0.44 * df["FTA"])
        df["TS_PCT"] = np.where(tsa > 0, (df["PTS"] / tsa).round(4), np.nan)

    # Effective FG%
    if all(c in df.columns for c in ["FGM", "FG3M", "FGA"]):
        df["EFG_PCT"] = np.where(
            df["FGA"] > 0,
            ((df["FGM"] + 0.5 * df["FG3M"]) / df["FGA"]).round(4),
            np.nan,
        )

    # 3-point attempt rate
    if all(c in df.columns for c in ["FG3A", "FGA"]):
        df["THREE_RATE"] = np.where(
            df["FGA"] > 0,
            (df["FG3A"] / df["FGA"]).round(4),
            np.nan,
        )

    # Assist-to-turnover ratio
    if all(c in df.columns for c in ["AST", "TOV"]):
        df["AST_TOV"] = np.where(
            df["TOV"] > 0,
            (df["AST"] / df["TOV"]).round(2),
            np.nan,
        )

    return df


# ---------------------------------------------------------------------------
# Year-over-year cleaning
# ---------------------------------------------------------------------------

def clean_year_over_year(df: pd.DataFrame) -> pd.DataFrame:
    """Clean year-over-year splits — add advanced efficiency metrics."""
    df = df.copy()
    df = clean_league_stats(df)  # reuse the same efficiency calcs
    return df


# ---------------------------------------------------------------------------
# Team stats cleaning
# ---------------------------------------------------------------------------

def clean_team_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Clean team-level stats and add pace/efficiency context."""
    df = df.copy()

    numeric_cols = [
        "GP", "W", "L", "W_PCT", "MIN", "PTS", "FGM", "FGA",
        "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
        "REB", "AST", "STL", "BLK", "TOV", "PLUS_MINUS",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Offensive rating proxy (points per 100 possessions estimate)
    if all(c in df.columns for c in ["PTS", "FGA", "FTA", "TOV"]):
        poss_est = df["FGA"] + 0.44 * df["FTA"] + df["TOV"]
        df["OFF_RTG_EST"] = np.where(
            poss_est > 0, (df["PTS"] / poss_est * 100).round(1), np.nan
        )

    if all(c in df.columns for c in ["FG3A", "FGA"]):
        df["THREE_RATE"] = np.where(
            df["FGA"] > 0, (df["FG3A"] / df["FGA"]).round(4), np.nan
        )

    return df
