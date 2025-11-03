# Customer Support Copilot - Ticket Creation Workflow

## 🎯 Phase 1: Foundation - Ticket Creation

Welcome! This is the starting point of our AI-powered support system. Let's build the ticket creation workflow step by step.

---

## 📋 What We're Building

A ticket creation system that:
1. **Receives** tickets from multiple sources (web forms, Zendesk, Intercom)
2. **Validates** and structures the data
3. **Generates** unique ticket IDs
4. **Stores** tickets for processing
5. **Queues** tickets for AI analysis (next phase)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Navigate to backend folder
cd backend

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
# Run the FastAPI server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 3: Test the API

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📝 Creating Your First Ticket

### Option 1: Using the Interactive Docs (Easiest!)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/tickets/create`
3. Click "Try it out"
4. Use this example:

```json
{
  "customer_email": "john.doe@example.com",
  "customer_name": "John Doe",
  "subject": "Order hasn't shipped yet",
  "description": "My order #2021 was placed a week ago but hasn't shipped. Can you help?",
  "order_id": "2021",
  "source": "web"
}
```

5. Click "Execute"
6. See your created ticket!

### Option 2: Using cURL

```bash
curl -X POST "http://localhost:8000/api/tickets/create" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "jane.smith@example.com",
    "customer_name": "Jane Smith",
    "subject": "Billing charge issue",
    "description": "I was charged twice for my subscription",
    "source": "web"
  }'
```

### Option 3: Using Python

```python
import requests

ticket_data = {
    "customer_email": "customer@example.com",
    "customer_name": "Test User",
    "subject": "Need help with account",
    "description": "Can't access my account after password reset",
    "source": "web"
}

response = requests.post(
    "http://localhost:8000/api/tickets/create",
    json=ticket_data
)

print(response.json())
```

---

## 🔍 Understanding the Code

### 1. Ticket Model (`models/ticket.py`)

This defines what a ticket looks like:

```python
class Ticket(BaseModel):
    ticket_id: str           # Unique ID (e.g., "TKT-20241103-A1B2C3D4")
    customer_email: str      # Who submitted it
    subject: str             # What's the problem
    description: str         # Detailed explanation
    status: TicketStatus     # new, open, in_progress, resolved, closed
    priority: TicketPriority # low, medium, high, critical
    # ... and more fields
```

**Key Fields Explained:**
- `ticket_id`: Auto-generated unique ID
- `customer_id`: Auto-generated from email (in production, lookup real customer)
- `status`: Tracks ticket lifecycle (NEW → OPEN → IN_PROGRESS → RESOLVED → CLOSED)
- `priority`: How urgent (LOW, MEDIUM, HIGH, CRITICAL)
- `category`: Problem type (SHIPPING, BILLING, TECHNICAL, etc.)
- `ai_suggested_*`: Fields the AI will fill in later

### 2. API Endpoints (`api/tickets.py`)

**Main Endpoints:**

#### Create Ticket
```
POST /api/tickets/create
```
- Receives ticket data from customer
- Generates unique ID
- Stores in database
- Returns ticket info immediately

#### Get Ticket
```
GET /api/tickets/{ticket_id}
```
- Retrieves a specific ticket by ID

#### List Tickets
```
GET /api/tickets/
```
- Lists all tickets (with optional filtering)

#### Update Status
```
PUT /api/tickets/{ticket_id}/status
```
- Changes ticket status (e.g., mark as resolved)

#### Webhooks
```
POST /api/tickets/webhook/zendesk
POST /api/tickets/webhook/intercom
```
- Receives tickets from external platforms

---

## 🔄 Data Flow Diagram

```
Customer Submits Ticket
         ↓
┌────────────────────────┐
│  POST /api/tickets/    │
│  create                │
└────────────────────────┘
         ↓
┌────────────────────────┐
│  Validate Data         │
│  - Check required      │
│    fields              │
│  - Validate email      │
└────────────────────────┘
         ↓
┌────────────────────────┐
│  Generate IDs          │
│  - ticket_id           │
│  - customer_id         │
└────────────────────────┘
         ↓
┌────────────────────────┐
│  Create Ticket Object  │
│  - Set status: NEW     │
│  - Set priority: MED   │
│  - Add timestamps      │
└────────────────────────┘
         ↓
┌────────────────────────┐
│  Store in Database     │
│  (In-memory for now)   │
└────────────────────────┘
         ↓
┌────────────────────────┐
│  Queue AI Processing   │
│  (Background task)     │
└────────────────────────┘
         ↓
┌────────────────────────┐
│  Return Response       │
│  - Ticket details      │
│  - Confirmation        │
└────────────────────────┘
```

---

## 🧪 Testing Examples

### Example 1: Shipping Delay

```json
{
  "customer_email": "customer1@example.com",
  "subject": "Order delayed",
  "description": "Order #5432 was supposed to arrive yesterday but tracking shows it's still in transit",
  "order_id": "5432",
  "source": "web"
}
```

### Example 2: Billing Issue

```json
{
  "customer_email": "customer2@example.com",
  "subject": "Double charged",
  "description": "I was charged $49.99 twice on Nov 1st for the same subscription",
  "source": "email"
}
```

### Example 3: Technical Support

```json
{
  "customer_email": "customer3@example.com",
  "subject": "App crashing",
  "description": "The mobile app crashes every time I try to upload a photo. Using iPhone 14 with iOS 17.",
  "source": "chat"
}
```

---

## 📊 What You Get Back

When you create a ticket, you get a response like this:

```json
{
  "ticket": {
    "ticket_id": "TKT-20241103-A1B2C3D4",
    "customer_id": "CUST-12345",
    "customer_email": "customer@example.com",
    "customer_name": "John Doe",
    "subject": "Order hasn't shipped",
    "description": "My order #2021 was placed a week ago...",
    "category": null,
    "priority": "medium",
    "status": "new",
    "order_id": "2021",
    "created_at": "2024-11-03T10:30:00Z",
    "source": "web"
  },
  "suggested_actions": [
    "Ticket created successfully",
    "AI processing queued",
    "Agent will be notified"
  ]
}
```

---

## 🔌 Webhook Integration

### Zendesk Webhook Example

When a ticket is created in Zendesk, it sends data to your webhook:

```bash
# Zendesk sends this to your webhook URL
POST http://your-domain.com/api/tickets/webhook/zendesk

{
  "ticket": {
    "id": 123,
    "subject": "Help needed",
    "description": "I can't login to my account",
    "requester": {
      "email": "user@example.com",
      "name": "User Name"
    }
  }
}
```

Our system automatically converts it to our format!

### Intercom Webhook Example

```bash
POST http://your-domain.com/api/tickets/webhook/intercom

{
  "type": "conversation.created",
  "data": {
    "item": {
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
```

---

## 🎯 Next Steps

Now that tickets can be created, we'll add:

1. **Phase 2: AI Classification**
   - Auto-categorize tickets (SHIPPING, BILLING, etc.)
   - Auto-assign priority (LOW, MEDIUM, HIGH, CRITICAL)
   - Extract key information (order IDs, dates, etc.)

2. **Phase 3: Knowledge Base (RAG)**
   - Search KB for relevant solutions
   - Generate suggested replies
   - Provide sources/citations

3. **Phase 4: Forecasting**
   - Predict ticket volumes
   - Staffing recommendations
   - Trend analysis

4. **Phase 5: Agent Dashboard**
   - View tickets
   - See AI suggestions
   - Take actions

---

## 💡 Tips

**Current Storage:**
- Tickets are stored in memory (`tickets_db` dictionary)
- This is fine for learning/testing
- Data is lost when server restarts

**Next Phase:**
- We'll add a real database (SQLite or PostgreSQL)
- Persistent storage
- Better querying

**Testing:**
- Use the `/docs` endpoint (FastAPI auto-generates it!)
- It's interactive and shows examples
- Try different ticket scenarios

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Check Python version (need 3.10+)
python --version
```

### Can't access http://localhost:8000
```bash
# Check if server is running
# Look for: "Uvicorn running on http://0.0.0.0:8000"

# Try http://127.0.0.1:8000 instead
```

### Import errors
```bash
# Make sure you're in the backend folder
cd backend

# Install dependencies again
pip install -r requirements.txt
```

---

## 📚 Learn More

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Models**: https://docs.pydantic.dev/
- **HTTP Status Codes**: https://httpstatuses.com/

---

**Ready to test?** Start the server and create your first ticket! 🚀

In the next phase, we'll add AI to automatically classify and process these tickets.
