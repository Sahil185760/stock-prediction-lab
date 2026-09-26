import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stock_predictor import DEFAULT_DATA, analyze


class ConsoleTests(unittest.TestCase):
    def test_csv_and_json_produce_same_predictions(self):
        data = json.loads(DEFAULT_DATA.read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prices.csv'
            with path.open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=['date', 'close'])
                writer.writeheader()
                writer.writerows(data['observations'])
            self.assertEqual(analyze(path)['rows'], analyze()['rows'])

    def test_runs_outside_project_and_exports_json(self):
        script = Path(__file__).with_name('stock_predictor.py')
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'result.json'
            result = subprocess.run([sys.executable, str(script), '--output', str(output)],
                                    cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Stock Pricing Predictor | NVDA | as of 2025-10-29', result.stdout)
            self.assertTrue(json.loads(output.read_text())['rows'])

    def test_custom_cutoff_rejects_future_prices(self):
        with self.assertRaises(ValueError):
            analyze(as_of='2025-10-28')


if __name__ == '__main__':
    unittest.main()
