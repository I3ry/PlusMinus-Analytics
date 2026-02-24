"""
Quick verification script to confirm nba_api is installed and the
NBA stats endpoint is reachable.

Usage:
    python -m src.verify_connection
"""

import sys


def main():
    print("1/4  Importing nba_api …")
    try:
        from nba_api.stats.static import players, teams
    except ImportError:
        sys.exit("FAIL: nba_api is not installed. Run: pip install nba_api")

    print("2/4  Looking up a player (LeBron James) …")
    results = players.find_players_by_full_name("LeBron James")
    if not results:
        sys.exit("FAIL: Player lookup returned no results.")
    player = results[0]
    print(f"     Found: {player['full_name']} (ID: {player['id']})")

    print("3/4  Looking up a team (Los Angeles Lakers) …")
    team_results = teams.find_teams_by_full_name("Los Angeles Lakers")
    if not team_results:
        sys.exit("FAIL: Team lookup returned no results.")
    team = team_results[0]
    print(f"     Found: {team['full_name']} (ID: {team['id']})")

    print("4/4  Pulling a small shot chart from the API …")
    from nba_api.stats.endpoints import shotchartdetail
    import time

    time.sleep(0.6)
    response = shotchartdetail.ShotChartDetail(
        player_id=player["id"],
        team_id=0,
        season_nullable="2023-24",
        season_type_all_star="Regular Season",
        context_measure_simple="FGA",
    )
    df = response.get_data_frames()[0]
    print(f"     Retrieved {len(df)} shot records for 2023-24.")

    print("\nAll checks passed. Environment is ready.")


if __name__ == "__main__":
    main()
