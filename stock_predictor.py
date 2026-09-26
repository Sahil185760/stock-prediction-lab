"""Run Stock Pricing Predictor from a terminal or an IDE's Python console."""
import argparse
import csv
import json
from pathlib import Path

from engine import run

DEFAULT_DATA = Path(__file__).with_name('example.json')


def load_data(path, as_of=None, symbol=None):
    """Read the bundled JSON format or a CSV with date,close columns."""
    path = Path(path)
    if path.suffix.lower() == '.csv':
        with path.open(newline='', encoding='utf-8-sig') as handle:
            observations = [{'date': row['date'], 'close': float(row['close'])}
                            for row in csv.DictReader(handle)]
        if not observations:
            raise ValueError('CSV contains no observations')
        data = {'observations': observations, 'as_of': as_of or observations[-1]['date'],
                'symbol': symbol or path.stem}
    else:
        data = json.loads(path.read_text())
        if as_of:
            data['as_of'] = as_of
        if symbol:
            data['symbol'] = symbol
    return data


def analyze(path=DEFAULT_DATA, as_of=None, symbol=None):
    """Return results for interactive use: result = analyze('prices.csv')."""
    data = load_data(path, as_of, symbol)
    result = run(data)
    result['symbol'] = data.get('symbol', 'Stock')
    result['dataset_label'] = data.get('dataset_label', str(path))
    return result


def print_report(result, rows=10):
    print(f"Stock Pricing Predictor | {result['symbol']} | as of {result['details']['historical_as_of']}")
    print(result['dataset_label'])
    print()
    for label, value in result['metrics'].items():
        print(f'{label:32} {value:10.3%}')
    print(f"{'Estimated next closing price':32} {result['details']['estimated_next_close']:10.2f}")
    print(f"Training rows: {result['details']['training_rows_final']} | Evaluated sessions: {result['details']['test_rows']}")
    if rows:
        print('\nDate          Actual return   Predicted return')
        for row in result['rows'][-rows:]:
            print(f"{row['date']}    {row['actual_return']:10.3%}         {row['predicted_return']:10.3%}")
    print('\nModel estimates; no transaction costs or trading-profit calculation.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path, default=DEFAULT_DATA,
                        help='JSON dataset or CSV with date,close columns')
    parser.add_argument('--as-of', help='ISO date cutoff; later observations are rejected')
    parser.add_argument('--symbol', help='Display label; does not download data')
    parser.add_argument('--rows', type=int, default=10, help='Recent evaluation rows to print')
    parser.add_argument('--output', type=Path, help='Save complete results as JSON')
    args = parser.parse_args(argv)
    if args.rows < 0:
        parser.error('--rows must be zero or greater')
    if args.output and args.output.resolve() == args.input.resolve():
        parser.error('--output must differ from the input file')
    try:
        result = analyze(args.input, args.as_of, args.symbol)
        print_report(result, args.rows)
        if args.output:
            args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
            print(f'\nSaved: {args.output}')
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        parser.exit(2, f'Stock Pricing Predictor: {exc}\n')


if __name__ == '__main__':
    main()
