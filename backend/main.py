"""
Main FastAPI Application
Entry point for the Customer Support Copilot backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import tickets, forecasting, agents
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Customer Support Copilot",
    description="AI-powered support assistant for faster ticket resolution",
    version="1.0.0"
)

# Configure CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets.router)
app.include_router(forecasting.router)
app.include_router(agents.router)


# ============================================================================
# Startup Event - Initialize Sample Data
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize sample agents on startup for testing/demo
    """
    from models.agent import Agent, AgentStatus
    
    # Create sample agents
    sample_agents = [
        Agent(
            agent_id="AGENT-001",
            name="Alice Johnson",
            email="alice@company.com",
            team="shipping_team",
            skills=["SHIPPING", "RETURNS", "PRODUCT_INQUIRY"],
            max_tickets_per_day=15,
            status=AgentStatus.ACTIVE,
            active=True,
            total_tickets_resolved=245,
            avg_resolution_time_minutes=12.5
        ),
        Agent(
            agent_id="AGENT-002",
            name="Bob Smith",
            email="bob@company.com",
            team="billing_team",
            skills=["BILLING", "REFUND", "PAYMENT_ISSUE"],
            max_tickets_per_day=20,
            status=AgentStatus.ACTIVE,
            active=True,
            total_tickets_resolved=312,
            avg_resolution_time_minutes=8.3
        ),
        Agent(
            agent_id="AGENT-003",
            name="Carol Martinez",
            email="carol@company.com",
            team="shipping_team",
            skills=["SHIPPING", "PRODUCT_INQUIRY", "TECHNICAL"],
            max_tickets_per_day=15,
            status=AgentStatus.ACTIVE,
            active=True,
            total_tickets_resolved=198,
            avg_resolution_time_minutes=15.2
        ),
        Agent(
            agent_id="AGENT-004",
            name="David Lee",
            email="david@company.com",
            team="technical_team",
            skills=["TECHNICAL", "PRODUCT_INQUIRY", "ACCOUNT_ACCESS"],
            max_tickets_per_day=12,
            status=AgentStatus.ACTIVE,
            active=True,
            total_tickets_resolved=156,
            avg_resolution_time_minutes=22.7
        ),
        Agent(
            agent_id="AGENT-005",
            name="Emma Wilson",
            email="emma@company.com",
            team="general_support",
            skills=["SHIPPING", "BILLING", "RETURNS", "PRODUCT_INQUIRY", "REFUND"],
            max_tickets_per_day=18,
            status=AgentStatus.ACTIVE,
            active=True,
            total_tickets_resolved=423,
            avg_resolution_time_minutes=10.1
        )
    ]
    
    # Add to agents database
    for agent in sample_agents:
        agents.agents_db[agent.agent_id] = agent
    
    print(f"\n{'='*60}")
    print(f"🚀 Customer Support Copilot - Backend Started")
    print(f"{'='*60}")
    print(f"✅ Initialized {len(sample_agents)} sample agents")
    print(f"📊 Teams: shipping_team, billing_team, technical_team, general_support")
    print(f"🌐 API Docs: http://localhost:8000/docs")
    print(f"{'='*60}\n")


@app.get("/")
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "status": "online",
        "service": "Customer Support Copilot",
        "version": "1.0.0",
        "endpoints": {
            "tickets": "/api/tickets",
            "agents": "/api/agents",
            "forecasting": "/api/forecast",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_count": len(agents.agents_db),
        "tickets_count": len(tickets.tickets_db)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
