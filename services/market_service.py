import pandas as pd

from services.kb_client import KBClient
from utils.parsers import find_records, prepare_market


def _load_market(client: KBClient, endpoint: str, body: dict) -> tuple[dict | list, pd.DataFrame]:
    raw = client.post(endpoint, body)
    return raw, prepare_market(find_records(raw))


def get_surge(
    client: KBClient,
    rank_exchange: str,
    market_code: str,
    count: int,
    direction: str,
) -> tuple[dict | list, pd.DataFrame]:
    return _load_market(client, "ivu10270", {
        "excg_clsf": rank_exchange,
        "mkt_clsf": market_code,
        "inq_cnt": str(count),
        "up_dwn_ccd": "1" if direction == "급등" else "2",
        "minute_dy_ccd": "2",
        "minute_dy_unt": "1",
    })


def get_return_rank(
    client: KBClient,
    rank_exchange: str,
    market_code: str,
    count: int,
    sort_code: str,
) -> tuple[dict | list, pd.DataFrame]:
    return _load_market(client, "ivu10240", {
        "excg_clsf": rank_exchange,
        "mkt_clsf": market_code,
        "inq_cnt": str(count),
        "srt_clsf": sort_code,
    })


def get_volume_rank(
    client: KBClient,
    rank_exchange: str,
    market_code: str,
) -> tuple[dict | list, pd.DataFrame]:
    return _load_market(client, "ivu10280", {
        "excg_clsf": rank_exchange,
        "mkt_clsf": market_code,
    })


def get_value_rank(
    client: KBClient,
    rank_exchange: str,
    market_code: str,
    count: int,
) -> tuple[dict | list, pd.DataFrame]:
    return _load_market(client, "ivu10210", {
        "excg_clsf": rank_exchange,
        "mkt_clsf": market_code,
        "thdy_bdy_clsf": "1",
        "inq_cnt": str(count),
        "srt_clsf": "1",
    })


def get_quote(client: KBClient, quote_exchange: str, ticker: str) -> dict:
    return client.post("ivu10140", {"excg_clsf": quote_exchange, "shrt_cd": ticker}) or {}
