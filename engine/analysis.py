import pandas as pd

from engine.snapshot import (
    load_snapshot
)

from engine.calculations import (
    calc_gamma_vectorized
)


def run_analysis(
    symbol,
    max_dte
):

    options_df = load_snapshot(
        symbol
    )

    spot = float(
        options_df["spot"].iloc[0]
    )

    options_df = options_df[
        options_df["dte"] <= max_dte
    ].copy()

    if len(options_df) == 0:

        return {
            "symbol": symbol,
            "spot": spot,
            "num_options": 0
        }

    #
    # FILTRO 85%-115%
    #

    low_strike = spot * 0.85

    high_strike = spot * 1.15

    options_df = options_df[
        (
            options_df["strike"]
            >= low_strike
        )
        &
        (
            options_df["strike"]
            <= high_strike
        )
    ]

    options_df = options_df.dropna(
        subset=[
            "impliedVolatility",
            "openInterest"
        ]
    )

    options_df = options_df[
        options_df["openInterest"] > 0
    ]

    calls_df = options_df[
        options_df["type"] == "call"
    ].copy()

    puts_df = options_df[
        options_df["type"] == "put"
    ].copy()

    calls_oi = int(
        calls_df["openInterest"]
        .sum()
    )

    puts_oi = int(
        puts_df["openInterest"]
        .sum()
    )

    sample_strike = float(
        calls_df.iloc[0]["strike"]
    )

    sample_iv = float(
        calls_df.iloc[0]["impliedVolatility"]
    )

    sample_dte = int(
        calls_df.iloc[0]["dte"]
    )

    gamma = calc_gamma_vectorized(
        spot,
        sample_strike,
        sample_iv,
        sample_dte / 365
    )

    calls_df["gamma"] = (
        calc_gamma_vectorized(
            spot,
            calls_df["strike"],
            calls_df["impliedVolatility"],
            calls_df["dte"] / 365
        )
    )

    puts_df["gamma"] = (
        calc_gamma_vectorized(
            spot,
            puts_df["strike"],
            puts_df["impliedVolatility"],
            puts_df["dte"] / 365
        )
    )

    #
    # GEX REAL
    #

    calls_df["gex"] = (
        calls_df["gamma"]
        * calls_df["openInterest"]
        * 100
        * (spot ** 2)
        * 0.01
    )

    puts_df["gex"] = (
        -puts_df["gamma"]
        * puts_df["openInterest"]
        * 100
        * (spot ** 2)
        * 0.01
    )

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
        .sort_values("strike")
    )

    #
    # CALL WALL
    #

    call_walls = (
        calls_df
        .groupby("strike")["gex"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(3)
        .index
        .tolist()
    )

    #
    # PUT WALL
    #

    put_walls = (
        puts_df
        .groupby("strike")["gex"]
        .sum()
        .sort_values()
        .head(3)
        .index
        .tolist()
    )

    call_wall = (
        call_walls[0]
        if len(call_walls) > 0
        else None
    )

    put_wall = (
        put_walls[0]
        if len(put_walls) > 0
        else None
    )

    #
    # TOP NET
    #

    top_net_strike = float(
        net_gex_by_strike.loc[
            net_gex_by_strike["gex"]
            .abs()
            .idxmax()
        ]["strike"]
    )

    total_net_gex = float(
        net_gex_by_strike["gex"]
        .sum()
    )

    return {
        "symbol": symbol,
        "spot": spot,
        "max_dte": max_dte,
        "calls_oi": calls_oi,
        "puts_oi": puts_oi,
        "sample_gamma": float(gamma),
        "call_wall": call_wall,
        "put_wall": put_wall,
        "call_walls": call_walls,
        "put_walls": put_walls,
        "top_net_strike": top_net_strike,
        "total_net_gex": total_net_gex,
        "net_gex_by_strike": net_gex_by_strike
    }
