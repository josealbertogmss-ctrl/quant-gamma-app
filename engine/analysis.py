from engine.data import (
    load_ticker,
    get_spot_price,
    get_expirations,
    download_option_chain
)

from engine.calculations import (
    calc_gamma_vectorized
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

    calls_oi = int(
        chain.calls["openInterest"].fillna(0).sum()
    )

    puts_oi = int(
        chain.puts["openInterest"].fillna(0).sum()
    )

    sample_strike = chain.calls.iloc[0]["strike"]

    sample_iv = chain.calls.iloc[0]["impliedVolatility"]

    gamma = calc_gamma_vectorized(
        spot,
        sample_strike,
        sample_iv,
        30/365
    )
    
    return {
        "symbol": symbol,
        "spot": float(spot),
        "max_dte": max_dte,
        "num_expirations": len(expirations),
        "first_expiration": first_expiration,
        "num_calls": len(chain.calls),
        "num_puts": len(chain.puts),
        "calls_oi": calls_oi,
        "puts_oi": puts_oi,
        "sample_gamma": float(gamma),
    }
