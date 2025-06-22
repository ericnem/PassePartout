#!/usr/bin/env python3
"""
Test script for EarSightAI MVP backend
"""
import asyncio
import json
import os

from fastapi.testclient import TestClient
from main import app
from overpass_client import OverpassClient


def test_geocoding():
    """Test the new geocoding functionality"""
    print("🔍 Testing geocoding functionality...")
    
    overpass_client = OverpassClient()
    
    # Test locations
    test_locations = [
        "LA",
        "Los Angeles", 
        "Paris",
        "Toronto",
        "New York",
        "San Francisco"
    ]
    
    for location in test_locations:
        print(f"\n📍 Testing geocoding for: '{location}'")
        coords = overpass_client.geocode_location(location)
        print(f"   Result: {coords}")
        
        # Test if coordinates have POIs
        has_pois = overpass_client.validate_coordinates_have_pois(coords["lat"], coords["lng"])
        print(f"   Has POIs: {has_pois}")


def test_mvp_backend():
    """Test the MVP backend functionality"""
    client = TestClient(app)

    # Test 1: Health check
    print("🔍 Testing health check...")
    response = client.get("/health")
    print(f"Health check status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")

    # Test 2: Route generation with LA
    print("\n🔍 Testing route generation with LA...")
    test_request = {
        "input_text": "Plan a 3 km walking tour starting at LA and visiting museums.",
        "context": [
            {"role": "user", "content": "I want to see some museums in LA."},
            {
                "role": "assistant",
                "content": "Sure! LA has many great museums. Would you like a walking tour?",
            },
        ],
    }

    response = client.post("/generate-route", json=test_request)
    print(f"Route generation status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ Route generation successful!")
        print(f"Route ID: {data['route']['id']}")
        print(f"Total distance: {data['total_distance_km']:.2f} km")
        print(f"Number of points: {len(data['points'])}")
        print(f"Message: {data['message']}")

        # Print first few points
        print("\n📍 Route points:")
        for i, point in enumerate(data["points"][:3]):
            print(f"  {i+1}. {point['name']} ({point['lat']:.4f}, {point['lng']:.4f})")
            print(f"     Category: {point['category']}")
            print(f"     Script: {point['script'][:100]}...")

        # Check GeoJSON structure
        geojson = data["geojson"]
        print(f"\n🗺️ GeoJSON features: {len(geojson['features'])}")

        # Save response to file for inspection
        with open("test_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print("💾 Full response saved to test_response.json")

    else:
        print(f"❌ Route generation failed: {response.text}")

    # Test 3: Root endpoint
    print("\n🔍 Testing root endpoint...")
    response = client.get("/")
    print(f"Root endpoint status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Root endpoint working")
    else:
        print("❌ Root endpoint failed")


if __name__ == "__main__":
    # Check if GEMINI_API_KEY is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ Warning: GEMINI_API_KEY not set. Some features may not work.")
        print("Set it with: export GEMINI_API_KEY='your_key_here'")

    # Test geocoding first
    test_geocoding()
    
    # Then test the full backend
    test_mvp_backend()
