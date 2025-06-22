"""
Pydantic models for the EarSightAI backend
"""

from typing import List, Optional
from pydantic import BaseModel


class RoutePoint(BaseModel):
    """Model for a point in a route"""
    name: str
    lat: float
    lng: float
    script: str
    category: str
    distance_from_prev: Optional[float] = None
    duration_from_prev: Optional[float] = None


class RouteRequest(BaseModel):
    """Request model for route generation"""
    input_text: str
    context: Optional[List[dict]] = None


class RouteResponse(BaseModel):
    """Response model for route generation"""
    route: dict
    points: List[RoutePoint]
    total_distance_km: float
    geojson: dict
    message: str
    success: bool = True


class RoamRequest(BaseModel):
    """Request model for Roam API"""
    coordinates: str  # e.g., "43.6426, -79.3871"


class RoamResponse(BaseModel):
    """Response model for Roam API"""
    summary: str
