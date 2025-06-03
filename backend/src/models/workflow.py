from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, root_validator

from .agent import AgentType


class NodeType(str, Enum):
    """Type of a workflow node"""
    AGENT = "agent"
    CONDITION = "condition"
    INPUT = "input"
    OUTPUT = "output"
    TRANSFORMATION = "transformation"


class EdgeType(str, Enum):
    """Type of a workflow edge"""
    SUCCESS = "success"
    ERROR = "error"
    DEFAULT = "default"
    CONDITIONAL = "conditional"


class WorkflowStatus(str, Enum):
    """Status of a workflow"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class WorkflowExecutionStatus(str, Enum):
    """Status of a workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class NodeConfig(BaseModel):
    """Configuration for a workflow node"""
    agent_id: Optional[str] = None
    agent_type: Optional[AgentType] = None
    condition: Optional[Dict[str, Any]] = None
    transformation_code: Optional[str] = None
    input_mapping: Dict[str, str] = {}
    output_mapping: Dict[str, str] = {}
    retry_config: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 60


class Node(BaseModel):
    """A node in a workflow"""
    id: str
    name: str
    type: NodeType
    config: NodeConfig
    position: Dict[str, float]


class Edge(BaseModel):
    """An edge connecting nodes in a workflow"""
    id: str
    source_id: str
    target_id: str
    type: EdgeType = EdgeType.DEFAULT
    condition: Optional[Dict[str, Any]] = None


class WorkflowBase(BaseModel):
    """Base workflow model with common fields"""
    name: str
    description: str
    version: str = "1.0.0"
    nodes: List[Node]
    edges: List[Edge]
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}


class WorkflowCreate(WorkflowBase):
    """Model for creating a workflow"""
    pass


class WorkflowUpdate(BaseModel):
    """Model for updating a workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    nodes: Optional[List[Node]] = None
    edges: Optional[List[Edge]] = None
    status: Optional[WorkflowStatus] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class WorkflowInDB(WorkflowBase):
    """Workflow model as stored in the database"""
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    status: WorkflowStatus = WorkflowStatus.DRAFT
    tags: List[str] = []
    execution_count: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0

    class Config:
        populate_by_name = True


class Workflow(WorkflowBase):
    """Workflow model returned to clients"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    status: WorkflowStatus
    tags: List[str]
    execution_count: int
    average_execution_time: float
    success_rate: float


class NodeExecution(BaseModel):
    """Execution details for a single node in a workflow execution"""
    node_id: str
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


class WorkflowExecution(BaseModel):
    """Model for workflow execution logs"""
    id: str = Field(alias="_id")
    workflow_id: str
    status: WorkflowExecutionStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    node_executions: Dict[str, NodeExecution] = {}
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    triggered_by: str
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True 