"""
Test fixture and validation for the Curry vs. LeBron court-location comparison.

This test demonstrates the data cleaning and aggregation logic without
requiring live NBA API data, so the pipeline can be validated offline.
"""

import pandas as pd
import numpy as np
from src.data_cleaning import (
    clean_shot_chart,
    aggregate_by_zone,
    aggregate_by_grid,
    prepare_comparison,
)


def create_synthetic_shot_chart(
    player_name: str,
    n_shots: int = 200,
    zone_bias: str = "perimeter",
    accuracy: float = 0.45,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic shot chart for testing.

    Parameters
    ----------
    player_name : str
        Player name to include in the data.
    n_shots : int
        Number of shot records to generate.
    zone_bias : str
        'perimeter' favors 3-point range; 'paint' favors restricted area.
    accuracy : float
        Overall FG%.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Synthetic shot chart with realistic-looking coordinate and zone data.
    """
    np.random.seed(seed)

    # Generate coordinates based on bias
    if zone_bias == "perimeter":
        # Perimeter bias: more distance from basket, spread left/right
        locs = np.random.normal(loc=0, scale=200, size=(n_shots, 2))
        locs[:, 1] = np.abs(locs[:, 1]) + 150  # Push away from basket
    else:
        # Paint bias: close to basket
        locs = np.random.normal(loc=0, scale=50, size=(n_shots, 2))
        locs[:, 1] = np.abs(locs[:, 1])

    loc_x, loc_y = locs[:, 0], locs[:, 1]

    # Ensure coordinates stay within court bounds (roughly)
    loc_x = np.clip(loc_x, -250, 250)
    loc_y = np.clip(loc_y, 0, 470)

    # Assign shot zones based on coordinates
    shot_distance = np.sqrt(loc_x**2 + loc_y**2) / 10.0
    shot_zone_basic = pd.cut(
        shot_distance,
        bins=[0, 8, 16, 240],
        labels=["Restricted Area", "Mid-Range", "3-Point"],
    )

    shot_zone_area = pd.cut(
        loc_x,
        bins=[-250, -80, 80, 250],
        labels=["Left", "Center", "Right"],
    )

    # Generate shot results based on accuracy and zone
    made_flags = np.random.binomial(1, accuracy, n_shots)

    df = pd.DataFrame(
        {
            "LOC_X": loc_x,
            "LOC_Y": loc_y,
            "SHOT_MADE_FLAG": made_flags,
            "SHOT_ZONE_BASIC": shot_zone_basic,
            "SHOT_ZONE_AREA": shot_zone_area,
            "SHOT_DISTANCE": shot_distance,
            "GAME_DATE": pd.date_range("2023-01-01", periods=n_shots, freq="D").astype(str),
            "SEASON_ID": ["22023"] * n_shots,  # Mock season ID
            "PLAYER_NAME": player_name,
        }
    )

    return df


def test_zone_aggregation():
    """
    Test that zone aggregation correctly computes FG% by zone.
    """
    print("\n=== Test: Zone Aggregation ===")

    # Create synthetic data: perimeter shooter with 40% accuracy
    curry_raw = create_synthetic_shot_chart(
        "Stephen Curry", n_shots=300, zone_bias="perimeter", accuracy=0.40, seed=1
    )
    curry_clean = clean_shot_chart(curry_raw)

    # Aggregate by zone
    curry_by_zone = aggregate_by_zone(curry_clean)

    print(f"Curry: {len(curry_clean)} total shots")
    print(f"Zones identified: {len(curry_by_zone)}")
    print("\nCurry's shooting by zone:")
    print(curry_by_zone.to_string(index=False))

    # Validation checks
    total_fga = curry_by_zone["FGA"].sum()
    total_fgm = curry_by_zone["FGM"].sum()
    overall_fg_pct = (total_fgm / total_fga) if total_fga > 0 else 0

    print(f"\nOverall FG%: {overall_fg_pct:.1%}")
    assert total_fga == len(curry_clean), "FGA sum doesn't match shot count"
    print("✓ Zone aggregation is consistent")


def test_grid_aggregation():
    """
    Test that grid binning for heatmaps produces expected structure.
    """
    print("\n=== Test: Grid Aggregation ===")

    # Create synthetic data: paint-focused player with higher accuracy
    lebron_raw = create_synthetic_shot_chart(
        "LeBron James", n_shots=250, zone_bias="paint", accuracy=0.50, seed=2
    )
    lebron_clean = clean_shot_chart(lebron_raw)

    # Aggregate into grid
    lebron_grid = aggregate_by_grid(lebron_clean, bin_size=20)

    print(f"LeBron: {len(lebron_clean)} total shots")
    print(f"Grid cells occupied: {len(lebron_grid)}")
    print("\nGrid sample (first 10 cells):")
    print(lebron_grid.head(10).to_string(index=False))

    # Validation checks
    grid_total_fga = lebron_grid["FGA"].sum()
    assert grid_total_fga == len(lebron_clean), "Grid FGA sum doesn't match shot count"
    print(f"\n✓ Grid aggregation is consistent; all {len(lebron_clean)} shots accounted for")


def test_player_comparison():
    """
    Test that prepare_comparison correctly merges two players' data.
    """
    print("\n=== Test: Player Comparison ===")

    # Generate two distinct players
    curry_raw = create_synthetic_shot_chart(
        "Stephen Curry", n_shots=200, zone_bias="perimeter", accuracy=0.42, seed=10
    )
    curry_clean = clean_shot_chart(curry_raw)

    lebron_raw = create_synthetic_shot_chart(
        "LeBron James", n_shots=220, zone_bias="paint", accuracy=0.52, seed=20
    )
    lebron_clean = clean_shot_chart(lebron_raw)

    # Prepare comparison
    combined = prepare_comparison(curry_clean, lebron_clean, "Curry", "LeBron")

    print(f"Curry shots: {len(curry_clean)}")
    print(f"LeBron shots: {len(lebron_clean)}")
    print(f"Combined: {len(combined)}")

    # Check that both players are represented
    player_counts = combined["PLAYER"].value_counts()
    print(f"\nPlayer distribution:\n{player_counts}")

    assert "Curry" in player_counts.index and len(curry_clean) == player_counts["Curry"]
    assert "LeBron" in player_counts.index and len(lebron_clean) == player_counts["LeBron"]
    print("\n✓ Player comparison structure is correct")

    # Show court-location comparison example
    if "SHOT_ZONE_BASIC" in combined.columns:
        print("\nShot volume by zone and player:")
        zone_pivot = combined.groupby(["PLAYER", "SHOT_ZONE_BASIC"])["SHOT_MADE_FLAG"].agg(
            ["count", "sum"]
        )
        zone_pivot.columns = ["FGA", "FGM"]
        zone_pivot["FG%"] = (zone_pivot["FGM"] / zone_pivot["FGA"]).round(3)
        print(zone_pivot)


if __name__ == "__main__":
    print("=" * 70)
    print("NBA Player Comparison Pipeline — Test Fixture")
    print("=" * 70)

    try:
        test_zone_aggregation()
        test_grid_aggregation()
        test_player_comparison()

        print("\n" + "=" * 70)
        print("All tests passed ✓")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
