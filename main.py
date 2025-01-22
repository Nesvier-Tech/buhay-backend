from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from typing import AsyncGenerator
import json


from routing.load_data import load_flooded_areas
from routing.geojson import create_geojson
from models import Route, DirectionsResponse
from routing.main_routing import compute_best_route_from_request
from routing.cache_database import write_to_database


# Load the flooded areas on startup
@asynccontextmanager
async def startup_event(app: FastAPI) -> AsyncGenerator[None, None]:
    await load_flooded_areas()
    yield


# Initialize the FastAPI app
app = FastAPI(lifespan=startup_event)


@app.get("/directions", status_code=status.HTTP_200_OK)
async def directions(start: str, end: str) -> DirectionsResponse:
    try:
        (
            hashed_id,
            duration_minutes,
            total_distance_km,
            route_coordinates,
            route_info,
            route_data,
        ) = await compute_best_route_from_request(start, end)

        if route_data:
            route_data = DirectionsResponse.model_validate(route_data)
            return route_data

        geojson = create_geojson(route_coordinates)

        if duration_minutes:
            # Write the route to the cache database

            route_data = DirectionsResponse(
                route=Route(
                    duration=duration_minutes,
                    distanceKm=total_distance_km,
                    coordinates=route_coordinates,
                    routeInfo=route_info,
                ),
                geojson=geojson,
                message="Safe route found.",
            )

            write_to_database(
                hashed_id,
                route_data.model_dump_json(),
            ),

            return route_data
        else:
            # Return an error message if no safe route is found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No safe route found.",
            )

    except ValueError as e:
        # Handle specific exceptions with a 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request.",
        )

    except HTTPException as e:
        # Re-raise HTTPExceptions
        raise e

    except Exception as e:
        # Handle unexpected server errors with a 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
