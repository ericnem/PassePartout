#!/usr/bin/env python3
"""
Debug script to test Overpass API directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from overpass_client import OverpassClient
import requests
import json

def debug_overpass():
    """Debug Overpass API queries"""
    print("🔍 Debugging Overpass API...")
    
    overpass_client = OverpassClient()
    
    # Test coordinates (CN Tower area)
    lat = 43.6426
    lng = -79.3871
    radius_km = 5
    
    print(f"Testing coordinates: {lat}, {lng}")
    print(f"Search radius: {radius_km}km")
    
    # Test different OSM tags
    test_tags = [
        "tourism=attraction",
        "historic=monument", 
        "historic=memorial",
        "tourism=museum",
        "leisure=park",
        "amenity=restaurant",
        "shop=*"
    ]
    
    for tag in test_tags:
        print(f"\n--- Testing tag: {tag} ---")
        
        # Test the Overpass query directly
        radius_m = radius_km * 1000
        query = f"""
        [out:json][timeout:25];
        (
          node["{tag}"](around:{radius_m},{lat},{lng});
          way["{tag}"](around:{radius_m},{lat},{lng});
          relation["{tag}"](around:{radius_m},{lat},{lng});
        );
        out center;
        """
        
        print(f"Query: {query.strip()}")
        
        try:
            response = requests.get(
                "https://overpass-api.de/api/interpreter",
                params={"data": query},
                headers={'User-Agent': 'EarSightAI/1.0 (https://github.com/your-repo)'}
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                print(f"Found {len(elements)} elements")
                
                if elements:
                    print("Sample elements:")
                    for i, element in enumerate(elements[:3]):  # Show first 3
                        print(f"  {i+1}. Type: {element.get('type')}")
                        print(f"     Tags: {element.get('tags', {})}")
                        if element.get('type') == 'node':
                            print(f"     Coords: {element.get('lat')}, {element.get('lon')}")
                        elif element.get('type') == 'way':
                            print(f"     Center: {element.get('center', {})}")
                else:
                    print("No elements found")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Test the client's get_pois method
    print(f"\n--- Testing client.get_pois method ---")
    try:
        pois = overpass_client.get_pois(lat, lng, radius_km, ["monuments"])
        print(f"Client found {len(pois)} POIs")
        
        if pois:
            print("POIs found:")
            for i, poi in enumerate(pois):
                print(f"  {i+1}. {poi['name']} ({poi['lat']}, {poi['lng']}) - {poi['category']}")
        else:
            print("No POIs found by client method")
            
    except Exception as e:
        print(f"Error in client method: {e}")

def test_broader_search():
    """Test with broader search criteria"""
    print(f"\n🔍 Testing broader search...")
    
    overpass_client = OverpassClient()
    lat = 43.6426
    lng = -79.3871
    
    # Test with larger radius and broader tags
    radius_km = 10
    
    # Broader tag combinations
    broader_tags = [
        "tourism=*",
        "historic=*", 
        "leisure=*",
        "amenity=*"
    ]
    
    for tag in broader_tags:
        print(f"\n--- Testing broader tag: {tag} ---")
        
        radius_m = radius_km * 1000
        query = f"""
        [out:json][timeout:25];
        (
          node["{tag}"](around:{radius_m},{lat},{lng});
          way["{tag}"](around:{radius_m},{lat},{lng});
          relation["{tag}"](around:{radius_m},{lat},{lng});
        );
        out center;
        """
        
        try:
            response = requests.get(
                "https://overpass-api.de/api/interpreter",
                params={"data": query},
                headers={'User-Agent': 'EarSightAI/1.0 (https://github.com/your-repo)'}
            )
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                print(f"Found {len(elements)} elements with {tag}")
                
                if elements:
                    # Show some sample elements
                    for i, element in enumerate(elements[:5]):
                        tags = element.get('tags', {})
                        name = tags.get('name', 'Unnamed')
                        print(f"  {i+1}. {name} - {tags}")
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

def test_simple_queries():
    """Test with simpler queries to isolate the issue"""
    print(f"\n🔍 Testing simple queries...")
    
    lat = 43.6426
    lng = -79.3871
    radius_m = 5000
    
    # Test 1: Simple node query
    print("--- Test 1: Simple node query ---")
    query1 = f"""
    [out:json][timeout:25];
    node["tourism"](around:{radius_m},{lat},{lng});
    out;
    """
    
    try:
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query1},
            headers={'User-Agent': 'EarSightAI/1.0 (https://github.com/your-repo)'}
        )
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            print(f"Simple node query found {len(elements)} elements")
            
            if elements:
                for i, element in enumerate(elements[:3]):
                    print(f"  {i+1}. {element.get('tags', {})}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Bounding box query
    print("--- Test 2: Bounding box query ---")
    # Create a bounding box around the point
    bbox_lat_min = lat - 0.05  # ~5km
    bbox_lat_max = lat + 0.05
    bbox_lng_min = lng - 0.05
    bbox_lng_max = lng + 0.05
    
    query2 = f"""
    [out:json][timeout:25];
    (
      node["tourism"]({bbox_lat_min},{bbox_lng_min},{bbox_lat_max},{bbox_lng_max});
      way["tourism"]({bbox_lat_min},{bbox_lng_min},{bbox_lat_max},{bbox_lng_max});
    );
    out center;
    """
    
    try:
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query2},
            headers={'User-Agent': 'EarSightAI/1.0 (https://github.com/your-repo)'}
        )
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            print(f"Bounding box query found {len(elements)} elements")
            
            if elements:
                for i, element in enumerate(elements[:3]):
                    print(f"  {i+1}. {element.get('tags', {})}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test with a known working location (Paris)
    print("--- Test 3: Test with Paris coordinates ---")
    paris_lat = 48.8566
    paris_lng = 2.3522
    
    query3 = f"""
    [out:json][timeout:25];
    node["tourism"](around:{radius_m},{paris_lat},{paris_lng});
    out;
    """
    
    try:
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query3},
            headers={'User-Agent': 'EarSightAI/1.0 (https://github.com/your-repo)'}
        )
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            print(f"Paris query found {len(elements)} elements")
            
            if elements:
                for i, element in enumerate(elements[:3]):
                    print(f"  {i+1}. {element.get('tags', {})}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_overpass()
    test_broader_search()
    test_simple_queries() 