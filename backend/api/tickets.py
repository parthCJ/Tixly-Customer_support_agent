"""
Ticket Creation API Endpoint
Handles incoming ticket creation requests from various sources
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel

from ..models.ticket import (
    Ticket,
    TicketCreateRequest,
    TicketResponse,
    TicketStatus,
    TicketPriority,
    TicketCategory
)
from ..models.user import User, UserRole

# Import agent management functions
from . import agents as agents_api

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

# In-memory storage for demo (replace with database in production)
tickets_db = {}

# Global service instances (set by main.py on startup)
ai_service = None
kb_service = None


# Request models
class StatusUpdateRequest(BaseModel):
    status: TicketStatus


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
        
        # Check if AI service is available
        if not ai_service:
            print("⚠️  AI service not available, skipping AI processing")
            return
        
        # Prepare metadata for AI
        metadata = {
            "order_id": ticket.order_id,
            "customer_name": ticket.customer_name,
            "source": ticket.source
        }
        
        # Classify the ticket using the pre-initialized service
        classification = ai_service.classify_ticket(
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
        
        # Store complete AI analysis as a dictionary (this will be serialized in the response)
        ticket.ai_analysis = {
            "category": classification["category"],
            "priority": classification["priority"],
            "confidence": classification["confidence"],
            "sentiment": classification["sentiment"],
            "urgency_keywords": classification["urgency_keywords"],
            "extracted_info": classification["extracted_info"],
            "reasoning": classification.get("reasoning", "")
        }
        
        print(f"   📊 AI Analysis stored: {ticket.ai_analysis}")
        
        # Auto-assign category and priority if confidence is high
        category_changed = False
        if classification["confidence"] > 0.7:
            old_category = ticket.category
            ticket.category = TicketCategory(classification["category"])
            ticket.priority = TicketPriority(classification["priority"])
            print(f"   ✅ Auto-classified: {ticket.category.value} | {ticket.priority.value}")
            
            # Check if category changed significantly and reassign if needed
            if old_category != ticket.category and ticket.assigned_to:
                category_changed = True
                print(f"   🔄 Category changed from {old_category} to {ticket.category}, checking reassignment...")
        else:
            print(f"   ⚠️  Low confidence ({classification['confidence']:.2f}), keeping defaults")
        
        # Generate suggested reply using the pre-initialized service
        ticket_data = {
            "subject": ticket.subject,
            "description": ticket.description,
            "category": ticket.category.value if ticket.category else "GENERAL",
            "priority": ticket.priority.value
        }
        
        # Search KB for context if kb_service is available
        kb_context = None
        if kb_service:
            try:
                kb_articles = kb_service.search(
                    query=ticket.description,
                    n_results=2,
                    category_filter=ticket.category.value if ticket.category else None
                )
                if kb_articles:
                    kb_context = "\n\n".join([
                        f"KB Article: {article['title']}\n{article['content'][:500]}..."
                        for article in kb_articles[:2]
                    ])
            except Exception as e:
                print(f"   ⚠️  KB search failed: {e}")
        
        suggested_reply = ai_service.generate_suggested_reply(ticket_data, kb_context)
        ticket.ai_suggested_reply = suggested_reply
        
        # Reassign to better agent if category changed after AI classification
        if category_changed:
            try:
                current_agent_id = ticket.assigned_to
                best_agent = agents_api.find_best_agent_for_ticket(
                    category=ticket.category,
                    priority=ticket.priority.value if ticket.priority else "medium"
                )
                
                # Only reassign if we found a better agent with matching skills
                if best_agent and best_agent.agent_id != current_agent_id:
                    # Check if new agent has the skill for this category
                    if ticket.category.value in best_agent.skills:
                        # Unassign from current agent
                        agents_api.unassign_ticket_from_agent(current_agent_id, ticket.ticket_id)
                        # Assign to new agent
                        agents_api.assign_ticket_to_agent(best_agent.agent_id, ticket.ticket_id)
                        ticket.assigned_to = best_agent.agent_id
                        ticket.team = best_agent.team
                        print(f"   🔄 Reassigned from {current_agent_id} to {best_agent.name} (has {ticket.category.value} skill)")
            except Exception as e:
                print(f"   ⚠️  Could not reassign ticket: {e}")
        
        # Update the ticket in storage
        tickets_db[ticket.ticket_id] = ticket
        
        print(f"   ✨ AI processing complete!")
        print(f"   Reasoning: {classification['reasoning']}")
        
    except Exception as e:
        print(f"   ❌ AI processing error: {str(e)}")
        # Don't fail the ticket creation, just log the error


@router.post("/create/", response_model=TicketResponse)
async def create_ticket(
    request: TicketCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new support ticket
    
    This endpoint receives ticket data from various sources:
    - Web forms (public or authenticated)
    - Email (via webhook)
    - Chat systems
    - Support platforms (Zendesk, Intercom, etc.)
    
    Flow:
    1. Validate incoming data
    2. Generate unique ticket ID
    3. Create ticket record
    4. Queue for AI processing (background)
    5. Return ticket info immediately
    
    Note: Authentication is optional to support webhooks and public forms
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
        
        # Queue AI processing in background (will update category/priority)
        background_tasks.add_task(process_ticket_with_ai, ticket)
        
        # Try to auto-assign to best available agent after AI processing completes
        # For now, assign immediately based on default category
        try:
            best_agent = agents_api.find_best_agent_for_ticket(
                category=ticket.category,
                priority=ticket.priority.value if ticket.priority else "medium"
            )
            
            if best_agent:
                ticket.assigned_to = best_agent.agent_id
                ticket.team = best_agent.team
                ticket.status = TicketStatus.IN_PROGRESS
                agents_api.assign_ticket_to_agent(best_agent.agent_id, ticket_id)
                assignment_message = f"Auto-assigned to {best_agent.name}"
                print(f"✅ Ticket {ticket_id} auto-assigned to {best_agent.name}")
            else:
                assignment_message = "Pending agent assignment"
                print(f"⚠️  No available agent found for ticket {ticket_id}")
        except Exception as e:
            assignment_message = "Pending agent assignment"
            print(f"⚠️  Could not auto-assign ticket {ticket_id}: {e}")
        
        # Return immediate response
        return TicketResponse(
            ticket=ticket,
            suggested_actions=[
                "Ticket created successfully",
                assignment_message,
                "AI classification in progress",
                "Agent will be notified"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create ticket: {str(e)}"
        )


@router.get("/{ticket_id}/", response_model=Ticket)
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


@router.post("/webhook/zendesk/")
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


@router.post("/webhook/intercom/")
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


@router.put("/{ticket_id}/status/")
async def update_ticket_status(
    ticket_id: str,
    status: TicketStatus = Query(..., description="New status for the ticket")
):
    """
    Update ticket status
    
    When resolving/closing tickets, automatically decrements agent's current load
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )
    
    ticket = tickets_db[ticket_id]
    old_status = ticket.status
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    
    # If ticket is being resolved/closed, reduce agent's load
    if status in [TicketStatus.RESOLVED, TicketStatus.CLOSED] and old_status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
        if ticket.assigned_to:
            agents_api.unassign_ticket_from_agent(ticket.assigned_to, ticket_id)
    
    if status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
    
    return ticket


@router.put("/{ticket_id}/assign/")
async def assign_ticket(
    ticket_id: str, 
    agent_id: Optional[str] = Query(None, description="Specific agent ID to assign to"),
    auto_assign: bool = Query(False, description="Automatically find best available agent"),
    team: Optional[str] = None
):
    """
    Assign ticket to an agent
    
    Two modes:
    1. Manual assignment: Provide agent_id
    2. Auto-assignment: Set auto_assign=true, system finds best agent
    
    Auto-assignment logic:
    - Matches agent skills to ticket category
    - Considers agent availability and current load
    - Assigns to least busy qualified agent
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )
    
    ticket = tickets_db[ticket_id]
    
    # Auto-assignment mode
    if auto_assign:
        best_agent = agents_api.find_best_agent_for_ticket(
            category=ticket.category,
            priority=ticket.priority.value if ticket.priority else None
        )
        
        if not best_agent:
            raise HTTPException(
                status_code=404,
                detail=f"No available agents found with skills for {ticket.category}"
            )
        
        agent_id = best_agent.agent_id
        
        # Increment agent's load
        agents_api.assign_ticket_to_agent(agent_id, ticket_id)
        
        ticket.assigned_to = agent_id
        ticket.team = best_agent.team
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.updated_at = datetime.utcnow()
        
        return {
            "ticket": ticket,
            "assignment": {
                "mode": "auto",
                "agent_id": best_agent.agent_id,
                "agent_name": best_agent.name,
                "agent_load": best_agent.current_load,
                "message": f"Auto-assigned to {best_agent.name} (load: {best_agent.current_load}/{best_agent.max_tickets_per_day})"
            }
        }
    
    # Manual assignment mode
    if not agent_id:
        raise HTTPException(
            status_code=400,
            detail="Must provide agent_id or set auto_assign=true"
        )
    
    # Check if agent exists and has capacity
    agent = agents_api.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    # Unassign from previous agent if reassigning
    if ticket.assigned_to and ticket.assigned_to != agent_id:
        agents_api.unassign_ticket_from_agent(ticket.assigned_to, ticket_id)
    
    # Assign to new agent
    agents_api.assign_ticket_to_agent(agent_id, ticket_id)
    
    ticket.assigned_to = agent_id
    if team:
        ticket.team = team
    else:
        ticket.team = agent.team
    ticket.status = TicketStatus.IN_PROGRESS
    ticket.updated_at = datetime.utcnow()
    
    return {
        "ticket": ticket,
        "assignment": {
            "mode": "manual",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "agent_load": agent.current_load,
            "message": f"Assigned to {agent.name} (load: {agent.current_load}/{agent.max_tickets_per_day})"
        }
    }


@router.put("/{ticket_id}/unassign/")
async def unassign_ticket(ticket_id: str):
    """
    Remove agent assignment from a ticket
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )
    
    ticket = tickets_db[ticket_id]
    
    # Decrement agent's load if assigned
    if ticket.assigned_to:
        agents_api.unassign_ticket_from_agent(ticket.assigned_to, ticket_id)
        previous_agent = ticket.assigned_to
        ticket.assigned_to = None
        ticket.status = TicketStatus.NEW
        ticket.updated_at = datetime.utcnow()
        
        return {
            "ticket": ticket,
            "message": f"Unassigned from {previous_agent}"
        }
    
    return {
        "ticket": ticket,
        "message": "Ticket was not assigned"
    }

