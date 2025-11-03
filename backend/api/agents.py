"""
Agent Management API

CRUD operations and agent management endpoints for customer support agents.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.agent import (
    Agent, 
    AgentCreate, 
    AgentUpdate, 
    AgentStats, 
    AgentStatus,
    AgentAssignmentResponse
)
from models.ticket import TicketCategory

router = APIRouter(prefix="/api/agents", tags=["agents"])

# In-memory agent storage (replace with database in production)
agents_db: Dict[str, Agent] = {}


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("/", response_model=Agent, status_code=201)
async def create_agent(agent_data: AgentCreate):
    """
    Create a new support agent
    
    - **agent_id**: Unique identifier (e.g., AGENT-001)
    - **name**: Agent's full name
    - **email**: Contact email
    - **team**: Team name (optional)
    - **skills**: List of expertise areas (optional)
    - **max_tickets_per_day**: Capacity limit (default: 15)
    """
    if agent_data.agent_id in agents_db:
        raise HTTPException(
            status_code=400,
            detail=f"Agent with ID {agent_data.agent_id} already exists"
        )
    
    agent = Agent(
        agent_id=agent_data.agent_id,
        name=agent_data.name,
        email=agent_data.email,
        team=agent_data.team,
        skills=agent_data.skills,
        max_tickets_per_day=agent_data.max_tickets_per_day,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    
    agents_db[agent.agent_id] = agent
    return agent


@router.get("/", response_model=List[Agent])
async def list_agents(
    team: Optional[str] = Query(None, description="Filter by team"),
    status: Optional[AgentStatus] = Query(None, description="Filter by status"),
    active_only: bool = Query(True, description="Show only active agents")
):
    """
    List all agents with optional filtering
    
    - **team**: Filter by team name
    - **status**: Filter by agent status (active/away/offline)
    - **active_only**: Only show active agents (default: true)
    """
    agents = list(agents_db.values())
    
    # Apply filters
    if active_only:
        agents = [a for a in agents if a.active]
    
    if team:
        agents = [a for a in agents if a.team == team]
    
    if status:
        agents = [a for a in agents if a.status == status]
    
    return agents


@router.get("/stats", response_model=List[AgentStats])
async def get_agent_statistics(team: Optional[str] = None):
    """
    Get performance statistics for all agents
    
    Returns utilization, capacity, and performance metrics
    """
    agents = list(agents_db.values())
    
    if team:
        agents = [a for a in agents if a.team == team]
    
    stats = []
    for agent in agents:
        utilization = (agent.current_load / agent.max_tickets_per_day * 100) if agent.max_tickets_per_day > 0 else 0
        available_capacity = max(0, agent.max_tickets_per_day - agent.current_load)
        is_available = agent.active and agent.status == AgentStatus.ACTIVE and available_capacity > 0
        
        stats.append(AgentStats(
            agent_id=agent.agent_id,
            name=agent.name,
            current_load=agent.current_load,
            max_tickets_per_day=agent.max_tickets_per_day,
            utilization_percentage=round(utilization, 2),
            available_capacity=available_capacity,
            is_available=is_available,
            total_tickets_resolved=agent.total_tickets_resolved,
            avg_resolution_time_minutes=agent.avg_resolution_time_minutes,
            status=agent.status
        ))
    
    # Sort by availability (available first) then by lowest load
    stats.sort(key=lambda x: (not x.is_available, x.current_load))
    
    return stats


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """
    Get details for a specific agent
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    return agents_db[agent_id]


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, update_data: AgentUpdate):
    """
    Update agent details
    
    Can update: name, email, team, skills, max_tickets_per_day, status, active
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    agent = agents_db[agent_id]
    
    # Update fields if provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(agent, field, value)
    
    agent.last_active = datetime.utcnow()
    
    return agent


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, permanent: bool = Query(False, description="Permanently delete (vs deactivate)")):
    """
    Delete or deactivate an agent
    
    - **permanent=False**: Deactivates agent (default, safe)
    - **permanent=True**: Permanently removes from system
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    if permanent:
        del agents_db[agent_id]
        return {"message": f"Agent {agent_id} permanently deleted"}
    else:
        agents_db[agent_id].active = False
        agents_db[agent_id].status = AgentStatus.OFFLINE
        return {"message": f"Agent {agent_id} deactivated"}


# ============================================================================
# Agent Availability & Assignment
# ============================================================================

@router.get("/available/by-skill")
async def get_available_agents_by_skill(
    skill: str = Query(..., description="Required skill (e.g., SHIPPING, BILLING)")
):
    """
    Find available agents with a specific skill
    
    Returns agents who:
    - Are active
    - Have the required skill
    - Have available capacity
    - Are in ACTIVE status
    
    Sorted by current load (least busy first)
    """
    available_agents = []
    
    for agent in agents_db.values():
        has_capacity = agent.current_load < agent.max_tickets_per_day
        has_skill = skill.upper() in [s.upper() for s in agent.skills]
        is_working = agent.active and agent.status == AgentStatus.ACTIVE
        
        if has_skill and has_capacity and is_working:
            available_agents.append({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "team": agent.team,
                "current_load": agent.current_load,
                "max_tickets_per_day": agent.max_tickets_per_day,
                "available_capacity": agent.max_tickets_per_day - agent.current_load,
                "skills": agent.skills
            })
    
    # Sort by load (least busy first)
    available_agents.sort(key=lambda x: x["current_load"])
    
    return {
        "skill": skill,
        "available_count": len(available_agents),
        "agents": available_agents
    }


@router.post("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: AgentStatus = Query(..., description="New status (active/away/offline)")
):
    """
    Update agent's availability status
    
    - **active**: Available for assignments
    - **away**: Temporarily unavailable
    - **offline**: Not working
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    agent = agents_db[agent_id]
    agent.status = status
    agent.last_active = datetime.utcnow()
    
    # If going offline, deactivate
    if status == AgentStatus.OFFLINE:
        agent.active = False
    
    return {
        "agent_id": agent_id,
        "name": agent.name,
        "status": status,
        "message": f"Agent status updated to {status}"
    }


# ============================================================================
# Helper Functions (used by tickets API)
# ============================================================================

def find_best_agent_for_ticket(category: Optional[TicketCategory], priority: Optional[str] = None) -> Optional[Agent]:
    """
    Find the best available agent for a ticket
    
    Logic:
    1. Find agents with matching skill (category)
    2. Filter for active agents with capacity
    3. If priority is CRITICAL, prefer agents with lower load
    4. Return agent with lowest current load
    
    Returns None if no suitable agent found
    """
    category_str = category.value if category else None
    
    # Find qualified agents
    qualified_agents = []
    
    for agent in agents_db.values():
        # Must be active and have capacity
        if not agent.active or agent.status != AgentStatus.ACTIVE:
            continue
        
        if agent.current_load >= agent.max_tickets_per_day:
            continue
        
        # Check skill match
        if category_str:
            has_skill = category_str.upper() in [s.upper() for s in agent.skills]
            if not has_skill:
                continue
        
        qualified_agents.append(agent)
    
    if not qualified_agents:
        return None
    
    # Sort by current load (least busy first)
    qualified_agents.sort(key=lambda a: a.current_load)
    
    return qualified_agents[0]


def assign_ticket_to_agent(agent_id: str, ticket_id: str) -> Agent:
    """
    Increment agent's current load when ticket is assigned
    
    Called from tickets API when assigning a ticket
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    agent = agents_db[agent_id]
    
    if agent.current_load >= agent.max_tickets_per_day:
        raise HTTPException(
            status_code=400,
            detail=f"Agent {agent.name} is at capacity ({agent.max_tickets_per_day} tickets)"
        )
    
    agent.current_load += 1
    agent.last_active = datetime.utcnow()
    
    return agent


def unassign_ticket_from_agent(agent_id: str, ticket_id: str) -> Agent:
    """
    Decrement agent's current load when ticket is resolved/unassigned
    
    Called from tickets API when resolving/reassigning tickets
    """
    if agent_id not in agents_db:
        return None
    
    agent = agents_db[agent_id]
    
    if agent.current_load > 0:
        agent.current_load -= 1
        agent.total_tickets_resolved += 1
    
    agent.last_active = datetime.utcnow()
    
    return agent


def get_agent_by_id(agent_id: str) -> Optional[Agent]:
    """Get agent by ID (helper for other modules)"""
    return agents_db.get(agent_id)
