import pandas as pd
import streamlit as st


def render_holdings_table(holdings: pd.DataFrame) -> None:
    if holdings.empty:
        st.info("보유 종목 데이터가 없거나 응답의 레코드 배열을 자동 판별하지 못했습니다. API 원본 응답 및 계좌 권한을 확인하세요.")
        return
    display_cols = [
        c for c in [
            "종목코드", "종목", "보유수량", "매입평균가", "현재가",
            "매입금액", "평가금액", "평가손익", "수익률(%)",
        ]
        if c in holdings.columns
    ]
    st.dataframe(
        holdings[display_cols].style.format({
            c: ("{:,.2f}" if c == "수익률(%)" else "{:,.0f}")
            for c in display_cols if c not in ["종목", "종목코드"]
        }),
        use_container_width=True,
        hide_index=True,
    )


def render_market_table(
    df: pd.DataFrame,
    columns: list[str],
    empty_message: str,
    raw=None,
    limit: int | None = None,
) -> None:
    if df.empty:
        st.info(empty_message)
        if raw is not None:
            with st.expander("원본 응답"):
                st.json(raw)
        return
    cols = [c for c in columns if c in df.columns]
    view = df[cols].head(limit) if limit else df[cols]
    st.dataframe(view, use_container_width=True, hide_index=True)
