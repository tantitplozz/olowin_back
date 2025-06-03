# agents/result_analyzer.py - Logic for analyzing results from DOM/redirects


# Attempt to import log_event and AgentState, provide placeholders if not ready
try:
    from utils.logger import log_event
except ImportError:
    print(
        "Warning: utils.logger.log_event not found in result_analyzer. Using placeholder."
    )

    def log_event(event_type, payload):
        print(f"[LOG_PLACEHOLDER:{event_type}] | {payload}")


try:
    from workflow.state_schema import AgentState  # This will be Pydantic BaseModel
except ImportError:
    print(
        "Warning: workflow.state_schema.AgentState not found in result_analyzer. Using placeholder."
    )

    class AgentState(dict):
        pass  # Basic placeholder if schema not found


def summarize_checkout_result(
    checkout_execution_status: str, attempt_count: int
) -> str:
    """Summarizes the result of the checkout attempt based on execution status and attempts."""
    print(
        f"[Result Analyzer] Summarizing status: '{checkout_execution_status}', Attempts: {attempt_count}"
    )

    # Default to a generic summary if status is None or unexpected
    if checkout_execution_status is None:
        summary = f"❓ Checkout status unknown after {attempt_count} attempts."
    elif (
        checkout_execution_status == "SUCCESS"
    ):  # Assuming this is the final success from checkout_agent
        summary = (
            f"✅ Transaction Completed Successfully after {attempt_count} attempts."
        )
    elif (
        checkout_execution_status == "CHECKOUT_DONE"
    ):  # If checkout_agent uses this for success
        summary = (
            f"✅ Checkout Process Done Successfully after {attempt_count} attempts."
        )
    elif checkout_execution_status == "OTP":
        summary = f"⚠️ OTP Required. Attempt {attempt_count}."
    elif (
        "FAIL" in checkout_execution_status.upper()
        or "ERROR" in checkout_execution_status.upper()
    ):  # Catch various failure/error states
        summary = f"❌ Transaction Failed (Status: {checkout_execution_status}). Attempt {attempt_count}."
    else:
        summary = f"❓ Unknown/Unhandled Checkout Status: '{checkout_execution_status}'. Attempt {attempt_count}."

    log_event(
        "analysis_summary_generation",
        {
            "raw_status": checkout_execution_status,
            "attempt_count": attempt_count,
            "generated_summary": summary,
        },
    )
    return summary


def result_analyzer_node_logic(state: AgentState) -> AgentState:
    """Wrapper for summarize_checkout_result to be used as a LangGraph node."""
    execution_status = state.execution_status  # Directly access Pydantic field
    attempt_count = state.attempt_count if state.attempt_count is not None else 0

    if execution_status is None:
        print("[Result Analyzer Node] Error: execution_status not found in state.")
        state.result_summary = (
            "Analysis failed: Execution status not available in state."
        )
        state.execution_status = (
            "ANALYZE_ERROR_NO_STATUS"  # Update status to reflect this error
        )
        state.is_final = True
        return state

    summary = summarize_checkout_result(execution_status, attempt_count)
    state.result_summary = summary

    # The graph's conditional logic (condition_after_result) will primarily determine if the process is final.
    # However, we can set is_final to True here if the analyzer deems the result terminal regardless of retries.
    if execution_status == "SUCCESS" or execution_status == "CHECKOUT_DONE":
        state.is_final = True
    # For other states like OTP or FAIL, condition_branch will decide if it's final (abandon) or leads to retry/other steps.
    # So, we might not need to set is_final explicitly for those here, letting the graph logic control it.
    # If a status analyzed here is *always* final, set state.is_final = True.

    print(f"[Result Analyzer Node] Analysis complete. Summary: {summary}")
    return state
