import pandas as pd

from datetime import datetime

from engine.data import (
    load_ticker,
    get_spot_price,
    download_option_chain
)

from engine.calculations import (
    calc_gamma_vectorized
)


def run_analysis(
    symbol,
    selected_expiration
):

    ticker = load_ticker(symbol)

    spot = get_spot_price(ticker)

    exp_date = datetime.strptime(
        selected_expiration,
        "%Y-%m-%d"
    )

    dte = max(
        (
            exp_date
            - datetime.today()
        ).days,
        1
    )

    chain = download_option_chain(
        ticker,
        selected_expiration
    )

    calls_df = chain.calls.copy()
    puts_df = chain.puts.copy()

    calls_df["type"] = "call"
    puts_df["type"] = "put"

    calls_df["dte"] = dte
    puts_df["dte"] = dte

    options_df = pd.concat(
        [
            calls_df,
            puts_df
        ],
        ignore_index=True
    )

    #
    # FILTRO 85%-115%
    #

    low_strike = spot * 0.85
    high_strike = spot * 1.15

    options_df = options_df[
        (
            options_df["strike"] >= low_strike
        )
        &
        (
            options_df["strike"] <= high_strike
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

    if len(calls_df) == 0:

        return {
            "symbol": symbol,
            "spot": float(spot),
            "error": "No hay datos válidos"
        }

    calls_oi = int(
        calls_df["openInterest"]
        .sum()
    )

    puts_oi = int(
        puts_df["openInterest"]
        .sum()
    )

    sample_strike = calls_df.iloc[0]["strike"]

    sample_iv = calls_df.iloc[0][
        "impliedVolatility"
    ]

    gamma = calc_gamma_vectorized(
        spot,
        sample_strike,
        sample_iv,
        dte / 365
    )

    #
    # GAMMAS
    #

    calls_df["gamma"] = calc_gamma_vectorized(
        spot,
        calls_df["strike"],
        calls_df["impliedVolatility"],
        calls_df["dte"] / 365
    )

    puts_df["gamma"] = calc_gamma_vectorized(
        spot,
        puts_df["strike"],
        puts_df["impliedVolatility"],
        puts_df["dte"] / 365
    )

    #
    # GEX
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

    #
    # NET GEX
    #

    net_gex_by_strike = (
        options_df
        .groupby("strike")["gex"]
        .sum()
        .reset_index()
        .sort_values("strike")
    )

    #
    # CALL WALLS
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
    # PUT WALLS
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
        float(call_walls[0])
        if len(call_walls) > 0
        else None
    )

    put_wall = (
        float(put_walls[0])
        if len(put_walls) > 0
        else None
    )

    #
    # GAMMA FLIP
    #

    net_gex_by_strike["sign"] = (
        net_gex_by_strike["gex"]
        .apply(
            lambda x:
            1 if x > 0 else -1
        )
    )

    net_gex_by_strike["flip"] = (
        net_gex_by_strike["sign"]
        .diff()
    )

    flips = net_gex_by_strike[
        net_gex_by_strike["flip"] != 0
    ]

    gamma_flip = None

    if len(flips) > 0:

        gamma_flip = float(
            flips.iloc[
                (
                    flips["strike"]
                    - spot
                ).abs().argmin()
            ]["strike"]
        )

    #
    # EXPECTED MOVE
    #

    atm_idx = (
        calls_df["strike"]
        - spot
    ).abs().idxmin()

    atm_iv = float(
        calls_df.loc[
            atm_idx,
            "impliedVolatility"
        ]
    )

    expected_move = (
        spot
        * atm_iv
        * (
            dte / 365
        ) ** 0.5
    )

    lower_expected = (
        spot
        - expected_move
    )

    upper_expected = (
        spot
        + expected_move
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

        "spot": float(spot),

        "expiration": selected_expiration,

        "dte": dte,

        "calls_oi": calls_oi,

        "puts_oi": puts_oi,

        "sample_gamma": float(gamma),

        "call_wall": call_wall,

        "put_wall": put_wall,

        "call_walls": call_walls,

        "put_walls": put_walls,

        "gamma_flip": gamma_flip,

        "top_net_strike": top_net_strike,

        "total_net_gex": total_net_gex,

        "atm_iv": atm_iv,

        "expected_move": expected_move,

        "lower_expected": lower_expected,

        "upper_expected": upper_expected,

        "net_gex_by_strike": net_gex_by_strike

    }
