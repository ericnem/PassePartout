"""
Main FastAPI application for EarSightAI MVP backend
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from geojson import Feature, FeatureCollection, LineString, Point

# Import our modules
from models import RoutePoint, RouteRequest, RouteResponse
from osrm_client import OSRMClient
from overpass_client import OverpassClient
from script_generator import ScriptGenerator
from text_parser import TextParser
from tsp_solver import TSPSolver

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="EarSightAI Backend",
    description="A browser-based, audio-first tour-guide web app",
    version="1.0.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
text_parser = TextParser()
overpass_client = OverpassClient()
osrm_client = OSRMClient()
tsp_solver = TSPSolver()
script_generator = ScriptGenerator()


@app.get("/")
def read_root():
    return {
        "message": "EarSightAI Backend running!",
        "version": "1.0.0",
        "endpoints": {"generate_route": "POST /generate-route"},
    }


@app.post("/generate-route", response_model=RouteResponse)
async def generate_route(request: RouteRequest):
    """
    Generate an optimized route based on text input

    Args:
        request: RouteRequest containing input_text

    Returns:
        RouteResponse with optimized route, points, and GeoJSON
    """
    try:
        print(f"Processing request: {request.input_text}")

        # Step 1: Parse input text with Gemini
        print("Step 1: Parsing input text...")
        params = text_parser.parse_input(request.input_text)
        print(f"Parsed parameters: {params}")

        # Step 2: Geocode starting location
        print("Step 2: Geocoding starting location...")
        start_coords = overpass_client.geocode_location(params["start_location"])
        print(f"Starting coordinates: {start_coords}")

        # Step 3: Get POIs from Overpass API
        print("Step 3: Fetching POIs...")
        search_radius = min(
            params["max_distance_km"] * 2, 10
        )  # Search radius up to 10km
        pois = overpass_client.get_pois(
            start_coords["lat"],
            start_coords["lng"],
            search_radius,
            params["preferences"],
        )
        print(f"Found {len(pois)} POIs")

        if not pois:
            raise HTTPException(
                status_code=400,
                detail="No points of interest found for the given preferences",
            )

        # Step 4: Prepare points for TSP (including start location)
        print("Step 4: Preparing points for TSP...")
        all_points = [(start_coords["lat"], start_coords["lng"])]  # Start point
        poi_points = [(poi["lat"], poi["lng"]) for poi in pois]
        all_points.extend(poi_points)

        # Step 5: Get distance and duration matrices from OSRM
        print("Step 5: Getting distance and duration matrices...")
        matrices = osrm_client.get_distance_matrix(all_points)
        distance_matrix = matrices["distance_matrix"]
        duration_matrix = matrices["duration_matrix"]

        # Step 6: Solve TSP with OR-Tools
        print("Step 6: Solving TSP...")
        route_indices = tsp_solver.solve_tsp(distance_matrix, params["max_distance_km"])
        print(f"Route indices: {route_indices}")

        # Step 7: Build optimized route
        print("Step 7: Building optimized route...")
        optimized_pois = []
        route_points = []

        for i, idx in enumerate(route_indices):
            if idx == 0:
                # Start location
                point = RoutePoint(
                    name=params["start_location"],
                    lat=start_coords["lat"],
                    lng=start_coords["lng"],
                    script=f"Welcome to {params['start_location']}! This is where your journey begins.",
                    category="start",
                )
            else:
                # POI - use fallback script to avoid rate limits
                poi = pois[idx - 1]
                
                # Only generate AI script for the first 3 POIs to avoid rate limits
                if i <= 3:
                    try:
                        script = script_generator.generate_script(poi)
                    except Exception as e:
                        print(f"Using fallback script for {poi['name']}: {e}")
                        script = f"Welcome to {poi['name']}! This is a great spot to explore and discover what makes Toronto special."
                else:
                    # Use simple fallback script for remaining POIs
                    script = f"Here's {poi['name']}, another interesting location on your walking tour of Toronto."
                
                point = RoutePoint(
                    name=poi["name"],
                    lat=poi["lat"],
                    lng=poi["lng"],
                    script=script,
                    category=poi["category"],
                )

            optimized_pois.append(
                poi
                if idx > 0
                else {
                    "name": params["start_location"],
                    "lat": start_coords["lat"],
                    "lng": start_coords["lng"],
                }
            )
            route_points.append(point)

        # Step 8: Get detailed route from OSRM
        print("Step 8: Getting detailed route...")
        route_coords = [(point.lat, point.lng) for point in route_points]
        route_details = osrm_client.get_route(route_coords)

        # Step 9: Create GeoJSON
        print("Step 9: Creating GeoJSON...")
        geojson = create_geojson(route_points, route_details)

        # Step 10: Calculate total distance
        total_distance = tsp_solver.get_route_distance(route_indices, distance_matrix)

        print(f"Route generation complete! Total distance: {total_distance:.2f}km")

        return RouteResponse(
            route={
                "id": datetime.now().isoformat(),
                "total_distance_km": total_distance,
                "estimated_duration_minutes": route_details.get(
                    "duration", total_distance * 12
                ),
                "waypoints": len(route_points),
                "created_at": datetime.now().isoformat(),
            },
            points=route_points,
            geojson=geojson,
            total_distance_km=total_distance,
            distance_matrix=distance_matrix,
            duration_matrix=duration_matrix,
            success=True,
            message=f"Generated route with {len(route_points)} waypoints covering {total_distance:.1f}km",
        )

    except Exception as e:
        print(f"Error generating route: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating route: {str(e)}")


def create_geojson(points: list[RoutePoint], route_details: dict) -> dict:
    """
    Create GeoJSON from route points and details

    Args:
        points: List of route points
        route_details: Route details from OSRM

    Returns:
        GeoJSON dictionary
    """
    features = []

    # Add point features
    for i, point in enumerate(points):
        feature = Feature(
            geometry=Point((point.lng, point.lat)),
            properties={
                "name": point.name,
                "category": point.category,
                "script": point.script,
                "order": i,
            },
        )
        features.append(feature)

    # Add route line if available
    if route_details.get("geometry"):
        # Convert OSRM geometry to GeoJSON format
        coordinates = []
        for coord in route_details["geometry"]:
            # OSRM returns [lng, lat], GeoJSON expects [lng, lat]
            coordinates.append(coord)

        route_feature = Feature(
            geometry=LineString(coordinates),
            properties={
                "name": "Walking Route",
                "distance_km": route_details.get("distance", 0),
                "duration_minutes": route_details.get("duration", 0),
            },
        )
        features.append(route_feature)

    return FeatureCollection(features)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
