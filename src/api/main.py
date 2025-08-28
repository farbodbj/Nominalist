import dotenv
dotenv.load_dotenv('../../../.env')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from src.graph.workflow import UsernameWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Username Recommendation System",
    description="Multi-agent system for generating username recommendations",
    version="1.0.0"
)

# Initialize the workflow
workflow = UsernameWorkflow()

class UsernameRequest(BaseModel):
    """Request model for username generation."""
    name: str

class UsernameResponse(BaseModel):
    """Response model for username generation."""
    input_name: str
    recommended_usernames: List[str]
    count: int

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Username Recommendation System",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate-usernames (POST)",
            "health": "/health (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "username-recommendation-system"}

@app.post("/generate-usernames", response_model=UsernameResponse)
async def generate_usernames(request: UsernameRequest):
    """
    Generate username recommendations based on input name.
    """
    try:
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        
        logger.info(f"Generating usernames for: {request.name}")
        
        # Generate usernames using the workflow
        recommended_usernames = workflow.generate_usernames(request.name.strip())
        
        logger.info(f"Generated {len(recommended_usernames)} usernames")
        
        return UsernameResponse(
            input_name=request.name.strip(),
            recommended_usernames=recommended_usernames,
            count=len(recommended_usernames)
        )
    
    except Exception as e:
        logger.error(f"Error generating usernames: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
