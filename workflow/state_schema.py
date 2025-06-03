# workflow/state_schema.py - Defines the structure of Task and AgentState for LangGraph
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class AgentState(BaseModel):
    target_site: Optional[str] = None
    card_info: Optional[Dict[str, Any]] = None
    recon_result: Optional[Dict[str, Any]] = None
    execution_status: Optional[str] = None
    attempt_count: Optional[int] = Field(default=0)  # Ensure default for Pydantic model
    result_summary: Optional[str] = None
    is_final: Optional[bool] = Field(default=False)  # Ensure default for Pydantic model
    task_id: Optional[str] = None  # Added task_id for better state tracking
    risk_score: Optional[int] = None  # For risk_assessor_agent
    risk_level: Optional[str] = None  # For risk_assessor_agent

    # If using Pydantic v2, model_config can be used for arbitrary types
    # class Config:
    #     arbitrary_types_allowed = True

    # Potentially other fields like error_message, otp_details, etc.

    @validator("target_site", pre=True, always=True)
    def validate_target_site(cls, value):
        if value is not None and not value.startswith(("http://", "https://")):
            # Attempt to prepend https:// if no scheme is present
            if "://" not in value:
                value = "https://" + value
            else:
                raise ValueError("target_site must be a valid http or https URL")
        # Could add more sophisticated URL validation here if needed
        return value
