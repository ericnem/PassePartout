#!/usr/bin/env python3
"""
Debug script to test TSP solver with actual data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_parser import TextParser
from overpass_client import OverpassClient
from osrm_client import OSRMClient
from tsp_solver import TSPSolver

def debug_tsp():
    """Debug TSP solver with actual data"""
    print("🔍 Debugging TSP solver...")
    
    # Initialize components
    text_parser = TextParser()
    overpass_client = OverpassClient()
    osrm_client = OSRMClient()
    tsp_solver = TSPSolver()
    
    # Test input
    test_input = "I want a 3 km walk starting at CN Tower visiting famous monuments"
    
    try:
        # Step 1: Parse input
        print("Step 1: Parsing input...")
        params = text_parser.parse_input(test_input)
        print(f"Parsed params: {params}")
        
        # Step 2: Geocode
        print("Step 2: Geocoding...")
        start_coords = overpass_client.geocode_location(params["start_location"])
        print(f"Start coords: {start_coords}")
        
        # Step 3: Get POIs
        print("Step 3: Getting POIs...")
        pois = overpass_client.get_pois(
            start_coords["lat"],
            start_coords["lng"],
            5,  # 5km radius
            params["preferences"]
        )
        print(f"Found {len(pois)} POIs")
        
        if not pois:
            print("No POIs found, using mock data...")
            # Use mock POIs for testing
            pois = [
                {"name": "Ripley's Aquarium", "lat": 43.6426, "lng": -79.3871, "category": "attraction"},
                {"name": "Rogers Centre", "lat": 43.6417, "lng": -79.3892, "category": "sports"},
                {"name": "Union Station", "lat": 43.6454, "lng": -79.3806, "category": "transport"},
                {"name": "St. Lawrence Market", "lat": 43.6487, "lng": -79.3735, "category": "food"},
                {"name": "Distillery District", "lat": 43.6508, "lng": -79.3592, "category": "culture"}
            ]
        
        # Step 4: Prepare points
        print("Step 4: Preparing points...")
        all_points = [(start_coords["lat"], start_coords["lng"])]
        poi_points = [(poi["lat"], poi["lng"]) for poi in pois]
        all_points.extend(poi_points)
        print(f"Total points: {len(all_points)}")
        print(f"Points: {all_points}")
        
        # Step 5: Get distance matrix
        print("Step 5: Getting distance matrix...")
        distance_matrix = osrm_client.get_distance_matrix(all_points)
        print(f"Distance matrix shape: {len(distance_matrix)}x{len(distance_matrix[0]) if distance_matrix else 0}")
        
        # Print first few rows of distance matrix
        print("Distance matrix (first 3 rows):")
        for i, row in enumerate(distance_matrix[:3]):
            print(f"Row {i}: {row[:3]}...")
        
        # Check for invalid values
        print("Checking for invalid values in distance matrix...")
        for i, row in enumerate(distance_matrix):
            for j, val in enumerate(row):
                if not isinstance(val, (int, float)) or val < 0:
                    print(f"Invalid value at [{i}][{j}]: {val} (type: {type(val)})")
        
        # Step 6: Test TSP solver
        print("Step 6: Testing TSP solver...")
        max_distance = params["max_distance_km"]
        print(f"Max distance: {max_distance}km")
        
        route_indices = tsp_solver.solve_tsp(distance_matrix, max_distance)
        print(f"Route indices: {route_indices}")
        
        # Step 7: Calculate route distance
        total_distance = tsp_solver.get_route_distance(route_indices, distance_matrix)
        print(f"Total route distance: {total_distance:.2f}km")
        
        print("✅ TSP debugging completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during TSP debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tsp() 