from typing import Any

import pandas as pd

from utils.formatters import as_number


def find_records(data: Any) -> list[dict]:
    """Find record arrays in KB JSON responses without assuming one wrapper key."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    preferred = [
        "Record1", "out2", "out1", "record", "records", "items", "data",
        "output", "result", "list",
    ]
    for key in preferred:
        value = data.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
        if isinstance(value, dict):
            nested = find_records(value)
            if nested:
                return nested
    for value in data.values():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value
    return []


def numeric_column(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    for c in candidates:
        if c in df.columns:
            return df[c].map(as_number)
    return pd.Series([0.0] * len(df), index=df.index)


def prepare_holdings(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    name_col = next((c for c in ["is_nm", "종목명"] if c in df), None)
    code_col = next((c for c in ["is_cd", "shrt_cd", "종목코드", "종목번호"] if c in df), None)
    if name_col:
        df["종목"] = df[name_col]
    if code_col:
        df["종목코드"] = df[code_col]
    mapping = {
        "보유수량": ["hld_q", "gnrl_q", "보유수량", "수량"],
        "현재가": ["now_prc", "현재가"],
        "평가금액": ["val_amt", "평가금액"],
        "매입금액": ["byng_amt", "매입금액"],
        "평가손익": ["val_pl", "평가손익"],
        "수익률(%)": ["val_yld", "val_yld_sum", "평가수익율", "수익률"],
        "매입평균가": ["byng_avr_prc", "매입평균가"],
    }
    for output, candidates in mapping.items():
        df[output] = numeric_column(df, candidates)
    return df


def prepare_market(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    mapping = {
        "순위": ["rnk", "순위"],
        "종목코드": ["is_cd", "shrt_cd", "종목코드"],
        "종목명": ["is_nm", "종목명"],
        "현재가": ["now_prc", "현재가"],
        "등락률(%)": ["up_dwn_r_p2", "등락율P2", "등락률"],
        "등락폭": ["bdy_cmpr", "전일대비"],
        "거래량": ["acml_vlm", "vlm", "거래량", "누적거래량"],
        "거래대금(원)": ["acml_dl_tw_amt", "dl_tw_amt", "거래대금"],
        "전일거래량대비(%)": ["bdy_vlm_cmpr_r_p2", "전일거래량대비율P2"],
        "급증율(%)": ["sdn_incrs_r_p2", "급증율P2"],
    }
    for output, candidates in mapping.items():
        for c in candidates:
            if c in df.columns:
                df[output] = df[c].map(as_number)
                break
    if "종목명" not in df.columns and "is_nm" in df.columns:
        df["종목명"] = df["is_nm"]
    return df
