# agents/checkout_agent.py - Logic for handling checkout process

from typing import Dict

# Attempt to import log_event and AgentState, provide placeholders if not ready
try:
    from utils.logger import log_event
except ImportError:
    print(
        "Warning: utils.logger.log_event not found in checkout_agent. Using placeholder."
    )

    def log_event(event_type, payload):
        print(f"[LOG_PLACEHOLDER:{event_type}] | {payload}")


try:
    from workflow.state_schema import AgentState  # This will be Pydantic BaseModel
except ImportError:
    print(
        "Warning: workflow.state_schema.AgentState not found in checkout_agent. Using placeholder."
    )

    class AgentState(dict):
        pass  # Basic placeholder if schema not found


# import random # Commented out as it's no longer used in the new logic


def run_checkout(
    card_info: Dict[str, any], recon_data: Dict[str, any]
) -> Dict[str, any]:
    """Simulates the checkout process based on card info and reconnaissance data."""
    print(
        f"[Checkout Agent] Running checkout for card: {card_info.get('number', 'N/A')[:4]}... with recon: {recon_data}"
    )

    # Determine success based on simplified logic
    # Card number starts with '4' (Visa) and checkout_steps from recon_data is less than 4
    is_card_valid_mock = card_info.get("number", "").startswith("4")
    checkout_complexity_ok = recon_data.get("checkout_steps", 1) < 4

    success = is_card_valid_mock and checkout_complexity_ok

    # If the basic checks pass, simulate a more nuanced outcome (e.g., OTP, or still fail due to other reasons)
    # For now, keeping it simple: if checks pass -> SUCCESS, else FAIL.
    # The previous random choice for OTP/FAIL is removed in favor of more deterministic mock logic based on inputs.
    status_code = "SUCCESS" if success else "FAIL"

    result = {
        "success": success,
        "status_code": status_code,  # More specific status code
        "attempted": True,
        "message": f"Checkout status: {status_code}",
        "analyzed_checkout_steps": recon_data.get("checkout_steps", 1),
    }
    log_event(
        "checkout_process_attempt",
        {
            "card_prefix": card_info.get("number", "N/A")[:4],
            "recon_data_summary": recon_data,
            "outcome": result,
        },
    )
    return result


def checkout_agent_node_logic(state: AgentState) -> AgentState:
    """Wrapper for run_checkout to be used as a LangGraph node."""
    card_info = state.card_info
    recon_result = state.recon_result

    if not card_info or not recon_result:
        print(
            "[Checkout Agent Node] Error: card_info or recon_result not found in state."
        )
        state.execution_status = "CHECKOUT_ERROR_MISSING_DATA"
        state.result_summary = (
            "Checkout failed: Missing card information or reconnaissance data."
        )
        state.is_final = True
        return state

    checkout_outcome = run_checkout(card_info, recon_result)

    state.execution_status = checkout_outcome.get(
        "status_code", "CHECKOUT_FAILED"
    )  # Use the new status_code
    # You might want to store the full checkout_outcome in the state as well for richer data
    # state.checkout_full_result = checkout_outcome
    state.attempt_count = (
        state.attempt_count or 0
    ) + 1  # Ensure attempt_count is not None
    print(
        f"[Checkout Agent Node] Checkout attempt {state.attempt_count} status: {state.execution_status}"
    )
    return state
