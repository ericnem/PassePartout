"""
OSRM client for walking distance calculations
"""

from typing import Any, Dict, List, Tuple

import requests


class OSRMClient:
    """Client for OSRM routing service"""

    OSRM_URL = "https://router.project-osrm.org/route/v1"

    def __init__(self):
        self.session = requests.Session()

    def get_distance_matrix(
        self, points: List[Tuple[float, float]]
    ) -> List[List[float]]:
        """
        Get distance matrix between all points using OSRM

        Args:
            points: List of (lat, lng) tuples

        Returns:
            Distance matrix (2D list of distances in km)
        """
        if len(points) < 2:
            return [[0.0]]

        # Build coordinates string for OSRM
        coords = ";".join([f"{lng},{lat}" for lat, lng in points])

        # Use the OSRM table service for distance matrix
        url = f"https://router.project-osrm.org/table/v1/driving/{coords}"
        params = {"annotations": "distance"}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            # Remove debug print, just raise if 'distances' is missing
            if data["code"] != "Ok" or "distances" not in data:
                raise Exception(
                    f"OSRM error: {data.get('message', 'No distances in response')}"
                )

            # Extract distances from response
            distances = data["distances"]

            # Convert to km and create matrix
            matrix = []
            for i, row in enumerate(distances):
                matrix_row = []
                for j, distance in enumerate(row):
                    if distance is None:
                        # If no route found, use straight-line distance as fallback
                        distance = self._haversine_distance(points[i], points[j])
                    else:
                        distance = distance / 1000  # Convert meters to km
                    matrix_row.append(distance)
                matrix.append(matrix_row)

            return matrix

        except Exception as e:
            print(f"Error getting distance matrix from OSRM: {e}")
            # Fallback to haversine distances
            return self._haversine_matrix(points)

    def get_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Get detailed route between points

        Args:
            points: List of (lat, lng) tuples in order

        Returns:
            Route information including geometry and distance
        """
        if len(points) < 2:
            return {"distance": 0.0, "geometry": []}

        # Build coordinates string for OSRM
        coords = ";".join([f"{lng},{lat}" for lat, lng in points])

        url = f"{self.OSRM_URL}/driving/{coords}"
        params = {"overview": "full", "geometries": "geojson"}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data["code"] != "Ok":
                raise Exception(f"OSRM error: {data.get('message', 'Unknown error')}")

            route = data["routes"][0]

            return {
                "distance": route["distance"] / 1000,  # Convert to km
                "duration": route["duration"] / 60,  # Convert to minutes
                "geometry": route["geometry"]["coordinates"],
            }

        except Exception as e:
            print(f"Error getting route from OSRM: {e}")
            # Fallback to simple route
            return self._simple_route(points)

    def _haversine_distance(
        self, point1: Tuple[float, float], point2: Tuple[float, float]
    ) -> float:
        """
        Calculate haversine distance between two points

        Args:
            point1: (lat, lng) tuple
            point2: (lat, lng) tuple

        Returns:
            Distance in kilometers
        """
        import math

        lat1, lng1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lng2 = math.radians(point2[0]), math.radians(point2[1])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        r = 6371

        return r * c

    def _haversine_matrix(self, points: List[Tuple[float, float]]) -> List[List[float]]:
        """
        Create distance matrix using haversine distances

        Args:
            points: List of (lat, lng) tuples

        Returns:
            Distance matrix
        """
        matrix = []
        for i, point1 in enumerate(points):
            row = []
            for j, point2 in enumerate(points):
                if i == j:
                    row.append(0.0)
                else:
                    row.append(self._haversine_distance(point1, point2))
            matrix.append(row)
        return matrix

    def _simple_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Create simple route without OSRM

        Args:
            points: List of (lat, lng) tuples

        Returns:
            Simple route information
        """
        total_distance = 0.0
        geometry = []

        for i in range(len(points) - 1):
            distance = self._haversine_distance(points[i], points[i + 1])
            total_distance += distance

            # Add points to geometry
            geometry.extend([points[i], points[i + 1]])

        return {
            "distance": total_distance,
            "duration": total_distance * 12,  # Rough estimate: 5 km/hour walking
            "geometry": geometry,
        }
