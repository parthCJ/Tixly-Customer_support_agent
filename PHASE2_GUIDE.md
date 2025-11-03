# Phase 2: AI Classification Setup Guide

## 🎯 What's New

Phase 2 adds **AI-powered ticket classification**:
- ✅ Auto-categorize tickets (SHIPPING, BILLING, PRODUCT, etc.)
- ✅ Auto-assign priority (LOW, MEDIUM, HIGH, CRITICAL)
- ✅ Extract metadata (order IDs, amounts, dates)
- ✅ Sentiment analysis (positive, neutral, negative)
- ✅ AI-suggested replies

## 🚀 Quick Setup

### 1. Get a Free Groq API Key

Groq offers a generous free tier (30 req/min, 14,400 req/day):

1. Visit: https://console.groq.com/keys
2. Sign up (free, no credit card required)
3. Click "Create API Key"
4. Copy your key (starts with `gsk_...`)

### 2. Configure Environment

```powershell
# Copy the example env file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=gsk_your_actual_key_here
```

### 3. Install Dependencies

```powershell
pip install groq
```

Or reinstall everything:
```powershell
pip install -r requirements.txt
```

### 4. Start the Server

```powershell
python main.py
```

### 5. Test AI Classification

```powershell
python test_tickets.py
```

## 📊 How It Works

When a ticket is created:

1. **Ticket received** → API endpoint receives ticket data
2. **Background AI task** → Groq AI analyzes the ticket
3. **Classification** → AI determines category and priority
4. **Extraction** → Pulls out order IDs, dates, amounts
5. **Sentiment** → Analyzes customer emotion
6. **Reply generation** → Creates suggested response
7. **Auto-assign** → If confidence > 70%, auto-applies category/priority

## 🔍 Example: AI in Action

**Input Ticket:**
```json
{
  "subject": "URGENT: Order #2021 hasn't shipped",
  "description": "I placed order #2021 a week ago and paid $89.99 but tracking still shows processing. I need this by Friday!"
}
```

**AI Classification:**
```json
{
  "category": "SHIPPING",
  "priority": "HIGH",
  "sentiment": "negative",
  "urgency_keywords": ["urgent", "need this by"],
  "extracted_info": {
    "order_id": "2021",
    "amount": "$89.99",
    "date_mentioned": "Friday"
  },
  "confidence": 0.95,
  "reasoning": "Customer has urgent shipping concern with deadline"
}
```

**AI Suggested Reply:**
```
I understand how frustrating it must be to wait for your order, 
especially with a deadline approaching. I've checked order #2021 
and I'll escalate this immediately to our shipping team to get you 
tracking information today.

We'll do everything we can to ensure your order arrives by Friday. 
I'll follow up within 2 hours with an update.
```

## 🧪 Testing Without Groq API

If you don't want to use Groq yet, the system still works! It will:
- Use default category: `GENERAL`
- Use default priority: `MEDIUM`
- Skip AI reply generation
- Log a warning that AI is disabled

## 🎨 API Response Format

```json
{
  "ticket": {
    "ticket_id": "TKT-20241103-A1B2C3D4",
    "subject": "Order issue",
    "description": "...",
    "status": "new",
    
    // AI-assigned fields (if confidence > 0.7)
    "category": "SHIPPING",
    "priority": "HIGH",
    
    // AI suggestions (always present)
    "ai_suggested_category": "SHIPPING",
    "ai_suggested_priority": "HIGH",
    "ai_confidence": 0.95,
    "sentiment": "negative",
    "urgency_keywords": ["urgent", "asap"],
    "extracted_metadata": {
      "order_id": "2021",
      "amount": "$89.99"
    },
    "ai_suggested_reply": "I understand how frustrating..."
  }
}
```

## 💡 Tips

1. **High Confidence Auto-Assignment**: Only tickets with >70% confidence are auto-classified
2. **Review AI Suggestions**: Always check `ai_suggested_category` vs actual `category`
3. **Sentiment Analysis**: Use `sentiment` for prioritizing angry customers
4. **Urgency Keywords**: Track words like "urgent", "asap", "immediately"
5. **Extracted Metadata**: Automatically pulls order IDs, amounts, dates

## 🔧 Customization

Edit `backend/services/ai_service.py` to:
- Adjust confidence threshold (line 95)
- Modify classification prompt (line 123)
- Change AI model (line 22)
- Add new categories

## 📈 Next Steps

**Phase 3: RAG System** - Add knowledge base search with vector DB
- Use past tickets to suggest solutions
- Semantic search for similar issues
- Context-aware reply generation

**Phase 4: LSTM Forecasting** - Predict ticket volumes
- Historical trend analysis
- Staffing recommendations
- Peak hour predictions

Ready to implement Phase 3? Just let me know! 🚀
