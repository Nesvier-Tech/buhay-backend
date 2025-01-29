from pydantic import BaseModel
from typing import List, Tuple


class RouteInfo(BaseModel):
    instruction: str
    distance: float  # Distance in kilometers


class Route(BaseModel):
    duration: float
    distanceKm: float
    # coordinates: List[List[float]]
    # routeInfo: List[RouteInfo]


class DirectionsResponse(BaseModel):
    route: Route
    geojson: dict
    message: str = None


class Point(BaseModel):
    location_name: str | None
    coordinates: Tuple[float, float]
