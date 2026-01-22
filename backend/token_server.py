

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from livekit import api

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    roomName: str
    participantName: str


@app.post("/api/token")
async def generate_token(request: TokenRequest):
    """Generate LiveKit access token"""
    
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    # Check if credentials are configured
    if not livekit_url:
        raise HTTPException(status_code=500, detail="LIVEKIT_URL not configured in environment variables")
    if not livekit_api_key:
        raise HTTPException(status_code=500, detail="LIVEKIT_API_KEY not configured in environment variables")
    if not livekit_api_secret:
        raise HTTPException(status_code=500, detail="LIVEKIT_API_SECRET not configured in environment variables")
    
    try:
        # Create access token
        token = api.AccessToken(livekit_api_key, livekit_api_secret) \
            .with_identity(request.participantName) \
            .with_name(request.participantName) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=request.roomName,
                can_publish=True,
                can_subscribe=True,
            )) \
            .to_jwt()
        
        return {
            "token": token,
            "url": livekit_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

