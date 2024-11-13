from pydantic import BaseModel
from typing import List, Tuple


class RouteInfo(BaseModel):
    instruction: str
    distance: float  # Distance in kilometers


class Route(BaseModel):
    duration: float
    distanceKm: float
    coordinates: List[List[float]]
    routeInfo: List[RouteInfo]


class DirectionsResponse(BaseModel):
    route: Route
    message: str = None
