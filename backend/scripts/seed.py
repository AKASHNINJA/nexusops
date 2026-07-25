import asyncio
from datetime import datetime
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.domain import (
    Organization, DataSource, IngestedRecord, ResolvedEntity,
    AgentWorkflowTask, AuditLog, ConnectorType, TaskPriority, TaskStatus
)

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Organization
        org = Organization(
            id="org-acme-corp",
            name="Apex Financial Systems",
            slug="apex-financial"
        )
        session.add(org)

        # 2. Data Sources
        ds_zendesk = DataSource(
            id="ds-zendesk-01",
            organization_id=org.id,
            name="Zendesk Support Tickets Stream",
            connector_type=ConnectorType.ZENDESK,
            status="ACTIVE",
            records_count=1420,
            last_synced_at=datetime.utcnow()
        )
        ds_hubspot = DataSource(
            id="ds-hubspot-02",
            organization_id=org.id,
            name="HubSpot CRM Accounts",
            connector_type=ConnectorType.HUBSPOT,
            status="ACTIVE",
            records_count=850,
            last_synced_at=datetime.utcnow()
        )
        ds_jira = DataSource(
            id="ds-jira-03",
            organization_id=org.id,
            name="Jira Engineering Projects",
            connector_type=ConnectorType.JIRA,
            status="ACTIVE",
            records_count=610,
            last_synced_at=datetime.utcnow()
        )
        session.add_all([ds_zendesk, ds_hubspot, ds_jira])

        # 3. Resolved Entities (Merged Enterprise Customers)
        entity_acme = ResolvedEntity(
            id="ent-acme-001",
            organization_id=org.id,
            primary_name="Acme Global Logistics Inc",
            domain="acmeglobal.com",
            entity_type="ENTERPRISE_CLIENT",
            attributes={
                "annual_contract_value": "$450,000",
                "tier": "Platinum Enterprise",
                "health_score": "AMBER (SLA Breach Risk)"
            },
            match_confidence=0.98
        )
        entity_apex = ResolvedEntity(
            id="ent-apex-002",
            organization_id=org.id,
            primary_name="Apex Dynamics Technologies",
            domain="apexdynamics.io",
            entity_type="ENTERPRISE_CLIENT",
            attributes={
                "annual_contract_value": "$1,200,000",
                "tier": "Diamond VIP",
                "health_score": "HEALTHY"
            },
            match_confidence=0.95
        )
        session.add_all([entity_acme, entity_apex])

        # 4. Ingested Records
        rec_zd = IngestedRecord(
            id="rec-zd-9912",
            data_source_id=ds_zendesk.id,
            external_id="ZD-TICKET-9912",
            entity_type="SUPPORT_TICKET",
            raw_payload={"subject": "P0 Outage: API Gateway 504 Gateway Timeout", "requester": "sarah.connor@acmeglobal.com"},
            normalized_data={"company_name": "ACME Global", "domain": "acmeglobal.com", "severity": "CRITICAL"},
            resolved_entity_id=entity_acme.id
        )
        rec_hs = IngestedRecord(
            id="rec-hs-4401",
            data_source_id=ds_hubspot.id,
            external_id="HS-COMPANY-4401",
            entity_type="CRM_ACCOUNT",
            raw_payload={"name": "Acme Global Logistics, Inc.", "arr": 450000},
            normalized_data={"company_name": "Acme Global Logistics Inc", "domain": "acmeglobal.com"},
            resolved_entity_id=entity_acme.id
        )
        session.add_all([rec_zd, rec_hs])

        # 5. AI Agent Workflow Tasks (HITL Queue)
        task_refund = AgentWorkflowTask(
            id="task-001",
            resolved_entity_id=entity_acme.id,
            title="SLA Breach Compensation: Issue Credit Refund",
            description="Zendesk ticket ZD-9912 exceeded the Platinum SLA resolution threshold by 3.5 hours due to DB latency. AI Agent recommends issuing a $2,500 billing credit per contract terms.",
            priority=TaskPriority.HIGH,
            status=TaskStatus.AWAITING_APPROVAL,
            proposed_tool_name="issue_refund",
            proposed_tool_args={"amount": 2500, "customer_name": "Acme Global Logistics Inc", "ticket_id": "ZD-9912"},
            ai_confidence_score=0.92,
            ai_reasoning="Calculated SLA breach time = 210 mins. Contract clause #14.2 requires 5% credit ($2,500). Action tagged as high risk due to financial payout.",
            requires_human_approval=True
        )
        task_jira = AgentWorkflowTask(
            id="task-002",
            resolved_entity_id=entity_apex.id,
            title="Escalate Engineering Bug to P0 Priority",
            description="Apex Dynamics reported recurring authentication token revocation issue affecting 1,200 active users.",
            priority=TaskPriority.CRITICAL,
            status=TaskStatus.AWAITING_APPROVAL,
            proposed_tool_name="escalate_jira_ticket",
            proposed_tool_args={"jira_key": "ENG-4892", "customer_name": "Apex Dynamics Technologies"},
            ai_confidence_score=0.88,
            ai_reasoning="Customer ARR > $1M with >1,000 users impacted. Automated policy requires P0 escalation.",
            requires_human_approval=True
        )
        session.add_all([task_refund, task_jira])

        # 6. Initial Audit Logs
        audit_1 = AuditLog(
            organization_id=org.id,
            actor="ENTITY_RESOLUTION_ENGINE",
            action="FUZZY_MATCH_ENTITY_FUSED",
            details={
                "entity_name": "Acme Global Logistics Inc",
                "matched_sources": ["Zendesk", "HubSpot"],
                "confidence": 0.98
            }
        )
        session.add(audit_1)

        await session.commit()
        print("Database successfully seeded with enterprise FDE datasets!")

if __name__ == "__main__":
    asyncio.run(seed_data())
