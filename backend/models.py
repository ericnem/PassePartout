"""
Pydantic models for the simplified Roam API
"""

from pydantic import BaseModel
from typing import Dict, Any


class RoamRequest(BaseModel):
    """Request model for Roam API"""
    coordinates: str  # e.g., "43.6426, -79.3871"


class RoamResponse(BaseModel):
    """Response model for Roam API"""
    summary: str
class RouteRequest(BaseModel):
    input_text: str
    context: Optional[List[Dict[str, str]]] = (
        None  # Optional chat history for Gemini context
    )


class RoutePoint(BaseModel):
    name: str
    lat: float
    lng: float
    script: str
    category: str
    distance_from_prev: Optional[float] = None  # in km
    duration_from_prev: Optional[float] = None  # in minutes


class RouteResponse(BaseModel):
    route: Dict[str, Any]
    points: List[RoutePoint]
    geojson: Dict[str, Any]
    total_distance_km: float
    distance_matrix: List[List[float]]
    duration_matrix: List[List[float]]
    success: bool
    message: str
