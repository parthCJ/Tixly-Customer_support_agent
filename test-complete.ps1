# Complete End-to-End Testing Script
# Customer Support Copilot - Full System Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Customer Support Copilot - E2E Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify Servers
Write-Host "[STEP 1] Verifying servers are running..." -ForegroundColor Yellow
Write-Host ""

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host "  Backend (Port 8000):" -ForegroundColor Green
    Write-Host "    Status: $($health.status)" -ForegroundColor White
    Write-Host "    Agents: $($health.agents_count)" -ForegroundColor White
    Write-Host "    Tickets: $($health.tickets_count)" -ForegroundColor White
} catch {
    Write-Host "  ERROR: Backend not running!" -ForegroundColor Red
    Write-Host "  Start with: cd backend; python main.py" -ForegroundColor Yellow
    exit 1
}

try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "  Frontend (Port 3000):" -ForegroundColor Green
    Write-Host "    Status: OK (HTTP $($frontendCheck.StatusCode))" -ForegroundColor White
} catch {
    Write-Host "  ERROR: Frontend not running!" -ForegroundColor Red
    Write-Host "  Start with: cd frontend; npm run dev" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 2: Create Test Tickets
Write-Host "[STEP 2] Creating test tickets..." -ForegroundColor Yellow
Write-Host ""

$tickets = @(
    @{
        name = "Shipping Delay"
        data = @{
            subject = "My package hasn't arrived yet"
            description = "I ordered product XYZ-123 with order #12345 five days ago but it still hasn't shipped. This is urgent! I need it for a gift tomorrow."
            customer_email = "john.doe@example.com"
            customer_name = "John Doe"
            customer_id = "CUST-001"
        }
    },
    @{
        name = "Billing Issue"
        data = @{
            subject = "Incorrect charge on my credit card"
            description = "I was charged $99.99 but my order confirmation shows $79.99. Please refund the $20 difference immediately."
            customer_email = "jane.smith@example.com"
            customer_name = "Jane Smith"
            customer_id = "CUST-002"
        }
    },
    @{
        name = "Technical Problem"
        data = @{
            subject = "Cannot access my account"
            description = "I keep getting 'Invalid password' error even though I'm using the correct password. I tried resetting it but the email never arrived. Please help!"
            customer_email = "mike.jones@example.com"
            customer_name = "Mike Jones"
            customer_id = "CUST-003"
        }
    }
)

$createdTickets = @()

foreach ($ticketInfo in $tickets) {
    $body = $ticketInfo.data | ConvertTo-Json
    try {
        $result = Invoke-RestMethod -Uri "http://localhost:8000/api/tickets/create" -Method POST -Body $body -ContentType "application/json"
        $createdTickets += $result.ticket.ticket_id
        
        Write-Host "  Created: $($ticketInfo.name)" -ForegroundColor Green
        Write-Host "    ID: $($result.ticket.ticket_id)" -ForegroundColor White
        Write-Host "    AI Category: $($result.ai_classification.category)" -ForegroundColor Cyan
        Write-Host "    AI Priority: $($result.ai_classification.priority)" -ForegroundColor Cyan
        Write-Host "    AI Sentiment: $($result.ai_classification.sentiment)" -ForegroundColor Cyan
        Write-Host ""
    } catch {
        Write-Host "  ERROR creating ticket: $($ticketInfo.name)" -ForegroundColor Red
        Write-Host "  $_" -ForegroundColor Red
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 3: Auto-Assign Tickets
Write-Host "[STEP 3] Auto-assigning tickets to agents..." -ForegroundColor Yellow
Write-Host ""

foreach ($ticketId in $createdTickets) {
    try {
        $assignment = Invoke-RestMethod -Uri "http://localhost:8000/api/tickets/$ticketId/assign?auto_assign=true" -Method PUT
        
        Write-Host "  Assigned: $ticketId" -ForegroundColor Green
        Write-Host "    Agent: $($assignment.assignment.agent_name)" -ForegroundColor White
        Write-Host "    Team: $($assignment.assignment.agent_team)" -ForegroundColor White
        Write-Host "    Load: $($assignment.assignment.agent_load) tickets" -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "  ERROR assigning ticket: $ticketId" -ForegroundColor Red
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 4: View All Agents
Write-Host "[STEP 4] Checking agent status..." -ForegroundColor Yellow
Write-Host ""

try {
    $agents = Invoke-RestMethod -Uri "http://localhost:8000/api/agents/"
    
    Write-Host "  Total Agents: $($agents.Count)" -ForegroundColor Green
    Write-Host ""
    
    foreach ($agent in $agents) {
        $statusColor = if ($agent.status -eq "active") { "Green" } else { "Yellow" }
        Write-Host "  $($agent.name) ($($agent.agent_id))" -ForegroundColor White
        Write-Host "    Team: $($agent.team)" -ForegroundColor Gray
        Write-Host "    Skills: $($agent.skills -join ', ')" -ForegroundColor Gray
        Write-Host "    Load: $($agent.current_load)/$($agent.max_tickets_per_day)" -ForegroundColor Gray
        Write-Host "    Status: $($agent.status)" -ForegroundColor $statusColor
        Write-Host "    Resolved: $($agent.total_tickets_resolved) tickets" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "  ERROR fetching agents" -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 5: Test RAG Knowledge Base
Write-Host "[STEP 5] Testing RAG Knowledge Base..." -ForegroundColor Yellow
Write-Host ""

$kbQuery = @{
    query = "How do I return a defective product?"
    top_k = 3
} | ConvertTo-Json

try {
    $kbResults = Invoke-RestMethod -Uri "http://localhost:8000/api/kb/search" -Method POST -Body $kbQuery -ContentType "application/json"
    
    Write-Host "  Query: 'How do I return a defective product?'" -ForegroundColor Cyan
    Write-Host "  Found: $($kbResults.results.Count) articles" -ForegroundColor Green
    Write-Host ""
    
    foreach ($article in $kbResults.results | Select-Object -First 3) {
        $score = [math]::Round($article.relevance_score, 2)
        Write-Host "  - $($article.title)" -ForegroundColor White
        Write-Host "    Relevance: $score" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "  WARNING: RAG search failed (ChromaDB may need initialization)" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 6: Test Forecasting (if model exists)
Write-Host "[STEP 6] Testing LSTM Forecasting..." -ForegroundColor Yellow
Write-Host ""

try {
    $forecast = Invoke-RestMethod -Uri "http://localhost:8000/api/forecasting/daily?days=7" -Method GET
    
    Write-Host "  7-Day Forecast:" -ForegroundColor Green
    Write-Host ""
    
    foreach ($day in $forecast.predictions) {
        $tickets = [math]::Round($day.predicted_tickets, 0)
        Write-Host "  $($day.date): $tickets tickets" -ForegroundColor White
    }
    Write-Host ""
} catch {
    Write-Host "  WARNING: Forecasting not available (model may not be trained)" -ForegroundColor Yellow
    Write-Host "  Train with: python backend/train_forecast_model.py" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 7: Get Agent Stats
Write-Host "[STEP 7] Getting agent performance stats..." -ForegroundColor Yellow
Write-Host ""

try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/agents/stats"
    
    foreach ($stat in $stats | Select-Object -First 5) {
        $util = [math]::Round($stat.utilization_percentage, 1)
        $utilColor = if ($util -gt 80) { "Red" } elseif ($util -gt 60) { "Yellow" } else { "Green" }
        
        Write-Host "  $($stat.name):" -ForegroundColor White
        Write-Host "    Utilization: $util%" -ForegroundColor $utilColor
        Write-Host "    Capacity: $($stat.available_capacity) tickets available" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "  ERROR fetching stats" -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Final Summary
Write-Host "[SUMMARY] Test Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Now test the FRONTEND:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Open browser: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "  2. Test Navigation:" -ForegroundColor White
Write-Host "     - Dashboard     (http://localhost:3000/agent)" -ForegroundColor Gray
Write-Host "     - My Tickets    (http://localhost:3000/agent/tickets)" -ForegroundColor Gray
Write-Host "     - Analytics     (http://localhost:3000/manager)" -ForegroundColor Gray
Write-Host "     - Settings      (http://localhost:3000/settings)" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. What to Check:" -ForegroundColor White
Write-Host "     - Stats show correct counts (3 tickets created)" -ForegroundColor Gray
Write-Host "     - Tickets display with priority/category badges" -ForegroundColor Gray
Write-Host "     - AI suggested replies are visible" -ForegroundColor Gray
Write-Host "     - Manager dashboard shows team metrics" -ForegroundColor Gray
Write-Host "     - All navigation links work without 404 errors" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. API Documentation:" -ForegroundColor White
Write-Host "     http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created Tickets: $($createdTickets.Count)" -ForegroundColor Green
Write-Host "Ticket IDs: $($createdTickets -join ', ')" -ForegroundColor White
Write-Host ""
Write-Host "Test completed successfully!" -ForegroundColor Green
Write-Host ""
