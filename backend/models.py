"""
Pydantic models for the MVP backend
"""

from typing import Any, Dict, List, Optional

from geojson import Feature, FeatureCollection, LineString, Point
from pydantic import BaseModel


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
    distance_matrix: List[List[float]]
    duration_matrix: List[List[float]]
    success: bool
    message: str
