import asyncio
from app.core.database import AsyncSessionLocal
from app.schemas.api import TaskApprovalRequest
from app.api.router import review_agent_task

async def test():
    async with AsyncSessionLocal() as db:
        payload = TaskApprovalRequest(approved=True, reviewer="fde_lead@enterprise.com", notes="Testing review")
        res = await review_agent_task("task-001", payload, db)
        print("REVIEW SUCCESS:", res)

if __name__ == "__main__":
    asyncio.run(test())
