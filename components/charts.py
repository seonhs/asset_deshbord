import pandas as pd
import streamlit as st


def render_holdings_chart(holdings: pd.DataFrame) -> None:
    if holdings.empty or "종목" not in holdings.columns or "평가금액" not in holdings.columns:
        return
    chart_df = holdings[["종목", "평가금액"]].copy().set_index("종목")
    st.bar_chart(chart_df)
