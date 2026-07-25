from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from app.models.domain import TaskStatus, TaskPriority, ConnectorType

class OrganizationRead(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DataSourceRead(BaseModel):
    id: str
    organization_id: str
    name: str
    connector_type: ConnectorType
    status: str
    records_count: int
    last_synced_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IngestedRecordRead(BaseModel):
    id: str
    data_source_id: str
    external_id: str
    entity_type: str
    raw_payload: dict[str, Any]
    normalized_data: dict[str, Any]
    ingested_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResolvedEntityRead(BaseModel):
    id: str
    organization_id: str
    primary_name: str
    domain: Optional[str]
    entity_type: str
    attributes: dict[str, Any]
    match_confidence: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AgentWorkflowTaskRead(BaseModel):
    id: str
    resolved_entity_id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    proposed_tool_name: str
    proposed_tool_args: dict[str, Any]
    ai_confidence_score: float
    ai_reasoning: str
    requires_human_approval: bool
    approved_by: Optional[str]
    approval_notes: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskApprovalRequest(BaseModel):
    approved: bool
    reviewer: str = "fde_lead@enterprise.com"
    notes: Optional[str] = None

class AuditLogRead(BaseModel):
    id: str
    organization_id: str
    actor: str
    action: str
    details: dict[str, Any]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class DashboardOverviewStats(BaseModel):
    total_organizations: int
    active_connectors: int
    total_records_ingested: int
    resolved_entities_count: int
    pending_approvals_count: int
    executed_tasks_count: int
