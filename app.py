import pandas as pd
import streamlit as st

from components.charts import render_holdings_chart
from components.metrics import render_asset_metrics
from components.tables import render_holdings_table, render_market_table
from config.settings import APP_KEY, APP_SECRET, BASE_URL
from services.account_service import get_balance, get_cash, get_holdings
from services.kb_client import KBClient
from services.market_service import (
    get_quote,
    get_return_rank,
    get_surge,
    get_value_rank,
    get_volume_rank,
)
from utils.formatters import as_number, fmt_won

st.set_page_config(page_title="KB 국내주식 자산 대시보드", page_icon="📈", layout="wide")


def show_api_error(label: str, exc: Exception):
    st.warning(f"{label} 조회 실패: {exc}")
    st.caption("앱 키/시크릿, API 이용 권한, 필수 요청 필드, API 서버의 공통 헤더 규칙을 확인하세요.")


@st.cache_resource
def get_client() -> KBClient:
    return KBClient(APP_KEY, APP_SECRET)


st.title("📈 KB 국내주식 자산 대시보드")
st.caption("국내주식 계좌 평가 · 보유 종목 · 시장 급등주 탐색 | KB증권 Open API")

with st.sidebar:
    st.header("연결 설정")
    st.write("앱 키는 화면에 직접 입력하지 않고 환경변수 또는 Streamlit secrets 사용을 권장합니다.")
    st.caption("KBSEC_APP_KEY / KBSEC_APP_SECRET")
    st.caption(f"API 서버: {BASE_URL}")
    st.selectbox("통합시세 거래소(KRT/NXT)", ["통합시세 거래소"])
    balance_exchange = "A"
    quote_exchange = "0"
    rank_exchange = "0"

    market = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
    market_code = {"전체": "1", "KOSPI": "2", "KOSDAQ": "3"}[market]
    count = st.slider("급등주 목록 개수", 10, 100, 30, 10)
    refresh = st.button("데이터 새로고침", type="primary", use_container_width=True)

connected = bool(APP_KEY and APP_SECRET)
if not connected:
    st.info("API 연결을 시작하려면 KBSEC_APP_KEY와 KBSEC_APP_SECRET을 설정하세요. 아래 '실행 방법' 안내를 참고하세요.")

if connected:
    client = get_client()
    if refresh:
        st.cache_data.clear()

    st.subheader("계좌 자산 현황")
    balance = {}
    holdings = pd.DataFrame()
    cash = {}
    with st.spinner("계좌 정보를 조회하고 있습니다..."):
        try:
            balance = get_balance(client, balance_exchange)
        except Exception as e:
            show_api_error("잔고현황 SSQM2952", e)
        try:
            holdings = get_holdings(client)
        except Exception as e:
            show_api_error("보유주식 SSQM1801", e)
        try:
            cash = get_cash(client)
        except Exception as e:
            show_api_error("예수금 SSQM0004", e)

    render_asset_metrics(balance, cash)
    with st.expander("계좌 API 원본 응답 보기"):
        st.write("SSQM2952")
        st.json(balance or {})
        st.write("SSQM0004")
        st.json(cash or {})

    st.subheader("보유 종목")
    render_holdings_table(holdings)
    render_holdings_chart(holdings)

    st.divider()
    st.subheader("국내 급등주 탐색")
    st.caption("실시간 조건 검색 결과이며 투자 추천이나 미래 수익 보장이 아닙니다. 거래정지·관리종목 등 상태를 별도로 확인하세요.")
    tab1, tab2, tab3, tab4 = st.tabs(["급등·급락", "등락률 상위", "거래량 상위", "거래대금 상위"])

    with tab1:
        direction = st.radio("방향", ["급등", "급락"], horizontal=True, key="surge_dir")
        try:
            raw, df = get_surge(client, rank_exchange, market_code, count, direction)
            render_market_table(
                df,
                ["종목코드", "종목명", "현재가", "등락률(%)", "거래량", "거래대금(원)", "급증율(%)"],
                "급등·급락 데이터가 없거나 응답 배열을 찾지 못했습니다.",
                raw,
            )
        except Exception as e:
            show_api_error("급등·급락 IVU10270", e)

    with tab2:
        sort_label = st.selectbox("정렬", ["상승률", "하락률", "상승폭", "하락폭"], key="ret_sort")
        sort_code = {"상승률": "1", "하락률": "2", "상승폭": "3", "하락폭": "4"}[sort_label]
        try:
            raw, df = get_return_rank(client, rank_exchange, market_code, count, sort_code)
            render_market_table(
                df,
                ["종목코드", "종목명", "현재가", "등락률(%)", "등락폭", "거래량"],
                "등락률 데이터가 없거나 응답 배열을 찾지 못했습니다.",
                raw,
            )
        except Exception as e:
            show_api_error("등락률 IVU10240", e)

    with tab3:
        try:
            raw, df = get_volume_rank(client, rank_exchange, market_code)
            render_market_table(
                df,
                ["종목코드", "종목명", "현재가", "등락률(%)", "거래량", "전일거래량대비(%)", "거래대금(원)"],
                "거래량 상위 데이터가 없거나 응답 배열을 찾지 못했습니다.",
                raw,
                limit=count,
            )
        except Exception as e:
            show_api_error("거래량 상위 IVU10280", e)

    with tab4:
        try:
            raw, df = get_value_rank(client, rank_exchange, market_code, count)
            render_market_table(
                df,
                ["종목코드", "종목명", "현재가", "등락률(%)", "거래량", "거래대금(원)"],
                "거래대금 상위 데이터가 없거나 응답 배열을 찾지 못했습니다.",
                raw,
                limit=count,
            )
        except Exception as e:
            show_api_error("거래대금 상위 IVU10210", e)

    st.divider()
    st.subheader("종목 현재가 조회")
    ticker = st.text_input("종목 단축코드 (6자리)", value="005930", max_chars=6, help="예: 삼성전자 005930")
    if st.button("현재가 조회"):
        if not ticker.isdigit() or len(ticker) != 6:
            st.error("종목코드는 숫자 6자리로 입력하세요.")
        else:
            try:
                quote = get_quote(client, quote_exchange, ticker)
                qcols = st.columns(4)
                qcols[0].metric("종목", quote.get("is_nm", ticker))
                qcols[1].metric("현재가", fmt_won(quote.get("now_prc", 0)))
                qcols[2].metric("등락률", f"{as_number(quote.get('up_dwn_r_p2', 0)):.2f}%")
                qcols[3].metric("거래량", f"{as_number(quote.get('acml_vlm', 0)):,.0f}")
                with st.expander("현재가 원본 응답"):
                    st.json(quote)
            except Exception as e:
                show_api_error("현재가 IVU10140", e)
else:
    st.subheader("미리보기: 대시보드에 연결되는 API")
    st.dataframe(pd.DataFrame([
        {"화면": "자산 현황", "API": "SSQM2952", "요청 필드": "excg_mktpr_ccd (선택)"},
        {"화면": "보유 종목", "API": "SSQM1801", "요청 필드": "inq_clsf=0, mkt_tm_ccd=1"},
        {"화면": "예수금", "API": "SSQM0004", "요청 필드": "is_no (선택)"},
        {"화면": "현재가", "API": "IVU10140", "요청 필드": "excg_clsf, shrt_cd"},
        {"화면": "등락률 상위", "API": "IVU10240", "요청 필드": "excg_clsf, mkt_clsf, inq_cnt, srt_clsf"},
        {"화면": "급등·급락", "API": "IVU10270", "요청 필드": "excg_clsf, mkt_clsf, inq_cnt, up_dwn_ccd, minute_dy_ccd, minute_dy_unt"},
        {"화면": "거래량 상위", "API": "IVU10280", "요청 필드": "excg_clsf, mkt_clsf"},
        {"화면": "거래대금 상위", "API": "IVU10210", "요청 필드": "excg_clsf, mkt_clsf, thdy_bdy_clsf, inq_cnt, srt_clsf"},
    ]), use_container_width=True, hide_index=True)

with st.expander("실행 방법 및 API 연결 참고"):
    st.markdown("""
1. Python 3.10 이상을 설치합니다.
2. `pip install -r requirements.txt`
3. 환경변수 `KBSEC_APP_KEY`, `KBSEC_APP_SECRET`을 설정합니다.
4. `streamlit run app.py` 실행 후 브라우저에서 확인합니다.

토큰 발급은 엑셀 `토큰 발급` 시트의 명세를 사용합니다.
- POST `/oauth2/token`
- JSON: `grantType=client_credentials`, `appKey`, `appSecret`
- 응답: `access_token`, `token_type`, `expires_in`
- API 호출 Authorization 헤더: `Bearer {access_token}`

업무 API의 요청·응답은 `dataHeader` + `dataBody` envelope로 처리합니다. 예시의 `ipAddr`, `macAddr`를 포함했습니다. KB 개발자 포털의 계정별 최신 호출 규칙과 권한을 확인해 주세요.
""")
