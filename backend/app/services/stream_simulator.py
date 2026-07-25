import asyncio
import random
import uuid
from datetime import datetime
from app.core.websockets import manager

SAMPLE_TICKETS = [
    {
        "company": "Vortex Heavy Industries",
        "domain": "vortexind.com",
        "subject": "API Rate Limit Exceeded on Batch Export",
        "arr": "$890,000",
        "tier": "Enterprise Gold",
        "tool": "adjust_rate_limit",
        "tool_args": {"company_name": "Vortex Heavy Industries", "new_limit": 10000},
        "reasoning": "Batch export job blocked due to legacy rate limit cap (5,000 req/min). Enterprise contract allows up to 20,000 req/min.",
        "confidence": 0.91,
        "priority": "HIGH"
    },
    {
        "company": "Cyberdyne Systems Corp",
        "domain": "cyberdyne.io",
        "subject": "Database Latency Spike in EU Region",
        "arr": "$2,400,000",
        "tier": "Diamond VIP",
        "tool": "escalate_jira_ticket",
        "tool_args": {"jira_key": "EU-7719", "customer_name": "Cyberdyne Systems Corp"},
        "reasoning": "EU-Central database replica lagging by 4.2 seconds. Affected account ARR > $2M. Auto-escalating to Tier-3 Infrastructure Engineering.",
        "confidence": 0.94,
        "priority": "CRITICAL"
    },
    {
        "company": "Acme Global Logistics Inc",
        "domain": "acmeglobal.com",
        "subject": "Billing Discrepancy on Ingestion Storage",
        "arr": "$450,000",
        "tier": "Platinum Enterprise",
        "tool": "issue_refund",
        "tool_args": {"amount": 1200, "customer_name": "Acme Global Logistics Inc", "ticket_id": "ZD-10492"},
        "reasoning": "Duplicate ingestion storage charge detected on May billing cycle. Recommending $1,200 automated credit adjustment.",
        "confidence": 0.89,
        "priority": "MEDIUM"
    }
]

async def start_live_stream_simulator():
    """Background simulator task generating real-time customer data streams and AI tasks."""
    print("🚀 Live Ingestion Stream Simulator started...")
    idx = 0
    while True:
        await asyncio.sleep(12)  # Emit event every 12 seconds
        sample = SAMPLE_TICKETS[idx % len(SAMPLE_TICKETS)]
        idx += 1

        record_id = f"rec-sim-{uuid.uuid4().hex[:6]}"
        task_id = f"task-sim-{uuid.uuid4().hex[:6]}"
        timestamp = datetime.utcnow().isoformat()

        # 1. Broadcast Ingestion Event
        ingestion_data = {
            "id": record_id,
            "external_id": f"ZD-LIVE-{random.randint(1000, 9999)}",
            "source": "Zendesk Support Stream",
            "company_name": sample["company"],
            "domain": sample["domain"],
            "subject": sample["subject"],
            "timestamp": timestamp
        }
        await manager.broadcast("RECORD_INGESTED", ingestion_data)

        await asyncio.sleep(1)

        # 2. Broadcast AI Agent HITL Task Event
        ai_task_data = {
            "id": task_id,
            "resolved_entity_id": f"ent-{sample['domain'].split('.')[0]}",
            "title": f"AI Action: {sample['subject']}",
            "description": f"Automated analysis for {sample['company']}: {sample['reasoning']}",
            "priority": sample["priority"],
            "status": "AWAITING_APPROVAL",
            "proposed_tool_name": sample["tool"],
            "proposed_tool_args": sample["tool_args"],
            "ai_confidence_score": sample["confidence"],
            "ai_reasoning": sample["reasoning"],
            "requires_human_approval": True,
            "created_at": timestamp
        }
        await manager.broadcast("AGENT_TASK_CREATED", ai_task_data)

        # 3. Broadcast Audit Log Event
        audit_data = {
            "id": f"aud-sim-{uuid.uuid4().hex[:6]}",
            "actor": "LIVE_STREAM_SIMULATOR",
            "action": "REALTIME_RECORD_INGESTED_AND_EVALUATED",
            "details": {
                "company": sample["company"],
                "subject": sample["subject"],
                "ai_confidence": sample["confidence"]
            },
            "timestamp": timestamp
        }
        await manager.broadcast("AUDIT_LOG_ADDED", audit_data)
