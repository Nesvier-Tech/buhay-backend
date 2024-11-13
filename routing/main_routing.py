import time
from models import DirectionsResponse

from routing.global_variables import (
    calculate_duration,
    calculate_distance,
)
from routing.route_system.safest_route_computation import find_safest_route
from routing.direction_system.directions import get_directions


async def compute_best_route_from_request(start: str, end: str):

    # Parse the start and end coordinates
    start_lng, start_lat = map(float, start.split(","))
    end_lng, end_lat = map(float, end.split(","))

    start_time = time.time()

    # Find the safest route between the start and end coordinates
    safest_route, route_coordinates, G, path, route = await find_safest_route(
        (start_lat, start_lng),
        (end_lat, end_lng),
    )

    # Get the route information
    route_info = get_directions(G, path, route)

    end_time = time.time()

    print(f"Time taken to find the safest route: {end_time - start_time:.2f} seconds")

    if safest_route:
        # Calculate the total distance and duration of the route
        total_distance_km = calculate_distance(safest_route)
        duration_minutes = calculate_duration(total_distance_km * 1000)

        return duration_minutes, total_distance_km, route_coordinates, route_info
    else:
        # Return None if no safe route is found
        return None, None, None, None
