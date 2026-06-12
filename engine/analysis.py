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

    ticker = load_ticker(symbol)

    spot = get_spot_price(ticker)

    expirations = get_expirations(ticker)

    all_options = []

    today = datetime.today()

    term_structure = []

    for expiration in expirations:

        exp_date = datetime.strptime(
            expiration,
            "%Y-%m-%d"
        )

        dte = (
            exp_date - today
        ).days

        if dte < 0:
            continue

        chain = download_option_chain(
            ticker,
            expiration
        )

        #
        # TERM STRUCTURE
        #

        try:

            calls_tmp = chain.calls.copy()

            atm_idx = (
                calls_tmp["strike"] - spot
            ).abs().idxmin()

            atm_iv = float(
                calls_tmp.loc[
                    atm_idx,
                    "impliedVolatility"
                ]
            )

            term_structure.append(
                {
                    "expiration": expiration,
                    "dte": dte,
                    "iv": atm_iv
                }
            )

        except Exception:
            pass

        if dte > max_dte:
            continue

        calls_df = chain.calls.copy()
        puts_df = chain.puts.copy()

        calls_df["type"] = "call"
        puts_df["type"] = "put"

        calls_df["dte"] = dte
        puts_df["dte"] = dte

        all_options.append(calls_df)
        all_options.append(puts_df)

    if len(all_options) == 0:

        return {
            "symbol": symbol,
            "spot": float(spot),
            "max_dte": max_dte,
            "num_options": 0
        }

    options_df = pd.concat(
        all_options,
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

    calls_oi = int(
        calls_df["openInterest"]
        .sum()
    )

    puts_oi = int(
        puts_df["openInterest"]
        .sum()
    )

    sample_strike = calls_df.iloc[0]["strike"]

    sample_iv = calls_df.iloc[0]["impliedVolatility"]

    sample_dte = calls_df.iloc[0]["dte"]

    gamma = calc_gamma_vectorized(
        spot,
        sample_strike,
        sample_iv,
        sample_dte / 365
    )

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
    # WALLS
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

    term_df = pd.DataFrame(
        term_structure
    )

    selected_row = term_df.iloc[
        (
            term_df["dte"]
            - max_dte
        ).abs().argmin()
    ]

    selected_dte_real = int(
        selected_row["dte"]
    )

    selected_iv_atm = float(
        selected_row["iv"]
    )

    expected_move = (
        spot
        * selected_iv_atm
        * (
            selected_dte_real / 365
        ) ** 0.5
    )

    lower_expected = (
        spot - expected_move
    )

    upper_expected = (
        spot + expected_move
    )

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
        "max_dte": max_dte,
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
        "selected_iv_atm": selected_iv_atm,
        "selected_dte_real": selected_dte_real,
        "expected_move": expected_move,
        "lower_expected": lower_expected,
        "upper_expected": upper_expected,
        "net_gex_by_strike": net_gex_by_strike
    }
