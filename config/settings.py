import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 찾아 읽기
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

def get_secret(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return str(value) if value else default
APP_KEY = get_secret("KBSEC_APP_KEY")
APP_SECRET = get_secret("KBSEC_APP_SECRET")
BASE_URL = get_secret(
    "KBSEC_API_BASE_URL",
    get_secret("KBSEC_BASE_URL", "https://developer.kbsec.com:32484"),
)
TOKEN_URL = f"{BASE_URL}/oauth2/token"
TIMEOUT = 20