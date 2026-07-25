import enum
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ConnectorType(str, enum.Enum):
    ZENDESK = "ZENDESK"
    HUBSPOT = "HUBSPOT"
    JIRA = "JIRA"
    POSTGRESQL = "POSTGRESQL"
    CUSTOM_REST = "CUSTOM_REST"

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    data_sources: Mapped[list["DataSource"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    entities: Mapped[list["ResolvedEntity"]] = relationship(back_populates="organization", cascade="all, delete-orphan")

class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    connector_type: Mapped[ConnectorType] = mapped_column(SQLEnum(ConnectorType), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    records_count: Mapped[int] = mapped_column(default=0)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="data_sources")
    records: Mapped[list["IngestedRecord"]] = relationship(back_populates="data_source", cascade="all, delete-orphan")

class IngestedRecord(Base):
    __tablename__ = "ingested_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. ticket, crm_contact, bug_report
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    normalized_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    data_source: Mapped["DataSource"] = relationship(back_populates="records")
    resolved_entity_id: Mapped[Optional[str]] = mapped_column(ForeignKey("resolved_entities.id"), nullable=True)
    resolved_entity: Mapped[Optional["ResolvedEntity"]] = relationship(back_populates="raw_records")

class ResolvedEntity(Base):
    __tablename__ = "resolved_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    primary_name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(100), default="CUSTOMER_ACCOUNT")
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    match_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="entities")
    raw_records: Mapped[list["IngestedRecord"]] = relationship(back_populates="resolved_entity")
    workflow_tasks: Mapped[list["AgentWorkflowTask"]] = relationship(back_populates="resolved_entity")

class AgentWorkflowTask(Base):
    __tablename__ = "agent_workflow_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resolved_entity_id: Mapped[str] = mapped_column(ForeignKey("resolved_entities.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.AWAITING_APPROVAL)
    
    proposed_tool_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "issue_refund", "escalate_jira_ticket"
    proposed_tool_args: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ai_confidence_score: Mapped[float] = mapped_column(Float, default=0.88)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resolved_entity: Mapped["ResolvedEntity"] = relationship(back_populates="workflow_tasks")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. "AI_AGENT", "fde_admin@enterprise.com"
    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "ENTITY_FUSED", "TASK_APPROVED", "TOOL_EXECUTED"
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
