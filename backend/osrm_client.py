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
    ) -> Dict[str, List[List[float]]]:
        """
        Get distance and duration matrices between all points using OSRM

        Args:
            points: List of (lat, lng) tuples

        Returns:
            Dict with 'distance_matrix' (in km) and 'duration_matrix' (in minutes)
        """
        if len(points) < 2:
            return {"distance_matrix": [[0.0]], "duration_matrix": [[0.0]]}

        # Build coordinates string for OSRM
        coords = ";".join([f"{lng},{lat}" for lat, lng in points])

        # Use the OSRM table service for distance and duration matrix (foot profile)
        url = f"https://router.project-osrm.org/table/v1/foot/{coords}"
        params = {"annotations": "distance,duration"}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if (
                data["code"] != "Ok"
                or "distances" not in data
                or "durations" not in data
            ):
                raise Exception(
                    f"OSRM error: {data.get('message', 'No distances or durations in response')}"
                )

            # Extract and convert distances (meters to km) and durations (seconds to minutes)
            distances = data["distances"]
            durations = data["durations"]

            distance_matrix = []
            duration_matrix = []
            for i, (row_dist, row_dur) in enumerate(zip(distances, durations)):
                matrix_row_dist = []
                matrix_row_dur = []
                for j, (distance, duration) in enumerate(zip(row_dist, row_dur)):
                    if distance is None:
                        distance = self._haversine_distance(points[i], points[j])
                    else:
                        distance = distance / 1000  # meters to km
                    if duration is None:
                        duration = (
                            self._haversine_distance(points[i], points[j]) / 5
                        ) * 60  # assume 5km/h
                    else:
                        duration = duration / 60  # seconds to minutes
                    matrix_row_dist.append(distance)
                    matrix_row_dur.append(duration)
                distance_matrix.append(matrix_row_dist)
                duration_matrix.append(matrix_row_dur)

            return {
                "distance_matrix": distance_matrix,
                "duration_matrix": duration_matrix,
            }

        except Exception as e:
            print(f"Error getting distance/duration matrix from OSRM: {e}")
            # Fallback to haversine distances and estimated durations
            dist = self._haversine_matrix(points)
            dur = [[(d / 5) * 60 for d in row] for row in dist]  # 5km/h walking
            return {"distance_matrix": dist, "duration_matrix": dur}

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

        url = f"https://router.project-osrm.org/route/v1/foot/{coords}"
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
