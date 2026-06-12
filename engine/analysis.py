import pandas as pd

# Funciones de acceso a datos (Yahoo Finance)
from engine.data import (
    load_ticker,
    get_spot_price,
    get_expirations,
    download_option_chain
)

# Funciones matemáticas (Black-Scholes, Gamma, etc.)
from engine.calculations import (
    calc_gamma_vectorized
)


def run_analysis(symbol, max_dte):

    # ============================================================
    # 1. CARGA DEL ACTIVO
    # ============================================================

    # Descarga el objeto ticker desde Yahoo
    ticker = load_ticker(symbol)

    # Obtiene el precio spot actual
    spot = get_spot_price(ticker)

    # ============================================================
    # 2. EXPIRACIONES DISPONIBLES
    # ============================================================

    # Lista de todas las expiraciones disponibles
    expirations = get_expirations(ticker)

    # De momento trabajamos SOLO con la primera expiración
    # (más adelante recorreremos todas)
    first_expiration = expirations[0]

    # ============================================================
    # 3. DESCARGA DE OPTION CHAIN
    # ============================================================

    # Descarga Calls y Puts de la expiración seleccionada
    chain = download_option_chain(
        ticker,
        first_expiration
    )

    # Copias de trabajo
    calls_df = chain.calls.copy()
    puts_df = chain.puts.copy()

    # Etiquetas para distinguir Calls y Puts
    calls_df["type"] = "call"
    puts_df["type"] = "put"

    # ============================================================
    # 4. OPEN INTEREST AGREGADO
    # ============================================================

    # Open Interest total de Calls
    calls_oi = int(
        chain.calls["openInterest"]
        .fillna(0)
        .sum()
    )

    # Open Interest total de Puts
    puts_oi = int(
        chain.puts["openInterest"]
        .fillna(0)
        .sum()
    )

    # ============================================================
    # 5. PRUEBA DE GAMMA INDIVIDUAL
    # ============================================================

    # Primera opción de la cadena
    sample_strike = chain.calls.iloc[0]["strike"]

    sample_iv = chain.calls.iloc[0]["impliedVolatility"]

    # Cálculo de Gamma para una sola opción
    gamma = calc_gamma_vectorized(
        spot,
        sample_strike,
        sample_iv,
        30 / 365
    )

    # ============================================================
    # 6. GAMMA PARA TODAS LAS CALLS
    # ============================================================

    calls_df["gamma"] = calc_gamma_vectorized(
        spot,
        calls_df["strike"],
        calls_df["impliedVolatility"],
        30 / 365
    )

    # ============================================================
    # 7. GAMMA PARA TODAS LAS PUTS
    # ============================================================

    puts_df["gamma"] = calc_gamma_vectorized(
        spot,
        puts_df["strike"],
        puts_df["impliedVolatility"],
        30 / 365
    )

    # ============================================================
    # 8. GEX INDIVIDUAL
    # ============================================================

    # Call GEX
    calls_df["gex"] = (
        calls_df["gamma"]
        * calls_df["openInterest"]
    )

    # Put GEX
    # Signo negativo para obtener Net GEX
    puts_df["gex"] = (
        -puts_df["gamma"]
        * puts_df["openInterest"]
    )

    # ============================================================
    # 9. GEX POR STRIKE (SOLO CALLS)
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

    # ============================================================
    # 10. UNIFICACIÓN CALLS + PUTS
    # ============================================================

    options_df = pd.concat(
        [
            calls_df,
            puts_df
        ],
        ignore_index=True
    )

    # ============================================================
    # 11. STRIKE CON MAYOR CALL GEX
    # ============================================================

    top_call_strike = float(
        gex_by_strike.loc[
            gex_by_strike["gex"].idxmax()
        ]["strike"]
    )

    # ============================================================
    # 12. NET GEX POR STRIKE
    # ============================================================

    net_gex_by_strike = (
        options_df
        .groupby("strike")["gex"]
        .sum()
        .reset_index()
    )

    # ============================================================
    # 13. STRIKE DOMINANTE DE NET GEX
    # ============================================================

    top_net_strike = float(
        net_gex_by_strike.loc[
            net_gex_by_strike["gex"]
            .abs()
            .idxmax()
        ]["strike"]
    )

    # ============================================================
    # 14. RESULTADO DEVUELTO A STREAMLIT
    # ============================================================

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
        "total_call_gex": total_call_gex,
        "top_call_strike": top_call_strike,
        "top_net_strike": top_net_strike,
        "net_gex_by_strike": net_gex_by_strike,
    }
