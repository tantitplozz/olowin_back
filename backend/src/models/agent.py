from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Status of an agent"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


class AgentType(str, Enum):
    """Type of an agent"""
    LLM = "llm"
    RETRIEVER = "retriever"
    CLASSIFIER = "classifier"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    CUSTOM = "custom"


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    model_name: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = []
    additional_params: Dict[str, Any] = {}


class AgentBase(BaseModel):
    """Base agent model with common fields"""
    name: str
    description: str
    type: AgentType
    config: AgentConfig
    is_active: bool = True


class AgentCreate(AgentBase):
    """Model for creating an agent"""
    pass


class AgentUpdate(BaseModel):
    """Model for updating an agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AgentType] = None
    config: Optional[AgentConfig] = None
    is_active: Optional[bool] = None


class AgentInDB(AgentBase):
    """Agent model as stored in the database"""
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: AgentStatus = AgentStatus.IDLE
    last_used: Optional[datetime] = None
    usage_count: int = 0
    success_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "60d6ec9f7c213e1a1c9c1e1c",
                "name": "Text Summarizer",
                "description": "Summarizes text documents",
                "type": "llm",
                "config": {
                    "model_name": "llama3",
                    "temperature": 0.5,
                    "max_tokens": 512
                },
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "status": "idle",
                "last_used": "2023-01-01T00:00:00",
                "usage_count": 100,
                "success_count": 95,
                "error_count": 5,
                "average_response_time": 1.2
            }
        }


class Agent(AgentBase):
    """Agent model returned to clients"""
    id: str
    created_at: datetime
    updated_at: datetime
    status: AgentStatus
    last_used: Optional[datetime] = None
    usage_count: int
    success_count: int
    error_count: int
    average_response_time: float

    class Config:
        json_schema_extra = {
            "example": {
                "id": "60d6ec9f7c213e1a1c9c1e1c",
                "name": "Text Summarizer",
                "description": "Summarizes text documents",
                "type": "llm",
                "config": {
                    "model_name": "llama3",
                    "temperature": 0.5,
                    "max_tokens": 512
                },
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "status": "idle",
                "last_used": "2023-01-01T00:00:00",
                "usage_count": 100,
                "success_count": 95,
                "error_count": 5,
                "average_response_time": 1.2
            }
        }


class AgentExecution(BaseModel):
    """Model for agent execution logs"""
    id: str = Field(alias="_id")
    agent_id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True 