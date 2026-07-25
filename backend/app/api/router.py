import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.core.database import get_db
from app.core.websockets import manager
from app.models.domain import (
    Organization, DataSource, IngestedRecord, ResolvedEntity,
    AgentWorkflowTask, AuditLog, TaskStatus
)
from app.schemas.api import (
    OrganizationRead, DataSourceRead, IngestedRecordRead,
    ResolvedEntityRead, AgentWorkflowTaskRead, TaskApprovalRequest,
    AuditLogRead, DashboardOverviewStats
)
from app.services.agent_engine import execute_approved_agent_tool

router = APIRouter(prefix="/api/v1")

@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NexusOps Enterprise Control Plane Backend",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/dashboard/stats", response_model=DashboardOverviewStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_orgs = await db.scalar(select(func.count(Organization.id))) or 0
    active_connectors = await db.scalar(select(func.count(DataSource.id))) or 0
    total_records = await db.scalar(select(func.count(IngestedRecord.id))) or 0
    total_entities = await db.scalar(select(func.count(ResolvedEntity.id))) or 0
    pending_tasks = await db.scalar(select(func.count(AgentWorkflowTask.id)).where(AgentWorkflowTask.status == TaskStatus.AWAITING_APPROVAL)) or 0
    executed_tasks = await db.scalar(select(func.count(AgentWorkflowTask.id)).where(AgentWorkflowTask.status == TaskStatus.EXECUTED)) or 0

    return DashboardOverviewStats(
        total_organizations=total_orgs,
        active_connectors=active_connectors,
        total_records_ingested=total_records,
        resolved_entities_count=total_entities,
        pending_approvals_count=pending_tasks,
        executed_tasks_count=executed_tasks
    )

@router.get("/organizations", response_model=List[OrganizationRead])
async def list_organizations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization))
    return result.scalars().all()

@router.get("/connectors", response_model=List[DataSourceRead])
async def list_data_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DataSource))
    return result.scalars().all()

@router.get("/records", response_model=List[IngestedRecordRead])
async def list_ingested_records(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IngestedRecord).limit(limit))
    return result.scalars().all()

@router.get("/entities", response_model=List[ResolvedEntityRead])
async def list_resolved_entities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResolvedEntity))
    return result.scalars().all()

@router.get("/agent/tasks", response_model=List[AgentWorkflowTaskRead])
async def list_agent_tasks(status: TaskStatus = None, db: AsyncSession = Depends(get_db)):
    query = select(AgentWorkflowTask)
    if status:
        query = query.where(AgentWorkflowTask.status == status)
    result = await db.execute(query.order_by(AgentWorkflowTask.created_at.desc()))
    return result.scalars().all()

@router.post("/agent/tasks/{task_id}/review", response_model=AgentWorkflowTaskRead)
async def review_agent_task(
    task_id: str,
    payload: TaskApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    # Query explicit database columns directly
    stmt = select(
        AgentWorkflowTask.id,
        AgentWorkflowTask.resolved_entity_id,
        AgentWorkflowTask.title,
        AgentWorkflowTask.description,
        AgentWorkflowTask.priority,
        AgentWorkflowTask.status,
        AgentWorkflowTask.proposed_tool_name,
        AgentWorkflowTask.proposed_tool_args_str,
        AgentWorkflowTask.ai_confidence_score,
        AgentWorkflowTask.ai_reasoning,
        AgentWorkflowTask.requires_human_approval,
        AgentWorkflowTask.created_at
    ).where(AgentWorkflowTask.id == task_id)

    res = await db.execute(stmt)
    row = res.first()

    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    (
        t_id, resolved_entity_id, title, description, priority,
        current_status, tool_name, tool_args_str, confidence, reasoning,
        requires_approval, created_at
    ) = row

    tool_args = json.loads(tool_args_str) if tool_args_str else {}
    new_status = TaskStatus.EXECUTED if payload.approved else TaskStatus.REJECTED

    if payload.approved:
        exec_result = await execute_approved_agent_tool(tool_name, tool_args)
        audit_action = "HUMAN_APPROVED_AND_EXECUTED_TOOL"
        audit_details = {
            "task_id": task_id,
            "tool_name": tool_name,
            "execution_result": exec_result,
            "notes": payload.notes
        }
    else:
        audit_action = "HUMAN_REJECTED_AGENT_PROPOSAL"
        audit_details = {
            "task_id": task_id,
            "tool_name": tool_name,
            "notes": payload.notes
        }

    # Execute direct update query
    upd_stmt = (
        update(AgentWorkflowTask)
        .where(AgentWorkflowTask.id == task_id)
        .values(
            status=new_status,
            approved_by=payload.reviewer,
            approval_notes=payload.notes
        )
    )
    await db.execute(upd_stmt)

    # Insert audit log
    audit = AuditLog(
        organization_id="org-acme-corp",
        actor=payload.reviewer,
        action=audit_action,
        details=audit_details
    )
    db.add(audit)
    await db.commit()

    return AgentWorkflowTaskRead(
        id=t_id,
        resolved_entity_id=resolved_entity_id,
        title=title,
        description=description,
        priority=priority,
        status=new_status,
        proposed_tool_name=tool_name,
        proposed_tool_args=tool_args,
        ai_confidence_score=confidence,
        ai_reasoning=reasoning,
        requires_human_approval=requires_approval,
        approved_by=payload.reviewer,
        approval_notes=payload.notes,
        created_at=created_at
    )

@router.get("/audit-logs", response_model=List[AuditLogRead])
async def list_audit_logs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit))
    return result.scalars().all()
