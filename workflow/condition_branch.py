# workflow/condition_branch.py - Defines conditional logic for LangGraph workflow branching


def condition_after_result(state):
    status = state.execution_status.upper()

    if status == "SUCCESS":
        return "end"
    if status == "OTP":
        return "halt_otp"
    if status == "FAIL" and state.attempt_count < 3:
        return "retry"

    return "abandon"  # Implicitly the 'else' case
