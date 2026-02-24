# PlusMinus Analytics — NBA Player Efficiency Analysis

An interactive dashboard for comparing NBA player shooting efficiency across eras, teams, and court locations using visual heatmaps and statistical analysis.

## Problem

Comparing NBA players across different eras is difficult due to rule changes, pace differences, and evolving play styles. Traditional box-score statistics don't capture spatial shooting patterns.

## Solution

A data pipeline that pulls shot chart data from the NBA API, processes it into analysis-ready formats, and feeds a Tableau dashboard with heatmaps, player comparisons, and era analysis.

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Data Source | `nba_api` (Python) | Shot charts, player stats, team data |
| Processing | Pandas, NumPy | Clean, transform, aggregate |
| Visualization | Tableau | Interactive dashboards, heatmaps |
| Exploration | Jupyter, Matplotlib, Seaborn | Prototyping and validation |

## Project Structure

```
PlusMinus-Analytics/
├── data/
│   ├── raw/            # Raw API responses (git-ignored)
│   ├── cleaned/        # Processed data (git-ignored)
│   └── exports/        # Tableau-ready CSVs
├── src/
│   ├── __init__.py
│   ├── data_collection.py   # NBA API data retrieval
│   ├── data_cleaning.py     # Cleaning & transformation
│   └── verify_connection.py # API connectivity check
├── notebooks/
│   └── 01_exploration.ipynb # Interactive exploration
├── tableau/            # Tableau workbooks
├── docs/               # Documentation
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick Start

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the API connection**:
   ```bash
   python -m src.verify_connection
   ```

4. **Explore in Jupyter**:
   ```bash
   jupyter notebook notebooks/01_exploration.ipynb
   ```

## Usage

### Collect data for a player

```python
from src.data_collection import collect_player_data, season_range

data = collect_player_data("Stephen Curry", seasons=season_range(2015, 2023))
# Saves CSVs to data/raw/ automatically
```

### Clean and export for Tableau

```python
from src.data_cleaning import clean_shot_chart, aggregate_by_grid, export_for_tableau

cleaned = clean_shot_chart(data["shot_chart"])
grid = aggregate_by_grid(cleaned, bin_size=25)
export_for_tableau(grid, "curry_grid.csv")
```

### Compare two players

```python
from src.data_cleaning import prepare_comparison, export_for_tableau

combined = prepare_comparison(cleaned_player1, cleaned_player2, "Curry", "Jordan")
export_for_tableau(combined, "curry_vs_jordan.csv")
```

## Key Data Fields

| Field | Description |
|---|---|
| `LOC_X`, `LOC_Y` | Shot coordinates (tenths of feet from basket) |
| `SHOT_MADE_FLAG` | 1 = made, 0 = missed |
| `SHOT_ZONE_BASIC` | Court region (Restricted Area, Mid-Range, etc.) |
| `SHOT_ZONE_AREA` | Left / Center / Right positioning |
| `SHOT_DISTANCE` | Distance from basket in feet |
| `GAME_DATE` | Date of game (for era analysis) |

## Data Availability

Shot chart data is available from the 1996-97 season onward via the NBA API.

## Rate Limiting

The data collection module includes a 0.6-second delay between API calls to respect NBA.com rate limits. Data is cached locally as CSV files to avoid redundant requests.
