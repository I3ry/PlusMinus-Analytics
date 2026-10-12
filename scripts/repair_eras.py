"""Repair committed exports offline, preserving all non-era fields and row order."""
import csv
import json
from collections import defaultdict
from pathlib import Path
import pandas as pd
from src.data_cleaning import clean_shot_chart

root = Path(__file__).resolve().parents[1]
summary = {}
for folder in [root / 'data/exports', root / 'public/data']:
    for path in folder.glob('*.csv'):
        with path.open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            if not fields or not {'ERA', 'GAME_DATE', 'LOC_X', 'LOC_Y', 'SHOT_MADE_FLAG'}.issubset(fields):
                continue
            rows = list(reader)
        cleaned = clean_shot_chart(pd.DataFrame(rows))
        for row, era in zip(rows, cleaned['ERA']):
            row['ERA'] = era
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    master = pd.read_csv(folder / 'master_shot_chart.csv')
    for keys, filename in [(['ERA'], 'era_shooting_trends.csv'), (['PLAYER_NAME_LABEL', 'ERA'], 'player_era_breakdown.csv')]:
        result = master.groupby(keys).agg(FGA=('SHOT_MADE_FLAG', 'count'), FGM=('SHOT_MADE_FLAG', 'sum'), AVG_DISTANCE=('CALC_DISTANCE_FT', 'mean')).reset_index()
        result['FG_PCT'] = (result['FGM'] / result['FGA']).round(4)
        result.to_csv(folder / filename, index=False)
    summary[str(folder.relative_to(root))] = {'shots': len(master), 'players': master.PLAYER_NAME_LABEL.nunique(), 'first_game': str(master.GAME_DATE.min()), 'last_game': str(master.GAME_DATE.max()), 'eras': sorted(master.ERA.unique().tolist())}
print(json.dumps(summary, indent=2))
