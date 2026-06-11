# engine/analysis.py

import yfinance as yf


def run_analysis(symbol, max_dte):

    ticker = yf.Ticker(symbol)

    spot = ticker.history(period="1d")["Close"].iloc[-1]

    return {
        "symbol": symbol,
        "spot": float(spot),
        "max_dte": max_dte
    }
