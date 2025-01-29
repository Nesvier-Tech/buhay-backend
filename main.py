from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from typing import AsyncGenerator

# import json
import time


from routing.load_data import load_flooded_areas
from routing.geojson import create_geojson
from models import Route, DirectionsResponse
from routing.main_routing import compute_best_route_from_request
from tsp_endpoint import main_tsp
from routing.cache_database import (
    write_to_database,
    connect_to_database,
    close_database_connection,
)


# Load the flooded areas on startup
@asynccontextmanager
async def startup_event(app: FastAPI) -> AsyncGenerator[None, None]:
    await load_flooded_areas()
    await connect_to_database()
    yield
    await close_database_connection()


# Initialize the FastAPI app
app = FastAPI(lifespan=startup_event)

# Include router for tsp endpoint
app.include_router(main_tsp.router)


@app.get("/directions", status_code=status.HTTP_200_OK)
async def directions(start: str, end: str) -> DirectionsResponse:
    start_time = time.time()
    try:
        (
            hashed_id,
            duration_minutes,
            total_distance_km,
            route_coordinates,
            # route_info,
            route_data,
        ) = await compute_best_route_from_request(start, end)

        if route_data:
            route_data = DirectionsResponse.model_validate(route_data)

            end_time = time.time()
            print(f"Full running time: {end_time - start_time:.2f} seconds")

            return route_data

        geojson = create_geojson(route_coordinates)

        if duration_minutes:
            # Write the route to the cache database

            route_data = DirectionsResponse(
                route=Route(
                    duration=duration_minutes,
                    distanceKm=total_distance_km,
                    # coordinates=route_coordinates,
                    # routeInfo=route_info,
                ),
                geojson=geojson,
                message="Safe route found.",
            )

            await write_to_database(
                hashed_id,
                route_data.model_dump_json(),
            )

            end_time = time.time()
            print(f"Full running time: {end_time - start_time:.2f} seconds")

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
