col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Spot",
    round(results["spot"], 2)
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
