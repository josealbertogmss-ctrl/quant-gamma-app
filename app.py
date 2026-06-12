import streamlit as st

from datetime import datetime

from engine.analysis import (
    run_analysis
)

from engine.snapshot import (
    update_snapshot,
    snapshot_exists,
    load_snapshot
)

from charts.plotly_charts import (
    create_gex_chart
)


st.set_page_config(
    page_title="Gamma Dashboard",
    layout="wide"
)

st.title("Gamma Dashboard")

#
# TICKER
#

ticker = st.text_input(
    "Ticker",
    value="SPY"
).upper()

#
# SNAPSHOT STATUS
#

snapshot_available = False

if ticker:

    snapshot_available = snapshot_exists(
        ticker
    )

#
# BOTONES
#

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Actualizar datos"
    ):

        try:

            with st.spinner(
                "Descargando cadena completa..."
            ):

                update_snapshot(
                    ticker
                )

            st.success(
                "Snapshot actualizado"
            )

            st.rerun()

        except Exception as e:

            st.error(str(e))

with col2:

    if snapshot_available:

        st.success(
            "Snapshot disponible"
        )

    else:

        st.warning(
            "No existe snapshot"
        )

#
# EXPIRACIONES DESDE SNAPSHOT
#

expirations = []

selected_expiration = None

if snapshot_available:

    try:

        snapshot_df = load_snapshot(
            ticker
        )

        expirations = sorted(
            snapshot_df[
                "expiration"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        if len(expirations) > 0:

            selected_expiration = st.selectbox(
                "Expiración máxima",
                expirations
            )

    except Exception as e:

        st.error(
            f"Error leyendo snapshot: {e}"
        )

#
# DTE
#

max_dte = 30

if selected_expiration:

    exp_date = datetime.strptime(
        selected_expiration,
        "%Y-%m-%d"
    )

    max_dte = (
        exp_date
        - datetime.today()
    ).days

#
# ANALIZAR
#

if st.button(
    "Analizar"
):

    try:

        results = run_analysis(
            ticker,
            max_dte
        )

        st.session_state[
            "results"
        ] = results

    except Exception as e:

        st.error(str(e))

#
# RESULTADOS
#

if "results" in st.session_state:

    results = st.session_state[
        "results"
    ]

    st.subheader(
        "Métricas"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Spot",
        round(
            results["spot"],
            2
        )
    )

    col2.metric(
        "Call Wall",
        results["call_wall"]
    )

    col3.metric(
        "Put Wall",
        results["put_wall"]
    )

    col4.metric(
        "Top Net",
        results["top_net_strike"]
    )

    st.plotly_chart(
        create_gex_chart(
            results[
                "net_gex_by_strike"
            ]
        ),
        use_container_width=True
    )

    with st.expander(
        "Debug"
    ):

        st.write(
            results
        )
