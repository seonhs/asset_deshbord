import streamlit as st

from utils.formatters import as_number, first_value, fmt_won


def render_asset_metrics(balance: dict, cash: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    total_assets = first_value(balance, ["nt_asts_val_amt", "val_amt_sum", "순자산평가금액", "평가금액합계"])
    stock_value = first_value(balance, ["scrts_nt_val_amt", "val_amt_sum", "유가순평가금액", "평가금액합계"])
    profit = first_value(balance, ["val_pl_sum", "val_pl", "평가손익합계", "평가손익"])
    return_rate = first_value(balance, ["val_yld_sum", "val_yld", "평가수익율합계", "평가수익율"])
    cash_available = first_value(
        cash,
        ["ordr_psbl_csh", "ordr_psbl_amt", "ordr_std_dpstn_csh", "주문가능현금", "주문가능금액"],
    )

    col1.metric("순자산 평가금액", fmt_won(total_assets))
    col2.metric("주식 평가금액", fmt_won(stock_value))
    col3.metric("평가손익", fmt_won(profit))
    col4.metric("평가수익률", f"{as_number(return_rate):,.2f}%")
    st.caption(f"주문 가능 현금(예수금 API): {fmt_won(cash_available)}")
