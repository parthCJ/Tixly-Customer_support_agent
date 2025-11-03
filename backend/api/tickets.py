"""
Ticket Creation API Endpoint
Handles incoming ticket creation requests from various sources
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import uuid
from typing import Optional

from models.ticket import (
    Ticket,
    TicketCreateRequest,
    TicketResponse,
    TicketStatus,
    TicketPriority,
    TicketCategory
)
from services.ai_service import classify_ticket, generate_reply

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

# In-memory storage for demo (replace with database in production)
tickets_db = {}


def generate_ticket_id() -> str:
    """Generate a unique ticket ID"""
    date_prefix = datetime.utcnow().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"TKT-{date_prefix}-{unique_id}"


def generate_customer_id(email: str) -> str:
    """Generate or lookup customer ID based on email"""
    # In production, this would lookup existing customer or create new one
    return f"CUST-{hash(email) % 100000:05d}"


async def process_ticket_with_ai(ticket: Ticket):
    """
    Background task to process ticket with AI
    - Classify ticket category
    - Assign priority based on content
    - Extract key information
    - Generate suggested reply
    """
    try:
        print(f"🤖 Processing ticket {ticket.ticket_id} with AI...")
        
        # Prepare metadata for AI
        metadata = {
            "order_id": ticket.order_id,
            "customer_name": ticket.customer_name,
            "source": ticket.source
        }
        
        # Classify the ticket
        classification = classify_ticket(
            subject=ticket.subject,
            description=ticket.description,
            metadata=metadata
        )
        
        # Update ticket with AI results
        ticket.ai_suggested_category = classification["category"]
        ticket.ai_suggested_priority = classification["priority"]
        ticket.ai_confidence = classification["confidence"]
        ticket.sentiment = classification["sentiment"]
        ticket.urgency_keywords = classification["urgency_keywords"]
        ticket.extracted_metadata = classification["extracted_info"]
        
        # Auto-assign category and priority if confidence is high
        if classification["confidence"] > 0.7:
            ticket.category = TicketCategory(classification["category"])
            ticket.priority = TicketPriority(classification["priority"])
            print(f"   ✅ Auto-classified: {ticket.category.value} | {ticket.priority.value}")
        else:
            print(f"   ⚠️  Low confidence ({classification['confidence']:.2f}), keeping defaults")
        
        # Generate suggested reply
        ticket_data = {
            "subject": ticket.subject,
            "description": ticket.description,
            "category": ticket.category.value if ticket.category else "GENERAL",
            "priority": ticket.priority.value
        }
        
        suggested_reply = generate_reply(ticket_data)
        ticket.ai_suggested_reply = suggested_reply
        
        # Update the ticket in storage
        tickets_db[ticket.ticket_id] = ticket
        
        print(f"   ✨ AI processing complete!")
        print(f"   Reasoning: {classification['reasoning']}")
        
    except Exception as e:
        print(f"   ❌ AI processing error: {str(e)}")
        # Don't fail the ticket creation, just log the error


@router.post("/create", response_model=TicketResponse)
async def create_ticket(
    request: TicketCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new support ticket
    
    This endpoint receives ticket data from various sources:
    - Web forms
    - Email (via webhook)
    - Chat systems
    - Support platforms (Zendesk, Intercom, etc.)
    
    Flow:
    1. Validate incoming data
    2. Generate unique ticket ID
    3. Create ticket record
    4. Queue for AI processing (background)
    5. Return ticket info immediately
    """
    try:
        # Generate IDs
        ticket_id = generate_ticket_id()
        customer_id = generate_customer_id(request.customer_email)
        
        # Create ticket object
        ticket = Ticket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            subject=request.subject,
            description=request.description,
            order_id=request.order_id,
            source=request.source,
            status=TicketStatus.NEW,
            priority=TicketPriority.MEDIUM,  # Default, will be updated by AI
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store ticket
        tickets_db[ticket_id] = ticket
        
        # Queue AI processing in background
        background_tasks.add_task(process_ticket_with_ai, ticket)
        
        # Return immediate response
        return TicketResponse(
            ticket=ticket,
            suggested_actions=[
                "Ticket created successfully",
                "AI processing queued",
                "Agent will be notified"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create ticket: {str(e)}"
        )


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str):
    """
    Retrieve a ticket by ID
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )
    
    return tickets_db[ticket_id]


@router.get("/", response_model=list[Ticket])
async def list_tickets(
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    limit: int = 50
):
    """
    List tickets with optional filtering
    """
    tickets = list(tickets_db.values())
    
    # Filter by status
    if status:
        tickets = [t for t in tickets if t.status == status]
    
    # Filter by priority
    if priority:
        tickets = [t for t in tickets if t.priority == priority]
    
    # Sort by creation date (newest first)
    tickets.sort(key=lambda t: t.created_at, reverse=True)
    
    # Limit results
    return tickets[:limit]


@router.post("/webhook/zendesk")
async def zendesk_webhook(payload: dict, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for Zendesk integration
    
    Example Zendesk webhook payload:
    {
        "ticket": {
            "id": 123,
            "subject": "Help needed",
            "description": "I can't login",
            "requester": {
                "email": "user@example.com",
                "name": "User Name"
            }
        }
    }
    """
    try:
        zendesk_ticket = payload.get("ticket", {})
        requester = zendesk_ticket.get("requester", {})
        
        # Convert Zendesk format to our format
        request = TicketCreateRequest(
            customer_email=requester.get("email"),
            customer_name=requester.get("name"),
            subject=zendesk_ticket.get("subject"),
            description=zendesk_ticket.get("description"),
            source="zendesk"
        )
        
        # Create ticket using our standard flow
        return await create_ticket(request, background_tasks)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Zendesk webhook payload: {str(e)}"
        )


@router.post("/webhook/intercom")
async def intercom_webhook(payload: dict, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for Intercom integration
    
    Example Intercom webhook payload:
    {
        "type": "conversation.created",
        "data": {
            "item": {
                "id": "456",
                "conversation_message": {
                    "body": "I need help with my order"
                },
                "user": {
                    "email": "user@example.com",
                    "name": "User Name"
                }
            }
        }
    }
    """
    try:
        data = payload.get("data", {}).get("item", {})
        user = data.get("user", {})
        message = data.get("conversation_message", {})
        
        # Convert Intercom format to our format
        request = TicketCreateRequest(
            customer_email=user.get("email"),
            customer_name=user.get("name"),
            subject="Support Request",  # Intercom doesn't have subjects
            description=message.get("body"),
            source="intercom"
        )
        
        # Create ticket using our standard flow
        return await create_ticket(request, background_tasks)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Intercom webhook payload: {str(e)}"
        )


@router.put("/{ticket_id}/status")
async def update_ticket_status(ticket_id: str, status: TicketStatus):
    """
    Update ticket status
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )
    
    ticket = tickets_db[ticket_id]
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    
    if status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
    
    return ticket


@router.put("/{ticket_id}/assign")
async def assign_ticket(ticket_id: str, agent_id: str, team: Optional[str] = None):
    """
    Assign ticket to an agent
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )
    
    ticket = tickets_db[ticket_id]
    ticket.assigned_to = agent_id
    if team:
        ticket.team = team
    ticket.status = TicketStatus.IN_PROGRESS
    ticket.updated_at = datetime.utcnow()
    
    return ticket
