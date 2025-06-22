"""
Overpass API client to fetch POIs from OpenStreetMap
"""

import time
from typing import Any, Dict, List
import os
import json

import requests
import google.generativeai as genai


class OverpassClient:
    """Client for Overpass API to fetch POIs"""

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self):
        self.session = requests.Session()
        # Add headers to avoid rate limiting
        self.session.headers.update(
            {"User-Agent": "EarSightAI/1.0 (https://github.com/your-repo)"}
        )
        # Initialize Gemini for location parsing
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        except Exception as e:
            print(f"Warning: Could not initialize Gemini model: {e}")
            self.gemini_model = None

    def get_pois(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        categories: List[str],
        start_location: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Get POIs from OpenStreetMap using Overpass API

        Args:
            lat: Center latitude
            lng: Center longitude
            radius_km: Search radius in kilometers
            categories: List of POI categories to search for
            start_location: The name of the starting location

        Returns:
            List of POI dictionaries
        """
        pois = []

        # Map categories to OSM tags
        category_mapping = {
            "monuments": [
                "tourism=attraction",
                "historic=monument",
                "historic=memorial",
            ],
            "museums": ["tourism=museum"],
            "parks": ["leisure=park", "leisure=garden"],
            "restaurants": ["amenity=restaurant", "amenity=cafe"],
            "shopping": [
                "shop=mall",
                "shop=supermarket",
                "shop=clothes",
                "shop=gift",
                "shop=convenience",
                "shop=department_store",
                "shop=bakery",
                "shop=butcher",
                "shop=bookstore",
                "shop=florist",
                "shop=shoes",
                "shop=beauty",
            ],
            "historical": ["historic=*"],
            "cultural": [
                "tourism=attraction",
                "amenity=theatre",
                "amenity=cinema",
                "amenity=arts_centre",
            ],
            "art galleries": [
                "tourism=gallery",
                "tourism=museum",
                "amenity=arts_centre",
            ],
            "cafes": ["amenity=cafe", "amenity=coffee_shop"],
            "bars": ["amenity=bar", "amenity=pub"],
            "libraries": ["amenity=library"],
            "churches": ["amenity=place_of_worship", "historic=church"],
            "universities": ["amenity=university", "amenity=college"],
            "hotels": ["tourism=hotel", "tourism=hostel", "tourism=motel"],
            "markets": ["amenity=marketplace", "shop=supermarket"],
            "theatres": ["amenity=theatre"],
            "cinemas": ["amenity=cinema"],
            "playgrounds": ["leisure=playground"],
            "gyms": ["leisure=fitness_centre", "leisure=sports_centre", "amenity=gym"],
            "pharmacies": ["amenity=pharmacy"],
            "hospitals": ["amenity=hospital"],
            "attractions": ["tourism=attraction"],
        }

        for category in categories:
            if category in category_mapping:
                tags = category_mapping[category]
                for tag in tags:
                    category_pois = self._query_overpass(lat, lng, radius_km, tag)
                    pois.extend(category_pois)

        # Remove duplicates and limit results
        unique_pois = []
        seen_names = set()
        cap = 10
        for poi in pois:
            if poi["name"] not in seen_names and len(unique_pois) < cap:
                unique_pois.append(poi)
                seen_names.add(poi["name"])

        # If no POIs found, try generating them with Gemini
        if not unique_pois and start_location:
            print("[INFO] No POIs found from Overpass, trying Gemini generation...")
            unique_pois = self._generate_pois_with_gemini(start_location, categories)

        # If still no POIs, use hardcoded mock data as a final resort
        if not unique_pois:
            print("[INFO] Gemini generation failed, using default mock data for testing")
            unique_pois = self._get_mock_pois(lat, lng, categories)

        return unique_pois

    def _get_mock_pois(
        self, lat: float, lng: float, categories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get mock POIs for testing when Overpass API fails
        """
        mock_pois = []

        # Toronto area mock POIs
        if "monuments" in categories or "historical" in categories:
            mock_pois.extend(
                [
                    {
                        "name": "CN Tower",
                        "lat": 43.6426,
                        "lng": -79.3871,
                        "category": "tourism",
                        "tags": {"tourism": "attraction", "name": "CN Tower"},
                    },
                    {
                        "name": "Casa Loma",
                        "lat": 43.6780,
                        "lng": -79.4095,
                        "category": "historic",
                        "tags": {"historic": "castle", "name": "Casa Loma"},
                    },
                    {
                        "name": "Royal Ontario Museum",
                        "lat": 43.6677,
                        "lng": -79.3948,
                        "category": "tourism",
                        "tags": {"tourism": "museum", "name": "Royal Ontario Museum"},
                    },
                    {
                        "name": "Art Gallery of Ontario",
                        "lat": 43.6537,
                        "lng": -79.3922,
                        "category": "tourism",
                        "tags": {"tourism": "museum", "name": "Art Gallery of Ontario"},
                    },
                    {
                        "name": "Nathan Phillips Square",
                        "lat": 43.6532,
                        "lng": -79.3832,
                        "category": "leisure",
                        "tags": {"leisure": "park", "name": "Nathan Phillips Square"},
                    },
                ]
            )

        # Remove duplicates
        unique_mock_pois = []
        seen_names = set()
        for poi in mock_pois:
            if poi["name"] not in seen_names:
                unique_mock_pois.append(poi)
                seen_names.add(poi["name"])

        return unique_mock_pois[:10]  # Cap at 10 POIs

    def _query_overpass(
        self, lat: float, lng: float, radius_km: float, tag: str
    ) -> List[Dict[str, Any]]:
        """
        Query Overpass API for specific tag

        Args:
            lat: Center latitude
            lng: Center longitude
            radius_km: Search radius in kilometers
            tag: OSM tag to search for (format: "key=value")

        Returns:
            List of POI dictionaries
        """
        # Convert radius to meters
        radius_m = radius_km * 1000

        # Parse the tag into key and value
        if "=" in tag:
            key, value = tag.split("=", 1)
            if value == "*":
                # For wildcard searches, use just the key
                query = f"""
                [out:json][timeout:25];
                (
                  node["{key}"](around:{radius_m},{lat},{lng});
                  way["{key}"](around:{radius_m},{lat},{lng});
                  relation["{key}"](around:{radius_m},{lat},{lng});
                );
                out center;
                """
            else:
                # For specific value searches, use key=value syntax
                query = f"""
                [out:json][timeout:25];
                (
                  node["{key}"="{value}"](around:{radius_m},{lat},{lng});
                  way["{key}"="{value}"](around:{radius_m},{lat},{lng});
                  relation["{key}"="{value}"](around:{radius_m},{lat},{lng});
                );
                out center;
                """
        else:
            # If no equals sign, treat as just a key
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
            response = self.session.get(self.OVERPASS_URL, params={"data": query})
            response.raise_for_status()

            data = response.json()
            pois = []

            for element in data.get("elements", []):
                if element["type"] == "node":
                    lat_elem = element["lat"]
                    lng_elem = element["lon"]
                elif element["type"] == "way":
                    # Use center coordinates for ways
                    lat_elem = element["center"]["lat"]
                    lng_elem = element["center"]["lon"]
                else:
                    continue

                name = element.get("tags", {}).get("name", "Unnamed Location")

                pois.append(
                    {
                        "name": name,
                        "lat": lat_elem,
                        "lng": lng_elem,
                        "category": tag.split("=")[0] if "=" in tag else tag,
                        "tags": element.get("tags", {}),
                    }
                )

            return pois

        except Exception as e:
            print(f"Error querying Overpass API: {e}")
            return []

    def geocode_location(self, location_name: str) -> Dict[str, float]:
        """
        Geocode a location name to coordinates using multiple methods

        Args:
            location_name: Name of the location

        Returns:
            Dictionary with lat and lng
        """
        print(f"[INFO] Geocoding location: '{location_name}'")
        
        # Method 1: Try Gemini-based geocoding first
        gemini_coords = self.geocode_location_with_gemini(location_name)
        if gemini_coords:
            # Validate that the coordinates have POIs
            if self.validate_coordinates_have_pois(gemini_coords["lat"], gemini_coords["lng"]):
                print(f"[INFO] Using Gemini coordinates for '{location_name}': {gemini_coords}")
                return gemini_coords
            else:
                print(f"[WARNING] Gemini coordinates for '{location_name}' have no POIs, trying fallback methods")

        # Method 2: Check common location mappings
        location_mappings = {
            "cn tower": {"lat": 43.6426, "lng": -79.3871},
            "toronto": {"lat": 43.6532, "lng": -79.3832},
            "paris": {"lat": 48.8566, "lng": 2.3522},
            "london": {"lat": 51.5074, "lng": -0.1278},
            "new york": {"lat": 40.7128, "lng": -74.0060},
            "los angeles": {"lat": 34.0522, "lng": -118.2437},
            "la": {"lat": 34.0522, "lng": -118.2437},
            "san francisco": {"lat": 37.7749, "lng": -122.4194},
            "sf": {"lat": 37.7749, "lng": -122.4194},
            "washington dc": {"lat": 38.9072, "lng": -77.0369},
            "dc": {"lat": 38.9072, "lng": -77.0369},
            "las vegas": {"lat": 36.1699, "lng": -115.1398},
            "vegas": {"lat": 36.1699, "lng": -115.1398},
            "city center": {"lat": 43.6532, "lng": -79.3832},  # Toronto default
        }

        # Check if we have a direct mapping
        location_lower = location_name.lower()
        for key, coords in location_mappings.items():
            if key in location_lower:
                print(f"[INFO] Using mapped coordinates for '{location_name}': {coords}")
                return coords

        # Method 3: Try Nominatim with better headers
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location_name, "format": "json", "limit": 1}

        headers = {
            "User-Agent": "EarSightAI/1.0 (https://github.com/your-repo)",
            "Accept": "application/json",
        }

        try:
            response = self.session.get(nominatim_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if data:
                coords = {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
                print(f"[INFO] Using Nominatim coordinates for '{location_name}': {coords}")
                return coords

        except Exception as e:
            print(f"Error geocoding location with Nominatim: {e}")

        # Default to Toronto coordinates
        print(f"[WARNING] Could not geocode '{location_name}', defaulting to Toronto")
        return {"lat": 43.6532, "lng": -79.3832}

    def geocode_location_with_gemini(self, location_name: str) -> Dict[str, float]:
        """
        Use Gemini to get precise coordinates for a location
        
        Args:
            location_name: Name of the location (e.g., "LA", "Los Angeles", "Paris")
            
        Returns:
            Dictionary with lat and lng, or None if failed
        """
        if not self.gemini_model:
            return None
            
        prompt = f"""
        Given the location name "{location_name}", provide the most accurate coordinates.
        
        Return ONLY a JSON object with this exact format:
        {{
            "lat": <latitude as float>,
            "lng": <longitude as float>,
            "confidence": <confidence level 0-1>
        }}
        
        Rules:
        - Use the most common/popular interpretation of the location name
        - For "LA" or "L.A.", use Los Angeles, California
        - For "NYC" or "NY", use New York City
        - For "SF", use San Francisco
        - For "DC", use Washington, D.C.
        - For "Vegas", use Las Vegas
        - Use city center coordinates when possible
        - Confidence should be high (0.8+) for well-known cities
        - Return only valid JSON, no other text
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            json_text = response.text.strip()
            
            # Clean up JSON response
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
                
            result = json.loads(json_text)
            
            # Validate coordinates
            lat = result.get("lat")
            lng = result.get("lng")
            confidence = result.get("confidence", 0)
            
            if (lat is not None and lng is not None and 
                -90 <= lat <= 90 and -180 <= lng <= 180 and
                confidence >= 0.5):
                
                print(f"[INFO] Gemini geocoded '{location_name}' to ({lat}, {lng}) with confidence {confidence}")
                return {"lat": float(lat), "lng": float(lng)}
                
        except Exception as e:
            print(f"[WARNING] Gemini geocoding failed for '{location_name}': {e}")
            
        return None

    def validate_coordinates_have_pois(self, lat: float, lng: float, radius_km: float = 2.0) -> bool:
        """
        Check if coordinates have any POIs in the area
        
        Args:
            lat: Latitude
            lng: Longitude  
            radius_km: Search radius
            
        Returns:
            True if POIs found, False otherwise
        """
        # Try a simple POI search to validate coordinates
        test_pois = self._query_overpass(lat, lng, radius_km, "tourism=attraction")
        return len(test_pois) > 0

    def _generate_pois_with_gemini(
        self, location_name: str, categories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Use Gemini to generate a list of POIs for a given location when Overpass fails.
        """
        if not self.gemini_model:
            return []

        print(f"[INFO] Using Gemini to generate mock POIs for {location_name}")
        prompt = f"""
        Generate a list of 3-5 famous points of interest for the following location and categories.
        
        Location: "{location_name}"
        Categories: {categories}

        Return ONLY a valid JSON array with this exact format:
        [
            {{
                "name": "<POI Name>",
                "lat": <latitude as float>,
                "lng": <longitude as float>,
                "category": "<one of the input categories>",
                "tags": {{ "name": "<POI Name>" }}
            }}
        ]
        
        Rules:
        - Return only the JSON array, no other text or explanations.
        - Ensure coordinates are accurate.
        - The "category" field must be one of the provided categories.
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            json_text = response.text.strip()
            
            # Clean up JSON response
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]

            pois = json.loads(json_text)

            # Basic validation
            if isinstance(pois, list) and all("name" in p for p in pois):
                print(f"[INFO] Gemini successfully generated {len(pois)} POIs.")
                return pois
            return []
        except Exception as e:
            print(f"[WARNING] Gemini POI generation failed: {e}")
            return []
