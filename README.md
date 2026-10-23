# KB 국내주식 자산 대시보드

KB증권 Open API로 계좌 잔고, 보유 종목, 예수금, 시세, 급등주를 조회하는 Streamlit 앱입니다. 조회 전용이며 주문 기능은 포함하지 않습니다.

## 실행

Python 3.10 이상이 필요합니다.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/activate
pip install -r requirements.txt
```

프로젝트 루트에 `.env`를 만들고 키를 넣습니다. `.env`는 Git에 올리지 마세요.

```
KBSEC_APP_KEY=발급받은앱키
KBSEC_APP_SECRET=발급받은앱시크릿
```

선택 항목:

```
KBSEC_API_BASE_URL=https://developer.kbsec.com:32484
```

`KBSEC_BASE_URL`도 동일하게 인식합니다. 둘 다 없으면 위 기본 주소를 사용합니다.

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`을 엽니다.

## 구성

| 경로 | 역할 |
|---|---|
| `app.py` | 화면 조립, 사이드바, 메뉴 |
| `config/settings.py` | `.env` 로딩, 서버 주소, 타임아웃 |
| `services/kb_client.py` | 토큰 발급, 공통 HTTP 요청 |
| `services/account_service.py` | 잔고, 보유 종목, 예수금 |
| `services/market_service.py` | 현재가, 급등주, 거래량·거래대금 순위 |
| `components/` | 자산 카드, 표, 차트 |
| `utils/` | 금액 포맷, API 응답 파싱 |

인증은 `kb_client.py`에만 두고, 페이지에서 `load_dotenv()`나 토큰 발급을 반복하지 않습니다.

## 연결 API

| 화면 | API | 요청 필드 |
|---|---|---|
| 자산 현황 | `SSQM2952` | `excg_mktpr_ccd` (선택) |
| 보유 종목 | `SSQM1801` | `inq_clsf=0`, `mkt_tm_ccd=1` |
| 예수금 | `SSQM0004` | `is_no` (선택) |
| 현재가 | `IVU10140` | `excg_clsf`, `shrt_cd` |
| 등락률 상위 | `IVU10240` | `excg_clsf`, `mkt_clsf`, `inq_cnt`, `srt_clsf` |
| 급등·급락 | `IVU10270` | `excg_clsf`, `mkt_clsf`, `inq_cnt`, `up_dwn_ccd`, `minute_dy_ccd`, `minute_dy_unt` |
| 거래량 상위 | `IVU10280` | `excg_clsf`, `mkt_clsf` |
| 거래대금 상위 | `IVU10210` | `excg_clsf`, `mkt_clsf`, `thdy_bdy_clsf`, `inq_cnt`, `srt_clsf` |

토큰:

- `POST {BASE_URL}/oauth2/token`
- 본문: `dataHeader`(`ipAddr`, `macAddr`) + `dataBody`(`grantType=client_credentials`, `appKey`, `appSecret`)
- 응답 토큰: `dataBody.access_token`
- 업무 API: `POST {BASE_URL}/api/v1/{endpoint}`, `Authorization: Bearer {access_token}`

응답의 종목 배열 이름은 API마다 다를 수 있어 `utils/parsers.py`의 `find_records()`가 `Record1`, `out2`, `out1` 등을 탐색합니다. 화면에 데이터가 없으면 expander의 원본 응답을 확인하고 파서를 보정하세요.

## 주의

- KB 개발자 포털에서 API 이용 신청과 계좌 권한이 있어야 합니다.
- 급등주·순위 화면은 실시간 조건 검색 결과이며 투자 추천이 아닙니다.
- 401/403이나 필드 오류가 나면 포털의 최신 공통 헤더와 계정별 호출 규칙을 확인하세요.
