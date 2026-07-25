from typing import Any, Dict
from app.models.domain import TaskStatus, TaskPriority

HIGH_RISK_TOOLS = {"issue_refund", "delete_customer_account", "downgrade_sla", "override_contract"}

def evaluate_agent_action_risk(tool_name: str, tool_args: Dict[str, Any], ai_confidence: float) -> bool:
    """
    Determine if an agent action requires Human-in-the-Loop approval.
    High-risk tools OR low confidence scores (>0.75 threshold requirement) require human review.
    """
    if tool_name in HIGH_RISK_TOOLS:
        return True
    if ai_confidence < 0.85:
        return True
    return False

async def execute_approved_agent_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate execution of an enterprise integration tool (e.g. updating CRM, issuing API refund, updating Jira).
    """
    if tool_name == "issue_refund":
        amount = tool_args.get("amount", 0)
        customer = tool_args.get("customer_name", "Client")
        return {
            "success": True,
            "message": f"Successfully issued credit refund of ${amount} to account '{customer}'.",
            "receipt_id": f"REF-{tool_args.get('ticket_id', '9999')}"
        }
    elif tool_name == "escalate_jira_ticket":
        issue_key = tool_args.get("jira_key", "ENG-101")
        return {
            "success": True,
            "message": f"Escalated ticket {issue_key} to P0 Critical engineering priority.",
            "updated_assignee": "Lead On-Call Engineer"
        }
    elif tool_name == "update_crm_tier":
        new_tier = tool_args.get("tier", "Enterprise VIP")
        return {
            "success": True,
            "message": f"Updated customer contract tier to '{new_tier}' in HubSpot CRM.",
            "synced_systems": ["HubSpot", "Zendesk", "BillingDB"]
        }
    else:
        return {
            "success": True,
            "message": f"Executed custom tool '{tool_name}' successfully.",
            "args_processed": tool_args
        }
