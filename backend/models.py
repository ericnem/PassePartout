"""
Pydantic models for the simplified Roam API
"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class RoamRequest(BaseModel):
    """Request model for Roam API"""

    coordinates: str  # e.g., "43.6426, -79.3871"
    context: Optional[list[dict]] = None  # Optional chat history for Gemini context


class RoamResponse(BaseModel):
    """Response model for Roam API"""

    summary: str


class RoutePoint(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class RouteRequest(BaseModel):
    start: RoutePoint
    end: RoutePoint
    waypoints: Optional[List[RoutePoint]] = None
    categories: Optional[List[str]] = None
    context: Optional[List[Dict]] = None


class RouteResponse(BaseModel):
    route: List[RoutePoint]
    summary: Optional[str] = None
    is_chatbot_response: Optional[bool] = False
    chatbot_response: Optional[str] = None
