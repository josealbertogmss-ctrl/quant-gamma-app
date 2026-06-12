import os

import pandas as pd
import yfinance as yf


def load_ticker(symbol):

    return yf.Ticker(symbol)


def get_spot_price(ticker):

    return float(
        ticker.history(
            period="1d"
        )["Close"].iloc[-1]
    )


def get_expirations(ticker):

    return ticker.options


def download_option_chain(
    ticker,
    expiration
):

    return ticker.option_chain(
        expiration
    )


def save_snapshot(symbol):

    ticker = load_ticker(symbol)

    spot = get_spot_price(
        ticker
    )

    expirations = get_expirations(
        ticker
    )

    all_options = []

    for expiration in expirations:

        try:

            chain = download_option_chain(
                ticker,
                expiration
            )

            calls = chain.calls.copy()
            puts = chain.puts.copy()

            calls["type"] = "call"
            puts["type"] = "put"

            calls["expiration"] = expiration
            puts["expiration"] = expiration

            all_options.append(
                calls
            )

            all_options.append(
                puts
            )

        except Exception:

            continue

    df = pd.concat(
        all_options,
        ignore_index=True
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    filename = (
        f"data/{symbol}_latest.parquet"
    )

    df.to_parquet(
        filename
    )

    return {
        "spot": spot,
        "file": filename
    }


def load_snapshot(symbol):

    filename = (
        f"data/{symbol}_latest.parquet"
    )

    return pd.read_parquet(
        filename
    )
