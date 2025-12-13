"""
Ticket Model - Represents a customer support ticket
This is the core data structure for our support system
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TicketStatus(str, Enum):
    """Ticket lifecycle states"""
    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Ticket urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, Enum):
    """Common support ticket categories"""
    SHIPPING = "shipping_delay"
    BILLING = "billing_issue"
    PRODUCT = "product_defect"
    ACCOUNT = "account_access"
    TECHNICAL = "technical_support"
    REFUND = "refund_request"
    GENERAL = "general_inquiry"
    OTHER = "other"


class Ticket(BaseModel):
    """
    Main Ticket Model
    
    This represents a customer support ticket with all necessary fields
    for processing, classification, and routing.
    """
    # Core identification
    ticket_id: str = Field(..., description="Unique ticket identifier")
    
    # Customer information
    customer_id: str = Field(..., description="Customer identifier")
    customer_email: str = Field(..., description="Customer email")
    customer_name: Optional[str] = Field(None, description="Customer name")
    
    # Ticket content
    subject: str = Field(..., description="Ticket subject line")
    description: str = Field(..., description="Detailed problem description")
    
    # Classification (can be auto-filled by AI)
    category: Optional[TicketCategory] = Field(None, description="Ticket category")
    priority: Optional[TicketPriority] = Field(TicketPriority.MEDIUM, description="Urgency level")
    status: TicketStatus = Field(TicketStatus.NEW, description="Current ticket status")
    
    # Assignment and routing
    assigned_to: Optional[str] = Field(None, description="Agent ID assigned to ticket")
    team: Optional[str] = Field(None, description="Team responsible for ticket")
    
    # AI-generated fields
    ai_suggested_category: Optional[TicketCategory] = Field(None, description="AI-predicted category")
    ai_suggested_priority: Optional[TicketPriority] = Field(None, description="AI-predicted priority")
    ai_suggested_reply: Optional[str] = Field(None, description="AI-generated draft response")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score (0-1)")
    
    # AI analysis fields
    ai_analysis: Optional[Dict[str, Any]] = Field(None, description="Complete AI analysis result")
    sentiment: Optional[str] = Field(None, description="Customer sentiment: positive, neutral, or negative")
    urgency_keywords: list[str] = Field(default_factory=list, description="Detected urgency indicators")
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict, description="AI-extracted entities (order_id, amounts, dates)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Ticket creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    # Additional context
    order_id: Optional[str] = Field(None, description="Related order number (if applicable)")
    tags: list[str] = Field(default_factory=list, description="Custom tags")
    attachments: list[str] = Field(default_factory=list, description="Attachment URLs")
    
    # Source tracking
    source: str = Field("web", description="Ticket origin (web, email, chat, phone)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TKT-2024-00001",
                "customer_id": "CUST-12345",
                "customer_email": "john.doe@example.com",
                "customer_name": "John Doe",
                "subject": "Order hasn't shipped yet",
                "description": "My order #2021 was placed a week ago but hasn't shipped. Can you help?",
                "category": "shipping_delay",
                "priority": "medium",
                "status": "new",
                "order_id": "2021",
                "source": "web",
                "created_at": "2024-11-03T10:00:00Z"
            }
        }


class TicketCreateRequest(BaseModel):
    """
    Request model for creating a new ticket
    (What customers/systems send to create a ticket)
    """
    customer_email: str
    customer_name: Optional[str] = None
    subject: str
    description: str
    order_id: Optional[str] = None
    source: str = "web"
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_email": "customer@example.com",
                "customer_name": "Jane Smith",
                "subject": "Billing charge issue",
                "description": "I was charged twice for my subscription this month",
                "source": "web"
            }
        }


class TicketResponse(BaseModel):
    """
    Response model after ticket processing
    (What we send back to agents/systems)
    """
    ticket: Ticket
    ai_analysis: Optional[Dict[str, Any]] = None
    suggested_actions: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket": {
                    "ticket_id": "TKT-2024-00001",
                    "customer_email": "customer@example.com",
                    "subject": "Billing charge issue",
                    "ai_suggested_category": "billing_issue",
                    "ai_suggested_priority": "high",
                    "ai_confidence": 0.92
                },
                "ai_analysis": {
                    "detected_issues": ["duplicate_charge"],
                    "sentiment": "frustrated",
                    "urgency_score": 0.85
                },
                "suggested_actions": [
                    "Check billing records for duplicate charges",
                    "Initiate refund if confirmed",
                    "Send apology and explanation"
                ]
            }
        }
