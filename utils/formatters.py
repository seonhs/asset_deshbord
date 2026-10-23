from typing import Any


def as_number(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(",", "").replace("%", "")
    if not s or s in {"-", "--", "None", "null"}:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def fmt_won(value: Any) -> str:
    return f"₩{as_number(value):,.0f}"


def first_value(data: dict, keys: list[str], default=0):
    if not isinstance(data, dict):
        return default
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return default
