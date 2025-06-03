from utils.logger import log_event


def assess_risk(card_info: dict, recon_result: dict) -> dict:
    risk_score = 0
    if recon_result.get("captcha"):
        risk_score += 2
    if not card_info.get("zip"):
        risk_score += 3
    if recon_result.get("checkout_steps", 1) > 2:
        risk_score += 1
    result = {
        "risk_score": risk_score,
        "risk_level": "high" if risk_score > 4 else "low",
    }
    log_event("risk_assessment", result)
    return result


def risk_assessor_node_logic(state):
    result = assess_risk(state.card_info, state.recon_result)
    state.risk_score = result["risk_score"]
    state.risk_level = result["risk_level"]
    return state
