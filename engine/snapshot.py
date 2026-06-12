# engine/snapshot.py

import os
import shutil
import pandas as pd

from datetime import datetime

from engine.data import (
    load_ticker,
    get_spot_price,
    get_expirations,
    download_option_chain
)


CACHE_DIR = "data_cache"

HISTORY_DIR = os.path.join(
    CACHE_DIR,
    "history"
)


def get_snapshot_path(symbol):

    symbol = symbol.upper()

    return os.path.join(
        CACHE_DIR,
        f"{symbol}_latest.parquet"
    )


def get_available_expirations(symbol):

    #
    # Ya no llamamos a Yahoo.
    # Leemos expiraciones desde snapshot.
    #

    df = load_snapshot(symbol)

    expirations = sorted(
        df["expiration"]
        .dropna()
        .unique()
        .tolist()
    )

    return expirations


def download_snapshot(symbol):

    ticker = load_ticker(symbol)

    spot = get_spot_price(ticker)

    expirations = get_expirations(ticker)

    today = datetime.today()

    all_options = []

    for expiration in expirations:

        try:

            exp_date = datetime.strptime(
                expiration,
                "%Y-%m-%d"
            )

            dte = (
                exp_date - today
            ).days

            chain = download_option_chain(
                ticker,
                expiration
            )

            calls = chain.calls.copy()

            calls["type"] = "call"
            calls["expiration"] = expiration
            calls["dte"] = dte

            puts = chain.puts.copy()

            puts["type"] = "put"
            puts["expiration"] = expiration
            puts["dte"] = dte

            all_options.append(calls)
            all_options.append(puts)

        except Exception as e:

            print(
                f"Error descargando {expiration}: {e}"
            )

    if len(all_options) == 0:

        raise Exception(
            f"No se pudieron descargar opciones para {symbol}"
        )

    options_df = pd.concat(
        all_options,
        ignore_index=True
    )

    options_df["spot"] = spot

    options_df["symbol"] = symbol.upper()

    options_df["snapshot_time"] = (
        datetime.now()
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    return options_df


def save_snapshot(
    symbol,
    df
):

    symbol = symbol.upper()

    os.makedirs(
        CACHE_DIR,
        exist_ok=True
    )

    os.makedirs(
        HISTORY_DIR,
        exist_ok=True
    )

    #
    # HISTÓRICO
    #

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    history_path = os.path.join(
        HISTORY_DIR,
        f"{symbol}_{timestamp}.parquet"
    )

    df.to_parquet(
        history_path,
        index=False
    )

    #
    # LATEST
    #

    latest_path = get_snapshot_path(
        symbol
    )

    df.to_parquet(
        latest_path,
        index=False
    )

    return latest_path


def load_snapshot(symbol):

    path = get_snapshot_path(
        symbol
    )

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"No existe snapshot para {symbol}"
        )

    return pd.read_parquet(path)


def snapshot_exists(symbol):

    path = get_snapshot_path(
        symbol
    )

    return os.path.exists(path)


def update_snapshot(symbol):

    df = download_snapshot(
        symbol
    )

    save_snapshot(
        symbol,
        df
    )

    cleanup_old_snapshots(
        max_days=30
    )

    return df


def cleanup_old_snapshots(
    max_days=30
):

    if not os.path.exists(
        HISTORY_DIR
    ):
        return

    now = datetime.now()

    for filename in os.listdir(
        HISTORY_DIR
    ):

        if not filename.endswith(
            ".parquet"
        ):
            continue

        full_path = os.path.join(
            HISTORY_DIR,
            filename
        )

        modified = datetime.fromtimestamp(
            os.path.getmtime(
                full_path
            )
        )

        age_days = (
            now - modified
        ).days

        if age_days > max_days:

            try:

                os.remove(
                    full_path
                )

            except Exception:
                pass


def get_snapshot_info(symbol):

    path = get_snapshot_path(
        symbol
    )

    if not os.path.exists(path):

        return None

    modified = datetime.fromtimestamp(
        os.path.getmtime(path)
    )

    size_mb = round(
        os.path.getsize(path)
        / 1024
        / 1024,
        2
    )

    return {
        "path": path,
        "modified": modified,
        "size_mb": size_mb
    }


def list_history(symbol):

    symbol = symbol.upper()

    if not os.path.exists(
        HISTORY_DIR
    ):
        return []

    files = []

    for filename in os.listdir(
        HISTORY_DIR
    ):

        if not filename.startswith(
            f"{symbol}_"
        ):
            continue

        if not filename.endswith(
            ".parquet"
        ):
            continue

        files.append(filename)

    files.sort(
        reverse=True
    )

    return files
