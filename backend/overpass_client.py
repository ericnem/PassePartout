"""
Overpass API client to fetch POIs from OpenStreetMap
"""
import requests
import time
from typing import List, Dict, Any

class OverpassClient:
    """Client for Overpass API to fetch POIs"""
    
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_pois(self, lat: float, lng: float, radius_km: float, categories: List[str]) -> List[Dict[str, Any]]:
        """
        Get POIs from OpenStreetMap using Overpass API
        
        Args:
            lat: Center latitude
            lng: Center longitude
            radius_km: Search radius in kilometers
            categories: List of POI categories to search for
            
        Returns:
            List of POI dictionaries
        """
        pois = []
        
        # Map categories to OSM tags
        category_mapping = {
            "monuments": ["tourism=attraction", "historic=monument", "historic=memorial"],
            "museums": ["tourism=museum"],
            "parks": ["leisure=park", "leisure=garden"],
            "restaurants": ["amenity=restaurant", "amenity=cafe"],
            "shopping": ["shop=*"],
            "historical": ["historic=*"],
            "cultural": ["tourism=attraction", "amenity=theatre", "amenity=cinema"]
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
        for poi in pois:
            if poi["name"] not in seen_names and len(unique_pois) < 20:
                unique_pois.append(poi)
                seen_names.add(poi["name"])
        
        return unique_pois
    
    def _query_overpass(self, lat: float, lng: float, radius_km: float, tag: str) -> List[Dict[str, Any]]:
        """
        Query Overpass API for specific tag
        
        Args:
            lat: Center latitude
            lng: Center longitude
            radius_km: Search radius in kilometers
            tag: OSM tag to search for
            
        Returns:
            List of POI dictionaries
        """
        # Convert radius to meters
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
                
                pois.append({
                    "name": name,
                    "lat": lat_elem,
                    "lng": lng_elem,
                    "category": tag.split("=")[0],
                    "tags": element.get("tags", {})
                })
            
            return pois
            
        except Exception as e:
            print(f"Error querying Overpass API: {e}")
            return []
    
    def geocode_location(self, location_name: str) -> Dict[str, float]:
        """
        Geocode a location name to coordinates using Nominatim
        
        Args:
            location_name: Name of the location
            
        Returns:
            Dictionary with lat and lng
        """
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_name,
            "format": "json",
            "limit": 1
        }
        
        try:
            response = self.session.get(nominatim_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return {
                    "lat": float(data[0]["lat"]),
                    "lng": float(data[0]["lon"])
                }
            
        except Exception as e:
            print(f"Error geocoding location: {e}")
        
        # Default to Toronto coordinates
        return {"lat": 43.6532, "lng": -79.3832} 