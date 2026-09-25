# SignalLab — Stock return prediction lab

Predict next-session stock returns with a ridge-regression model. An expanding-window evaluation compares it with a zero-return baseline. Each prediction is trained only on earlier observations; feature scaling is fitted inside each training window.

## Project history

The original project was completed in programming club in **November 2025**.

## Run locally

Requires Python 3.9 or later. No external packages, API keys, or network access are needed.

```sh
python3 app.py
```

Open http://127.0.0.1:8000. For a second project running at the same time, use `python3 app.py --port 8001`. The server binds only to your computer.

1. Click **Run analysis** to evaluate the historical dataset.
2. Edit the JSON input or load your own JSON file.
3. Inspect metrics, the results table and model notes.
4. Export the complete result as JSON.

## Historical dataset and cutoff

The bundled example contains **228 NVDA daily closes from January 2 to November 28, 2025**, with `as_of` set to November 28, 2025. This cutoff was selected during reconstruction to fit the owner's November 2025 project date. No observation after the cutoff is included or accepted. The next-session estimate is not labeled with an invented past publication date.

Source: [Yahoo Finance NVDA historical prices](https://finance.yahoo.com/quote/NVDA/history/), retrieved via its public chart endpoint. The exact request URL, retrieval date, price-field choice and file fingerprint are in `DATA_PROVENANCE.json`. The closing-price field is used rather than the dividend-adjusted close. Current providers can revise historical records or apply split adjustments; this is not an archived 2025 data vintage.

## Input contract

`as_of`: an ISO date. `observations`: 80–1,500 rows with ISO `date` and positive finite `close`, strictly ascending with unique dates. Rows after `as_of` are rejected. `symbol` and `dataset_label` identify the series; they do not trigger online downloads. Use one symbol and a consistent price convention.

## Method and limits

The model uses previous return, trailing five-return average and trailing five-return volatility. Each target is the next single-session return. The final 30% of eligible rows are evaluated, with at least 40 preceding training rows. Every prediction refits a ridge model (fixed penalty 2) and its standardization using only earlier rows. Future test prices cannot influence earlier estimates.

Metrics include mean absolute error, a zero-return baseline, and directional accuracy. Exact predictions and dates are exportable. Zero returns are grouped with non-positive returns for directional accuracy. The next-close output is a point estimate without a calibrated prediction interval. No transaction costs, execution, dividends or trading profits are modeled. Results are educational, not investment recommendations; the model can perform worse than the baseline.

The local server accepts JSON up to 1 MB and does not persist imported data. `engine.py` implements the temporal contract and expanding-window evaluation; `models.py` implements standardized ridge regression using a pivoted linear solve. Tests cover future-data isolation, cutoff enforcement, invalid prices and numerical behavior.

## Verify

```sh
python3 -m unittest -v
```

## API

`POST /api/run` accepts the same JSON as the editor and returns `metrics`, `series`, `rows`, and `details`. Errors return HTTP 400 with an `error` message. This is a local educational server, not an Internet-facing production service.

## Historical availability of the method

Ridge regression was published by Hoerl and Kennard in 1970 ([original paper](https://doi.org/10.1080/00401706.1970.10488634)). This reconstruction fits coefficients from the supplied historical data; it does not use a pretrained modern foundation model. The implementation uses only Python 3.9 standard-library functionality.
