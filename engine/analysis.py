from engine.data import (
    load_ticker,
    get_spot_price,
    get_expirations,
    download_option_chain
)

def run_analysis(symbol, max_dte):

    ticker = load_ticker(symbol)

    spot = get_spot_price(ticker)

    expirations = get_expirations(ticker)
    
    first_expiration = expirations[0]

    chain = download_option_chain(
        ticker,
        first_expiration
    )
    

    return {
        "symbol": symbol,
        "spot": float(spot),
        "max_dte": max_dte,
        "num_expirations": len(expirations),
        "first_expiration": first_expiration,
        "calls": len(chain.calls),
        "puts": len(chain.puts),
    }
