# Stock Pricing Predictor: stock return predictor

A Python console program for estimating next-session returns with ridge regression and evaluating predictions against a zero-return baseline.

## Run in a terminal or IDE

Requires Python 3.9 or later. Uses only the standard library.

```sh
python3 stock_predictor.py
python3 stock_predictor.py --rows 20 --output results.json
python3 stock_predictor.py prices.csv --symbol NVDA --as-of 2025-08-29
```

In an IDE, open the project folder and run `stock_predictor.py`. Results print in the run console. The bundled dataset is located relative to the script, so it works from another working directory too.

For an interactive Python console:

```python
from stock_predictor import analyze, print_report

result = analyze()
print_report(result)
result['details']['estimated_next_close']
```

## Data

The bundled `example.json` contains **165 NVDA daily closing prices from January 2 through August 29, 2025**, with an **August 29, 2025 cutoff**. No September or later observations are included. Source: [Yahoo Finance historical prices](https://finance.yahoo.com/quote/NVDA/history/). `DATA_PROVENANCE.json` records the source request, retrieval time, price field and dataset checksum. Prices use `quote.close`, not dividend-adjusted close; historical provider records can be revised.

Supply a JSON file in the same format or a CSV with `date,close` columns. Inputs require 80–1,500 positive finite closing prices, ordered by unique ISO dates. Data after the cutoff is rejected. `--symbol` is a label, not a download request. Use a consistent price convention throughout a dataset.

## Method and output

Features are the previous daily return, trailing five-return mean and trailing five-return volatility. The final 30% of eligible rows are evaluated with an expanding training window. Every prediction refits the model and its standardization using earlier observations only. Ridge penalty is fixed at 2.

The console reports mean absolute error, baseline error, directional accuracy, next-session estimated return and estimated next close. Optional JSON output includes every held-out prediction and model coefficients. The forecast is a point estimate without a calibrated uncertainty interval. No transaction costs, execution or trading profits are modeled; the model may perform worse than its baseline.

## Files

- `stock_predictor.py`: console entry point, CSV/JSON loading and reporting.
- `engine.py`: time-ordered features, validation and evaluation.
- `models.py`: standardized ridge regression using a pivoted linear solve.
- `example.json`: offline historical dataset.

## Verify

```sh
python3 -m unittest -v
```
