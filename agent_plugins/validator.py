def validate_card(card_info: dict) -> bool:
    number = card_info.get("number", "")
    return number.startswith("4") or number.startswith("5")


def check_proxy(proxy_meta: dict) -> bool:
    return proxy_meta.get("score", 0) > 70
