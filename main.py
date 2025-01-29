from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from routing.load_data import load_flooded_areas
from tsp_endpoint import main_tsp
from routing import route_directions
from routing.cache_database import (
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

app.include_router(route_directions.router)
