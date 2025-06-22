"""
Simple test script for the simplified Roam feature
"""

import asyncio
import time
import os
from dotenv import load_dotenv
from roam_service import RoamService
from models import RoamRequest

# Load environment variables from .env file
load_dotenv()

async def test_simplified_roam():
    """Test the simplified Roam feature"""
    print("🧪 Testing Simplified Roam Feature")
    print("=" * 50)
    
    roam_service = RoamService()
    
    # Test cases with coordinate strings
    test_cases = [
        {
            "name": "Toronto CN Tower",
            "coordinates": "43.6426, -79.3871"
        },
        {
            "name": "New York Times Square", 
            "coordinates": "40.7580, -73.9855"
        },
        {
            "name": "London Big Ben",
            "coordinates": "51.4994, -0.1245"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📍 Test {i}: {test_case['name']}")
        print(f"   Coordinates: {test_case['coordinates']}")
        
        start_time = time.time()
        
        try:
            request = RoamRequest(coordinates=test_case["coordinates"])
            response = await roam_service.get_roam_with_fallback(request)
            
            elapsed_time = (time.time() - start_time) * 1000
            
            print(f"   ⏱️ Response time: {elapsed_time:.1f}ms")
            print(f"   📝 Summary:")
            print(f"      {response.summary}")
            
            # Check if this is a fallback response
            if "Welcome to this amazing area! This location offers incredible opportunities for exploration" in response.summary:
                print("   🔄 DETECTED: Using fallback response (Gemini API likely failed)")
            elif "Welcome to this exciting area! This location offers amazing opportunities for visitors" in response.summary:
                print("   🔄 DETECTED: Using fallback response (Gemini API likely failed)")
            else:
                print("   🤖 DETECTED: Using actual Gemini API response")
            
            # Performance check
            if elapsed_time > 5000:
                print(f"   ⚠️ WARNING: Response time ({elapsed_time:.1f}ms) is quite slow")
            else:
                print(f"   ✅ Performance: {elapsed_time:.1f}ms (reasonable)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print(f"\n✅ Simplified Roam feature testing complete!")


async def test_gemini_api_directly():
    """Test Gemini API directly to see if it's working"""
    print("\n🧪 Testing Gemini API Directly")
    print("=" * 50)
    
    try:
        from roam_summary_generator import RoamSummaryGenerator
        
        generator = RoamSummaryGenerator()
        coordinates = "43.6426, -79.3871"
        
        print(f"📍 Testing direct Gemini API call for: {coordinates}")
        
        summary = generator.generate_tour_summary(coordinates)
        
        print(f"✅ Gemini API Response:")
        print(f"   Summary: {summary}")
        
        # Check if this is a fallback
        if "Welcome to this amazing area! This location offers incredible opportunities for exploration" in summary:
            print("   🔄 DETECTED: Using fallback response")
        elif "Welcome to this exciting area! This location offers amazing opportunities for visitors" in summary:
            print("   🔄 DETECTED: Using fallback response")
        else:
            print("   🤖 DETECTED: Using actual Gemini API response")
            
    except Exception as e:
        print(f"❌ Error testing Gemini API directly: {e}")


if __name__ == "__main__":
    print("🚀 Starting Simplified Roam Feature Tests")
    print("Make sure you have the following environment variables set:")
    print("- GEMINI_API_KEY (for Gemini API)")
    print()
    
    # Run tests
    asyncio.run(test_simplified_roam())
    asyncio.run(test_gemini_api_directly()) 