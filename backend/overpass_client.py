"""
Overpass API client to fetch POIs from OpenStreetMap
"""

import time
from typing import Any, Dict, List

import requests


class OverpassClient:
    """Client for Overpass API to fetch POIs"""

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self):
        self.session = requests.Session()
        # Add headers to avoid rate limiting
        self.session.headers.update(
            {"User-Agent": "EarSightAI/1.0 (https://github.com/your-repo)"}
        )

    def get_pois(
        self, lat: float, lng: float, radius_km: float, categories: List[str]
    ) -> List[Dict[str, Any]]:
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

        # If no POIs found, use mock data for testing
        if not unique_pois:
            print("No POIs found from Overpass API, using mock data for testing")
            unique_pois = self._get_mock_pois(lat, lng, categories)

        return unique_pois

    def _get_mock_pois(
        self, lat: float, lng: float, categories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get mock POIs for testing when Overpass API fails

        Args:
            lat: Center latitude
            lng: Center longitude
            categories: List of POI categories

        Returns:
            List of mock POI dictionaries
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
        if (
            "museums" in categories
            or "art galleries" in categories
            or "cultural" in categories
        ):
            mock_pois.extend(
                [
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
                        "name": "Power Plant Contemporary Art Gallery",
                        "lat": 43.6386,
                        "lng": -79.3806,
                        "category": "tourism",
                        "tags": {
                            "tourism": "gallery",
                            "name": "Power Plant Contemporary Art Gallery",
                        },
                    },
                ]
            )
        if "parks" in categories:
            mock_pois.extend(
                [
                    {
                        "name": "High Park",
                        "lat": 43.6467,
                        "lng": -79.4654,
                        "category": "leisure",
                        "tags": {"leisure": "park", "name": "High Park"},
                    },
                    {
                        "name": "Trinity Bellwoods Park",
                        "lat": 43.6471,
                        "lng": -79.4207,
                        "category": "leisure",
                        "tags": {"leisure": "park", "name": "Trinity Bellwoods Park"},
                    },
                ]
            )
        if "restaurants" in categories or "cafes" in categories or "bars" in categories:
            mock_pois.extend(
                [
                    {
                        "name": "St. Lawrence Market",
                        "lat": 43.6487,
                        "lng": -79.3716,
                        "category": "market",
                        "tags": {
                            "amenity": "marketplace",
                            "name": "St. Lawrence Market",
                        },
                    },
                    {
                        "name": "Dineen Coffee Co.",
                        "lat": 43.6525,
                        "lng": -79.3791,
                        "category": "cafe",
                        "tags": {"amenity": "cafe", "name": "Dineen Coffee Co."},
                    },
                    {
                        "name": "Bar Hop",
                        "lat": 43.6469,
                        "lng": -79.3957,
                        "category": "bar",
                        "tags": {"amenity": "bar", "name": "Bar Hop"},
                    },
                ]
            )
        if "shopping" in categories or "markets" in categories:
            mock_pois.extend(
                [
                    {
                        "name": "Eaton Centre",
                        "lat": 43.6544,
                        "lng": -79.3807,
                        "category": "shopping",
                        "tags": {"shop": "mall", "name": "Eaton Centre"},
                    },
                    {
                        "name": "Kensington Market",
                        "lat": 43.6540,
                        "lng": -79.4022,
                        "category": "market",
                        "tags": {"amenity": "marketplace", "name": "Kensington Market"},
                    },
                ]
            )
        if "libraries" in categories:
            mock_pois.append(
                {
                    "name": "Toronto Reference Library",
                    "lat": 43.6717,
                    "lng": -79.3860,
                    "category": "library",
                    "tags": {"amenity": "library", "name": "Toronto Reference Library"},
                }
            )
        if "churches" in categories:
            mock_pois.append(
                {
                    "name": "St. Michael's Cathedral Basilica",
                    "lat": 43.6540,
                    "lng": -79.3777,
                    "category": "church",
                    "tags": {
                        "amenity": "place_of_worship",
                        "name": "St. Michael's Cathedral Basilica",
                    },
                }
            )
        if "universities" in categories:
            mock_pois.append(
                {
                    "name": "University of Toronto",
                    "lat": 43.6629,
                    "lng": -79.3957,
                    "category": "university",
                    "tags": {"amenity": "university", "name": "University of Toronto"},
                }
            )
        if "hotels" in categories:
            mock_pois.append(
                {
                    "name": "Fairmont Royal York",
                    "lat": 43.6454,
                    "lng": -79.3807,
                    "category": "hotel",
                    "tags": {"tourism": "hotel", "name": "Fairmont Royal York"},
                }
            )
        if "theatres" in categories:
            mock_pois.append(
                {
                    "name": "Princess of Wales Theatre",
                    "lat": 43.6465,
                    "lng": -79.3902,
                    "category": "theatre",
                    "tags": {"amenity": "theatre", "name": "Princess of Wales Theatre"},
                }
            )
        if "cinemas" in categories:
            mock_pois.append(
                {
                    "name": "TIFF Bell Lightbox",
                    "lat": 43.6465,
                    "lng": -79.3902,
                    "category": "cinema",
                    "tags": {"amenity": "cinema", "name": "TIFF Bell Lightbox"},
                }
            )
        if "playgrounds" in categories:
            mock_pois.append(
                {
                    "name": "Grange Park Playground",
                    "lat": 43.6530,
                    "lng": -79.3910,
                    "category": "playground",
                    "tags": {"leisure": "playground", "name": "Grange Park Playground"},
                }
            )
        if "gyms" in categories:
            mock_pois.append(
                {
                    "name": "YMCA Central Toronto",
                    "lat": 43.6612,
                    "lng": -79.3832,
                    "category": "gym",
                    "tags": {
                        "leisure": "fitness_centre",
                        "name": "YMCA Central Toronto",
                    },
                }
            )
        if "pharmacies" in categories:
            mock_pois.append(
                {
                    "name": "Shoppers Drug Mart",
                    "lat": 43.6532,
                    "lng": -79.3832,
                    "category": "pharmacy",
                    "tags": {"amenity": "pharmacy", "name": "Shoppers Drug Mart"},
                }
            )
        if "hospitals" in categories:
            mock_pois.append(
                {
                    "name": "Toronto General Hospital",
                    "lat": 43.6588,
                    "lng": -79.3890,
                    "category": "hospital",
                    "tags": {"amenity": "hospital", "name": "Toronto General Hospital"},
                }
            )
        if "attractions" in categories:
            mock_pois.append(
                {
                    "name": "Ripley's Aquarium of Canada",
                    "lat": 43.6424,
                    "lng": -79.3860,
                    "category": "attraction",
                    "tags": {
                        "tourism": "attraction",
                        "name": "Ripley's Aquarium of Canada",
                    },
                }
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
        Geocode a location name to coordinates using Nominatim

        Args:
            location_name: Name of the location

        Returns:
            Dictionary with lat and lng
        """
        # Common location mappings
        location_mappings = {
            "cn tower": {"lat": 43.6426, "lng": -79.3871},
            "toronto": {"lat": 43.6532, "lng": -79.3832},
            "paris": {"lat": 48.8566, "lng": 2.3522},
            "london": {"lat": 51.5074, "lng": -0.1278},
            "new york": {"lat": 40.7128, "lng": -74.0060},
            "city center": {"lat": 43.6532, "lng": -79.3832},  # Toronto default
        }

        # Check if we have a direct mapping
        location_lower = location_name.lower()
        for key, coords in location_mappings.items():
            if key in location_lower:
                return coords

        # Try Nominatim with better headers
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
                return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}

        except Exception as e:
            print(f"Error geocoding location: {e}")

        # Default to Toronto coordinates
        return {"lat": 43.6532, "lng": -79.3832}
