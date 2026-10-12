import unittest
from pathlib import Path
import pandas as pd
from src.data_cleaning import clean_shot_chart

class EraTests(unittest.TestCase):
    def fixture(self, **columns):
        n = len(next(iter(columns.values())))
        return pd.DataFrame({'LOC_X': [0]*n, 'LOC_Y': [10]*n, 'SHOT_MADE_FLAG': [1]*n, **columns})

    def test_explicit_season_precedes_game_date(self):
        result = clean_shot_chart(self.fixture(SEASON_ID=['22023', '22019'], GAME_DATE=['19960101', '20200810']))
        self.assertEqual(result.ERA.tolist(), ['Modern Era', 'Three-Point Revolution'])

    def test_dates_and_bad_dates(self):
        result = clean_shot_chart(self.fixture(GAME_DATE=['20000115', '20200810', '20201225', 'bad'], HTM=['BOS']*4))
        self.assertEqual(result.ERA.tolist(), ['Mid 1990s', 'Three-Point Revolution', 'Modern Era', 'Unknown'])

    def test_integer_dates_and_mixed_seasons(self):
        result = clean_shot_chart(self.fixture(SEASON=['2014-15', None, '2023'], GAME_DATE=[20150501, 20060101, 20240101]))
        self.assertEqual(result.ERA.tolist(), ['Early 2010s', 'Mid 2000s', 'Modern Era'])

    def test_export_eras_are_supported_by_both_frontends(self):
        root = Path(__file__).resolve().parents[1]
        eras = pd.read_csv(root / 'public/data/era_shooting_trends.csv').ERA
        for filename in ['public/app.js', 'app.py']:
            source = (root / filename).read_text(encoding='utf-8')
            for era in eras:
                self.assertIn(era, source)

if __name__ == '__main__':
    unittest.main()
