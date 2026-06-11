from engine.data import (
    load_ticker,
    get_spot_price,
    get_expirations
)


def run_analysis(symbol, max_dte):

    ticker = load_ticker(symbol)

    spot = get_spot_price(ticker)

    expirations = get_expirations(ticker)

    return {
        "symbol": symbol,
        "spot": float(spot),
        "max_dte": max_dte,
        "num_expirations": len(expirations),
    }
