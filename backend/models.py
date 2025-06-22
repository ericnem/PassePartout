"""
Pydantic models for the simplified Roam API
"""

from pydantic import BaseModel


class RoamRequest(BaseModel):
    """Request model for Roam API"""
    coordinates: str  # e.g., "43.6426, -79.3871"


class RoamResponse(BaseModel):
    """Response model for Roam API"""
    summary: str
