"""
Pydantic models for the MVP backend
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from geojson import Feature, FeatureCollection, Point, LineString

class RouteRequest(BaseModel):
    input_text: str

class RoutePoint(BaseModel):
    name: str
    lat: float
    lng: float
    script: str
    category: str

class RouteResponse(BaseModel):
    route: Dict[str, Any]
    points: List[RoutePoint]
    geojson: Dict[str, Any]
    total_distance_km: float
    success: bool
    message: str 