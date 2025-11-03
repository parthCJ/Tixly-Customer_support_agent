"""
Agent Models for Customer Support Copilot

This module defines the data models for support agents who handle tickets.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent availability status"""
    ACTIVE = "active"
    AWAY = "away"
    OFFLINE = "offline"


class Agent(BaseModel):
    """
    Support Agent Model
    
    Represents a customer support agent who handles tickets.
    Tracks skills, capacity, current workload, and availability.
    """
    agent_id: str = Field(..., description="Unique agent identifier (e.g., AGENT-001)")
    name: str = Field(..., description="Agent's full name")
    email: EmailStr = Field(..., description="Agent's email address")
    
    # Team and Skills
    team: Optional[str] = Field(None, description="Team name (e.g., shipping_team, billing_team)")
    skills: List[str] = Field(default_factory=list, description="Agent's expertise areas (e.g., ['SHIPPING', 'RETURNS'])")
    
    # Capacity Management
    max_tickets_per_day: int = Field(15, description="Maximum tickets agent can handle per day", ge=1, le=50)
    current_load: int = Field(0, description="Number of currently assigned active tickets", ge=0)
    
    # Status and Availability
    status: AgentStatus = Field(AgentStatus.ACTIVE, description="Current availability status")
    active: bool = Field(True, description="Whether agent can receive new ticket assignments")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Agent creation timestamp")
    last_active: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    
    # Performance Tracking (optional)
    total_tickets_resolved: int = Field(0, description="Lifetime tickets resolved", ge=0)
    avg_resolution_time_minutes: Optional[float] = Field(None, description="Average time to resolve tickets")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "AGENT-001",
                "name": "Alice Johnson",
                "email": "alice@company.com",
                "team": "shipping_team",
                "skills": ["SHIPPING", "RETURNS", "PRODUCT_INQUIRY"],
                "max_tickets_per_day": 15,
                "current_load": 3,
                "status": "active",
                "active": True,
                "total_tickets_resolved": 245,
                "avg_resolution_time_minutes": 12.5
            }
        }


class AgentCreate(BaseModel):
    """Schema for creating a new agent"""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent's full name")
    email: EmailStr = Field(..., description="Agent's email address")
    team: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    max_tickets_per_day: int = Field(15, ge=1, le=50)
    

class AgentUpdate(BaseModel):
    """Schema for updating agent details"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    team: Optional[str] = None
    skills: Optional[List[str]] = None
    max_tickets_per_day: Optional[int] = Field(None, ge=1, le=50)
    status: Optional[AgentStatus] = None
    active: Optional[bool] = None


class AgentStats(BaseModel):
    """Agent performance statistics"""
    agent_id: str
    name: str
    current_load: int
    max_tickets_per_day: int
    utilization_percentage: float  # (current_load / max_tickets) * 100
    available_capacity: int  # max_tickets - current_load
    is_available: bool  # Can accept new tickets
    total_tickets_resolved: int
    avg_resolution_time_minutes: Optional[float]
    status: AgentStatus


class AgentAssignmentResponse(BaseModel):
    """Response after assigning ticket to agent"""
    success: bool
    agent_id: str
    agent_name: str
    ticket_id: str
    message: str
    new_load: int
    available_capacity: int
