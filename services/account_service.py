import pandas as pd

from services.kb_client import KBClient
from utils.parsers import find_records, prepare_holdings


def get_balance(client: KBClient, balance_exchange: str = "A") -> dict:
    return client.post("ssqm2952", {"excg_mktpr_ccd": balance_exchange}) or {}


def get_holdings(client: KBClient) -> pd.DataFrame:
    holding_raw = client.post("ssqm1801", {
        "mkt_tm_ccd": "1",
        "nxt_key": "",
        "inq_clsf": "0",
        "is_no": "",
    })
    holdings = prepare_holdings(find_records(holding_raw))
    if not holdings.empty and "종목" in holdings.columns:
        holdings = holdings[holdings["종목"].astype(str).str.strip() != ""]
    return holdings


def get_cash(client: KBClient) -> dict:
    return client.post("ssqm0004", {"is_no": ""}) or {}
