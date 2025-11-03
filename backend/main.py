"""
Main FastAPI Application
Entry point for the Customer Support Copilot backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import tickets, forecasting

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
        "timestamp": "2024-11-03T10:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
