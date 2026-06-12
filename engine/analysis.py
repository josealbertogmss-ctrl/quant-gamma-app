import pandas as pd

from datetime import datetime

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

    # ============================================================
    # CARGA DEL ACTIVO
    # ============================================================

    ticker = load_ticker(symbol)

    spot = get_spot_price(ticker)

    expirations = get_expirations(ticker)

    # ============================================================
    # DESCARGA DE TODAS LAS OPCIONES <= MAX_DTE
    # ============================================================

    all_options = []

    today = datetime.today()

    for expiration in expirations:

        exp_date = datetime.strptime(
            expiration,
            "%Y-%m-%d"
        )

        dte = (
            exp_date - today
        ).days

        if dte > max_dte:
            continue

        chain = download_option_chain(
            ticker,
            expiration
        )

        calls_df = chain.calls.copy()
        puts_df = chain.puts.copy()

        calls_df["type"] = "call"
        puts_df["type"] = "put"

        calls_df["dte"] = dte
        puts_df["dte"] = dte

        all_options.append(calls_df)
        all_options.append(puts_df)

    # ============================================================
    # SI NO HAY OPCIONES EN EL RANGO
    # ============================================================

    if len(all_options) == 0:

        return {
            "symbol": symbol,
            "spot": float(spot),
            "max_dte": max_dte,
            "num_options": 0
        }

    # ============================================================
    # DATAFRAME UNIFICADO
    # ============================================================

    options_df = pd.concat(
        all_options,
        ignore_index=True
    )

    calls_df = options_df[
        options_df["type"] == "call"
    ].copy()

    puts_df = options_df[
        options_df["type"] == "put"
    ].copy()

    # ============================================================
    # OPEN INTEREST TOTAL
    # ============================================================

    calls_oi = int(
        calls_df["openInterest"]
        .fillna(0)
        .sum()
    )

    puts_oi = int(
        puts_df["openInterest"]
        .fillna(0)
        .sum()
    )

    # ============================================================
    # GAMMA DE EJEMPLO
    # ============================================================

    sample_strike = calls_df.iloc[0]["strike"]

    sample_iv = calls_df.iloc[0]["impliedVolatility"]

    sample_dte = calls_df.iloc[0]["dte"]

    gamma = calc_gamma_vectorized(
        spot,
        sample_strike,
        sample_iv,
        sample_dte / 365
    )

    # ============================================================
    # GAMMA CALLS (DTE REAL)
    # ============================================================

    calls_df["gamma"] = calc_gamma_vectorized(
        spot,
        calls_df["strike"],
        calls_df["impliedVolatility"],
        calls_df["dte"] / 365
    )

    # ============================================================
    # GAMMA PUTS (DTE REAL)
    # ============================================================

    puts_df["gamma"] = calc_gamma_vectorized(
        spot,
        puts_df["strike"],
        puts_df["impliedVolatility"],
        puts_df["dte"] / 365
    )

    # ============================================================
    # GEX
    # ============================================================

    calls_df["gex"] = (
        calls_df["gamma"]
        * calls_df["openInterest"]
    )

    puts_df["gex"] = (
        -puts_df["gamma"]
        * puts_df["openInterest"]
    )

    # ============================================================
    # GEX CALLS POR STRIKE
    # ============================================================

    gex_by_strike = (
        calls_df
        .groupby("strike")["gex"]
        .sum()
        .reset_index()
    )

    total_call_gex = float(
        calls_df["gex"].sum()
    )

    top_call_strike = float(
        gex_by_strike.loc[
            gex_by_strike["gex"].idxmax()
        ]["strike"]
    )

    # ============================================================
    # NET GEX
    # ============================================================

    options_df = pd.concat(
        [
            calls_df,
            puts_df
        ],
        ignore_index=True
    )

    net_gex_by_strike = (
        options_df
        .groupby("strike")["gex"]
        .sum()
        .reset_index()
    )

    top_net_strike = float(
        net_gex_by_strike.loc[
            net_gex_by_strike["gex"]
            .abs()
            .idxmax()
        ]["strike"]
    )

    # ============================================================
    # RESULTADOS
    # ============================================================

    return {
        "symbol": symbol,
        "spot": float(spot),
        "max_dte": max_dte,
        "num_expirations": len(expirations),
        "num_options": len(options_df),
        "calls_oi": calls_oi,
        "puts_oi": puts_oi,
        "sample_gamma": float(gamma),
        "total_call_gex": total_call_gex,
        "top_call_strike": top_call_strike,
        "top_net_strike": top_net_strike,
        "net_gex_by_strike": net_gex_by_strike,
    }
