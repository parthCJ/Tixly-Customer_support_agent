"""
Hugging Face Space Entry Point for Tixly Customer Support Copilot
This simply exposes the FastAPI backend for the Space
"""
import os

# Import and expose the FastAPI app
from backend.main import app

# For Hugging Face Spaces, we just need to expose the app
# Spaces will automatically run it with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
