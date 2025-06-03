# agents/recon_agent.py - Logic for website reconnaissance

import ollama
import os  # Added os import
from typing import Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)  # Added tenacity

# Attempt to import log_event, provide a placeholder if utils.logger is not ready
try:
    from utils.logger import log_event
except ImportError:
    print(
        "Warning: utils.logger.log_event not found in recon_agent. Using placeholder."
    )

    def log_event(event_type: str, data: Dict[str, Any]):
        print(f"[LOG_PLACEHOLDER:{event_type}] | {data}")


# Attempt to import the actual AgentState Pydantic model
try:
    from workflow.state_schema import AgentState

    print("[Recon Agent] Successfully imported AgentState from workflow.state_schema.")
except ImportError:
    print(
        "Warning: workflow.state_schema.AgentState not found in recon_agent. Operations relying on AgentState structure might fail or use a basic dict."
    )

    # Define a very basic fallback if the real one isn't available at import time.
    # Code using AgentState will need to be robust or assume Pydantic model features.
    class AgentState(dict):  # type: ignore[no-redef]
        """Fallback AgentState if the Pydantic model from workflow.state_schema is not found."""

        target_site: Optional[str] = None
        recon_result: Optional[Dict[str, Any]] = None
        execution_status: Optional[str] = None
        result_summary: Optional[str] = None
        is_final: bool = False

        def __getattr__(self, name: str) -> Any:
            try:
                return self[name]
            except KeyError:
                # Return None for missing attributes to mimic Pydantic's Optional fields somewhat
                # or raise AttributeError if strictness is needed.
                # print(f"Warning: AgentState placeholder accessing missing attribute '{name}'")
                return None

        def __setattr__(self, name: str, value: Any) -> None:
            self[name] = value


# --- Ollama Configuration ---
# Get Ollama model and host from environment variables, with defaults
# The OLLAMA_MODEL in .env should be the primary source.
# The OLLAMA_HOST should be the address of the Ollama service from within the Docker network.
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL", "nous-hermes2")  # Default if not in .env
OLLAMA_HOST_URL = os.getenv(
    "OLLAMA_HOST", "http://ollama:11434"
)  # Default for Docker Compose service name

ollama_client = ollama.Client(host=OLLAMA_HOST_URL)  # Initialize client with host


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(
        Exception
    ),  # Retry on general exceptions from ollama.chat or parsing
)
def analyze_site_with_ollama(site_name: str) -> Dict[str, Any]:
    """Analyzes the target site using Ollama for anti-fraud features."""
    prompt = (
        f"Analyze the website '{site_name}' for its anti-fraud security features. Specifically, I need to know:\n"
        f"1. Is a CAPTCHA likely to be present during checkout or sensitive actions (answer yes/no)?\n"
        f"2. Is the site heavily reliant on JavaScript for its core functionality (answer yes/no)?\n"
        f"3. How many distinct steps are typically involved in its checkout process (answer with a number, e.g., 1, 2, 3, 4, 5)?\n"
        f"4. What level of Address Verification System (AVS) check is likely performed (e.g., none, zip only, full address, strict)?\n"
        f"Return the answers concisely, for example: CAPTCHA: yes, JavaScript: yes, Checkout Steps: 3, AVS Level: full.\n"
        f"Do not add any other explanations or conversational text."
    )

    print(
        f"[Recon Agent] Analyzing site: {site_name} using Ollama model: {OLLAMA_MODEL_NAME} at {OLLAMA_HOST_URL}"
    )
    log_event(
        "recon_ollama_request",
        {
            "site": site_name,
            "model": OLLAMA_MODEL_NAME,
            "host": OLLAMA_HOST_URL,
            "prompt": prompt,
        },
    )

    try:
        # Use the pre-configured client
        response = ollama_client.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"].lower()
        print(f"[Recon Agent] Ollama response content: {content}")

        # Basic parsing of the response - this needs to be robust
        # This parsing is very basic and assumes a fairly structured response from the LLM.
        result = {
            "captcha_required": "captcha: yes" in content
            or "captcha is yes" in content,
            "javascript_heavy": "javascript: yes" in content
            or "javascript is yes" in content,
            "checkout_steps": 1,  # Default
            "avs_check_level": "unknown",
            "raw_ollama_response": content,
        }

        # Try to parse checkout steps more accurately
        if "checkout steps:" in content:
            try:
                steps_str = content.split("checkout steps:")[1].split(",")[0].strip()
                result["checkout_steps"] = int(
                    steps_str.split()[0]
                )  # take the first number found
            except (ValueError, IndexError):
                error_source = steps_str if "steps_str" in locals() else "N/A"
                print(
                    f"[Recon Agent] Could not parse checkout_steps from: {error_source}"
                )

        # Try to parse AVS level
        if "avs level:" in content:
            try:
                avs_str = content.split("avs level:")[1].split(",")[0].strip()
                result["avs_check_level"] = avs_str
            except IndexError:
                print("[Recon Agent] Could not parse avs_check_level from response")

        log_event("recon_ollama_response", {"site": site_name, "result": result})
        return result
    except Exception as e:
        print(
            f"[Recon Agent] Error during Ollama call for site {site_name}: {e}. Will retry if attempts left."
        )
        log_event("recon_ollama_error", {"site": site_name, "error": str(e)})
        # Fallback to a default/mock result in case of Ollama error
        # This fallback will only be returned if all retry attempts fail.
        # When retrying, the original exception is raised by tenacity to trigger the next attempt.
        # So, if an error occurs that tenacity is configured to retry on, this part of the code (raising the exception)
        # is crucial for the retry mechanism to work.
        raise  # Re-raise the exception to trigger tenacity retry


# This function will be called by the LangGraph node.
# It needs to conform to the (AgentState) -> AgentState signature if not adapted by graph call.
# For now, assuming graph_controller will handle mapping the AgentState fields to this function's arguments
# and updating the state with its results.
# Or, we adapt this to work with AgentState directly if preferred for simplicity in graph_controller.

# Example of adapting to AgentState for direct use in graph_controller if that's the pattern:


def recon_agent_node_logic(state: AgentState) -> AgentState:
    """Wrapper for analyze_site_with_ollama to be used as a LangGraph node."""
    site_name = state.target_site
    if not site_name:
        print("[Recon Agent Node] Error: target_site not found in state.")
        state.execution_status = "RECON_ERROR_NO_SITE"
        state.result_summary = "Reconnaissance failed: Target site not specified."
        state.is_final = True
        return state

    recon_data = analyze_site_with_ollama(site_name)

    state.recon_result = recon_data  # Pydantic model will handle dict assignment
    state.execution_status = "RECON_DONE"
    print(f"[Recon Agent Node] Reconnaissance complete for {site_name}.")
    return state


def recon_agent(state: AgentState) -> AgentState:
    print(f"[Recon] Target site: {state.target_site}")

    recon_data = {
        "requires_zip": (
            state.target_site in ["apple", "adidas"] if state.target_site else False
        ),
        "requires_name": True,
        "has_avs_check": True,
        "risk_score": 0.3,  # mock: ใช้ ML จริงในอนาคต
    }

    # Ensure recon_result is initialized if it's None
    if state.recon_result is None:  # Pydantic attribute access
        state.recon_result = {}  # Initialize as dict

    if isinstance(state.recon_result, dict):  # Check if it's a dict before update
        state.recon_result.update(recon_data)
    else:
        # Handle case where recon_result might not be a dict (e.g. if placeholder was overwritten by a non-dict type)
        # This should ideally not happen if AgentState is consistently a Pydantic model or our placeholder
        print(
            f"[Recon Agent] Warning: state.recon_result is not a dict, cannot update. Type: {type(state.recon_result)}"
        )
        # Attempt to merge if possible, or re-assign. For simplicity, re-assigning if it's not our Pydantic model.
        # This part depends on how strictly the Pydantic model handles attribute assignment of different types.
        # If AgentState is the Pydantic model, it should handle dict assignment to recon_result if defined correctly.
        # For now, let's assume it's a dict or can be updated.
        # A safer approach might be to re-create the field if types mismatch and it's not a Pydantic model
        # that can handle the update.
        # If state is the ActualAgentState (Pydantic), this should be fine:
        current_recon_result = state.recon_result or {}
        current_recon_result.update(recon_data)
        state.recon_result = current_recon_result

    state.execution_status = "RECON_OK"  # Pydantic attribute access
    return state
