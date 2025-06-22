"""
TSP solver using OR-Tools for optimal route optimization
"""

from typing import Any, Dict, List, Tuple

from ortools.constraint_solver import pywrapcp, routing_enums_pb2


class TSPSolver:
    """Traveling Salesman Problem solver using OR-Tools"""

    def __init__(self):
        self.manager = None
        self.routing = None

    def solve_tsp(
        self, distance_matrix: List[List[float]], max_distance: float
    ) -> List[int]:
        """
        Solve TSP to find optimal route (open path, not returning to start)

        Args:
            distance_matrix: Distance matrix between all points (in km)
            max_distance: Maximum allowed route distance (in km)
            
        Returns:
            List of indices representing optimal route order
        """
        if not distance_matrix or len(distance_matrix) < 2:
            return [0]

        # Create routing model for open path (start at 0, end at last node)
        self.manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix), 1, [0], [len(distance_matrix) - 1]
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes in meters."""
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            # Convert km to meters and return as integer
            return int(distance_matrix[from_node][to_node] * 1000)
        
        transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add distance constraint (convert km to meters)
        max_distance_meters = int(max_distance * 1000)
        self.routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            max_distance_meters,  # maximum distance per vehicle (in meters)
            True,  # start cumul to zero
            "Distance",
        )
        distance_dimension = self.routing.GetDimensionOrDie("Distance")
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30

        # Solve the problem
        solution = self.routing.SolveWithParameters(search_parameters)

        if solution:
            return self._extract_route(solution)
        else:
            # Fallback to nearest neighbor if no solution found
            return self._nearest_neighbor(distance_matrix)

    def _extract_route(self, solution) -> List[int]:
        """Extract route from OR-Tools solution (open path)"""
        index = self.routing.Start(0)
        route = []

        while not self.routing.IsEnd(index):
            route.append(self.manager.IndexToNode(index))
            index = solution.Value(self.routing.NextVar(index))

        # Do not append the end node again (no return to start)
        return route

    def _nearest_neighbor(self, distance_matrix: List[List[float]]) -> List[int]:
        """
        Fallback to nearest neighbor algorithm

        Args:
            distance_matrix: Distance matrix

        Returns:
            Route as list of indices
        """
        n = len(distance_matrix)
        if n == 0:
            return []

        unvisited = set(range(1, n))  # Start from node 0
        route = [0]
        current = 0

        while unvisited:
            # Find nearest unvisited node
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        return route

    def get_route_distance(
        self, route: List[int], distance_matrix: List[List[float]]
    ) -> float:
        """
        Calculate total distance of a route

        Args:
            route: List of node indices
            distance_matrix: Distance matrix

        Returns:
            Total route distance
        """
        if len(route) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i + 1]]

        return total_distance
