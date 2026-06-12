import streamlit as st

from datetime import datetime

from engine.analysis import (
    run_analysis
)

from engine.snapshot import (
    update_snapshot,
    snapshot_exists,
    get_snapshot_expirations,
    cleanup_old_snapshots
)

from charts.plotly_charts import (
    create_gex_chart
)


cleanup_old_snapshots()


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
).upper().strip()

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
                "Descargando snapshot completo..."
            ):

                update_snapshot(
                    ticker
                )

            st.success(
                "Snapshot actualizado correctamente"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Error actualizando snapshot: {e}"
            )

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

        expirations = (
            get_snapshot_expirations(
                ticker
            )
        )

        if len(expirations) > 0:

            selected_expiration = st.selectbox(
                "Expiración máxima",
                expirations,
                index=len(expirations) - 1
            )

    except Exception as e:

        st.error(
            f"Error leyendo snapshot: {e}"
        )

#
# CALCULAR MAX DTE
#

max_dte = 30

if selected_expiration:

    try:

        exp_date = datetime.strptime(
            selected_expiration,
            "%Y-%m-%d"
        )

        max_dte = (
            exp_date
            - datetime.today()
        ).days

    except Exception:

        max_dte = 30

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

        st.error(
            f"Error en análisis: {e}"
        )

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
        round(
            results["call_wall"],
            2
        ) if results["call_wall"] else "-"
    )

    col3.metric(
        "Put Wall",
        round(
            results["put_wall"],
            2
        ) if results["put_wall"] else "-"
    )

    col4.metric(
        "Top Net",
        round(
            results["top_net_strike"],
            2
        ) if results["top_net_strike"] else "-"
    )

    #
    # EXPECTED MOVE
    #

    st.subheader(
        "Expected Move"
    )

    em_col1, em_col2, em_col3 = st.columns(3)

    em_col1.metric(
        "IV ATM",
        f"{results['selected_iv_atm'] * 100:.2f}%"
    )

    em_col2.metric(
        "DTE Real",
        results["selected_dte_real"]
    )

    em_col3.metric(
        "Expected Move",
        f"{results['expected_move']:.2f}"
    )

    st.write(

        f"Rango esperado: "
        f"{results['lower_expected']:.2f}"
        f" → "
        f"{results['upper_expected']:.2f}"

    )

    #
    # GAMMA LEVELS
    #

    st.subheader(
        "Gamma Levels"
    )

    g1, g2, g3 = st.columns(3)

    g1.metric(
        "Gamma Flip",
        (
            round(
                results["gamma_flip"],
                2
            )
            if results["gamma_flip"]
            else "-"
        )
    )

    g2.metric(
        "Call Wall",
        (
            round(
                results["call_wall"],
                2
            )
            if results["call_wall"]
            else "-"
        )
    )

    g3.metric(
        "Put Wall",
        (
            round(
                results["put_wall"],
                2
            )
            if results["put_wall"]
            else "-"
        )
    )

    #
    # CHART
    #

    st.plotly_chart(
        create_gex_chart(
            results[
                "net_gex_by_strike"
            ]
        ),
        use_container_width=True
    )

    #
    # DEBUG
    #

    with st.expander(
        "Debug"
    ):

        st.write(
            results
        )
