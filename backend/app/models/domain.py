import enum
import json
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, Boolean, Enum as SQLEnum
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

    data_sources: Mapped[list["DataSource"]] = relationship(back_populates="organization", cascade="all, delete-orphan", lazy="selectin")
    entities: Mapped[list["ResolvedEntity"]] = relationship(back_populates="organization", cascade="all, delete-orphan", lazy="selectin")

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

    organization: Mapped["Organization"] = relationship(back_populates="data_sources", lazy="selectin")
    records: Mapped[list["IngestedRecord"]] = relationship(back_populates="data_source", cascade="all, delete-orphan", lazy="selectin")

class IngestedRecord(Base):
    __tablename__ = "ingested_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_payload_str: Mapped[str] = mapped_column(Text, default="{}")
    normalized_data_str: Mapped[str] = mapped_column(Text, default="{}")
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    data_source: Mapped["DataSource"] = relationship(back_populates="records", lazy="selectin")
    resolved_entity_id: Mapped[Optional[str]] = mapped_column(ForeignKey("resolved_entities.id"), nullable=True)
    resolved_entity: Mapped[Optional["ResolvedEntity"]] = relationship(back_populates="raw_records", lazy="selectin")

    @property
    def raw_payload(self) -> dict:
        return json.loads(self.raw_payload_str) if self.raw_payload_str else {}

    @raw_payload.setter
    def raw_payload(self, val: dict):
        self.raw_payload_str = json.dumps(val)

    @property
    def normalized_data(self) -> dict:
        return json.loads(self.normalized_data_str) if self.normalized_data_str else {}

    @normalized_data.setter
    def normalized_data(self, val: dict):
        self.normalized_data_str = json.dumps(val)

class ResolvedEntity(Base):
    __tablename__ = "resolved_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    primary_name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(100), default="CUSTOMER_ACCOUNT")
    attributes_str: Mapped[str] = mapped_column(Text, default="{}")
    match_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="entities", lazy="selectin")
    raw_records: Mapped[list["IngestedRecord"]] = relationship(back_populates="resolved_entity", lazy="selectin")
    workflow_tasks: Mapped[list["AgentWorkflowTask"]] = relationship(back_populates="resolved_entity", lazy="selectin")

    @property
    def attributes(self) -> dict:
        return json.loads(self.attributes_str) if self.attributes_str else {}

    @attributes.setter
    def attributes(self, val: dict):
        self.attributes_str = json.dumps(val)

class AgentWorkflowTask(Base):
    __tablename__ = "agent_workflow_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resolved_entity_id: Mapped[str] = mapped_column(ForeignKey("resolved_entities.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.AWAITING_APPROVAL)
    
    proposed_tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    proposed_tool_args_str: Mapped[str] = mapped_column(Text, default="{}")
    ai_confidence_score: Mapped[float] = mapped_column(Float, default=0.88)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resolved_entity: Mapped["ResolvedEntity"] = relationship(back_populates="workflow_tasks", lazy="selectin")

    @property
    def proposed_tool_args(self) -> dict:
        return json.loads(self.proposed_tool_args_str) if self.proposed_tool_args_str else {}

    @proposed_tool_args.setter
    def proposed_tool_args(self, val: dict):
        self.proposed_tool_args_str = json.dumps(val)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details_str: Mapped[str] = mapped_column(Text, default="{}")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def details(self) -> dict:
        return json.loads(self.details_str) if self.details_str else {}

    @details.setter
    def details(self, val: dict):
        self.details_str = json.dumps(val)
