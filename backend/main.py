"""Main FastAPI application for Customer Support Copilot.

This version performs heavy AI/KB initialization in a background thread so
Render can detect the bound port quickly and avoid scan timeouts.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from datetime import datetime
from .api import tickets, forecasting, agents

app = FastAPI(
    title="Customer Support Copilot",
    description="AI-powered support assistant for faster ticket resolution",
    version="1.0.0"
)

# Global services (wired after background init)
ai_service = None
kb_service = None
services_ready = False

# ------------------------- CORS CONFIG ------------------------------------
_default_local_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
raw_allowed = os.getenv("ALLOWED_ORIGINS") or os.getenv("FRONTEND_URL") or ""
parsed_allowed = [o.strip().rstrip("/") for o in raw_allowed.split(",") if o.strip()]
allow_origins = list({*(parsed_allowed), *(_default_local_origins)}) if parsed_allowed else _default_local_origins
allow_credentials = True if allow_origins and allow_origins != ["*"] else False
print(f"🛡️  CORS allow_origins: {allow_origins} | allow_credentials={allow_credentials}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(tickets.router)
app.include_router(forecasting.router)
app.include_router(agents.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Customer Support Copilot",
        "timestamp": datetime.now().isoformat(),
        "services_ready": services_ready
    }


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Customer Support Copilot",
        "version": "1.0.0",
        "services_ready": services_ready,
        "endpoints": {
            "tickets": "/api/tickets",
            "agents": "/api/agents",
            "forecasting": "/api/forecast",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Customer Support Copilot...")
    asyncio.create_task(_initialize_services_async())


async def _initialize_services_async():
    await asyncio.to_thread(_init_services_blocking)


def _init_services_blocking():
    global ai_service, kb_service, services_ready
    try:
        print("� Background initialization started...")
        from .services.ai_service import TicketAIService
        from .services.kb_service import KnowledgeBaseService
        from .models.agent import Agent, AgentStatus
        from .data.sample_kb_articles import SAMPLE_ARTICLES

        # AI Service
        try:
            ai_service = TicketAIService()
            print("✅ AI Service initialized")
        except Exception as e:
            print(f"⚠️  AI Service initialization failed: {e}")
            ai_service = None

        # KB Service
        try:
            kb_service = KnowledgeBaseService()
            print("✅ Knowledge Base Service initialized")
            if kb_service.collection.count() == 0:
                print("📚 Loading sample KB articles...")
                kb_service.add_articles_bulk(SAMPLE_ARTICLES)
        except Exception as e:
            print(f"⚠️  KB Service initialization failed: {e}")
            kb_service = None

        # Wire services for ticket processing
        tickets.ai_service = ai_service
        tickets.kb_service = kb_service

        # Sample agents
        sample_agents = [
            Agent(agent_id="AGENT-001", name="Alice Johnson", email="alice@company.com", team="shipping_team", skills=["SHIPPING", "RETURNS", "PRODUCT_INQUIRY"], max_tickets_per_day=15, status=AgentStatus.ACTIVE, active=True, total_tickets_resolved=245, avg_resolution_time_minutes=12.5),
            Agent(agent_id="AGENT-002", name="Bob Smith", email="bob@company.com", team="billing_team", skills=["BILLING", "REFUND", "PAYMENT_ISSUE"], max_tickets_per_day=20, status=AgentStatus.ACTIVE, active=True, total_tickets_resolved=312, avg_resolution_time_minutes=8.3),
            Agent(agent_id="AGENT-003", name="Carol Martinez", email="carol@company.com", team="shipping_team", skills=["SHIPPING", "PRODUCT_INQUIRY", "TECHNICAL"], max_tickets_per_day=15, status=AgentStatus.ACTIVE, active=True, total_tickets_resolved=198, avg_resolution_time_minutes=15.2),
            Agent(agent_id="AGENT-004", name="David Lee", email="david@company.com", team="technical_team", skills=["TECHNICAL", "PRODUCT_INQUIRY", "ACCOUNT_ACCESS"], max_tickets_per_day=12, status=AgentStatus.ACTIVE, active=True, total_tickets_resolved=156, avg_resolution_time_minutes=22.7),
            Agent(agent_id="AGENT-005", name="Emma Wilson", email="emma@company.com", team="general_support", skills=["SHIPPING", "BILLING", "RETURNS", "PRODUCT_INQUIRY", "REFUND"], max_tickets_per_day=18, status=AgentStatus.ACTIVE, active=True, total_tickets_resolved=423, avg_resolution_time_minutes=10.1)
        ]
        for a in sample_agents:
            agents.agents_db[a.agent_id] = a

        services_ready = True
        print("✅ Background initialization complete")
        print(f"✅ Loaded {len(sample_agents)} sample agents")
    except Exception as e:
        print(f"❌ Background init error: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)