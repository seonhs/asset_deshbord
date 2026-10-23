import time

import requests

from config.settings import BASE_URL, TIMEOUT, TOKEN_URL


class KBClient:
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.session = requests.Session()
        self.token = None
        self.token_expiry = 0

    def authenticate(self):
        if self.token and time.time() < self.token_expiry - 60:
            return self.token
        response = self.session.post(
            TOKEN_URL,
            json={
                "dataHeader": {
                    "ipAddr": "127.0.0.1",
                    "macAddr": "00:00:00:00:00:00",
                },
                "dataBody": {
                    "appKey": self.app_key,
                    "appSecret": self.app_secret,
                    "grantType": "client_credentials",
                },
            },
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        header = payload.get("dataHeader", {})
        body = payload.get("dataBody", {})
        token = body.get("access_token")
        if not token:
            message = header.get("resultMessage") or header.get("processMessage") or payload
            raise RuntimeError(f"토큰 발급 실패: {message}")
        self.token = token
        self.token_expiry = time.time() + int(body.get("expires_in", 3600))
        return token

    def post(self, endpoint: str, body: dict | None = None):
        token = self.authenticate()
        request_payload = {
            "dataHeader": {
                "ipAddr": "127.0.0.1",
                "macAddr": "00:00:00:00:00:00",
            },
            "dataBody": body or {},
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/{endpoint}",
            json=request_payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=TIMEOUT,
        )
        if not response.ok:
            excerpt = response.text[:800]
            raise RuntimeError(f"HTTP {response.status_code} / {endpoint}: {excerpt}")
        try:
            payload = response.json()
        except ValueError:
            raise RuntimeError(f"{endpoint} 응답이 JSON이 아닙니다: {response.text[:300]}")
        header = payload.get("dataHeader", {}) if isinstance(payload, dict) else {}
        body_data = payload.get("dataBody", payload)
        if isinstance(header, dict):
            code = str(header.get("resultCode", header.get("processCode", "")))
            if code and code not in {"0", "00", "0000", "200"}:
                message = header.get("resultMessage") or header.get("processMessage") or code
                raise RuntimeError(f"{endpoint} 응답 오류: {message}")
        return body_data
