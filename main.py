from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from typing import AsyncGenerator
import json

from routing.load_data import load_flooded_areas
from tsp_endpoint import main_tsp
from tests.naive_tsp import naive_tsp  # For testing

from routing.route_directions import directions
from models import DirectionsRequest
from routing.cache_database import (
    connect_to_database,
    close_database_connection,
    search_login,
    add_request_row,
    add_route_info_row,
    update_route_info_id,
    route_info,
    update_rescued_boolean,
)
from models import (
    Point, 
    LoginInput, 
    AddRequestInput,
    SaveRouteInput,
    RouteInfo, 
    UpdateRescued
)
from qc_coordinates import check_point_in_polygon
from own_websocket import own_socket
from db_env import GOOGLE_MAPS_API
import googlemaps
from tsp_endpoint.tsp import tsp

from pprint import pprint


# Load the flooded areas on startup
@asynccontextmanager
async def startup_event(app: FastAPI) -> AsyncGenerator[None, None]:
    await load_flooded_areas()
    await connect_to_database()
    await own_socket.start_db_listener()
    yield
    await close_database_connection()


# Initialize the FastAPI app
app = FastAPI(lifespan=startup_event)
gmaps = googlemaps.Client(key = GOOGLE_MAPS_API)

# Include router for tsp endpoint
app.include_router(main_tsp.router)
app.include_router(naive_tsp.router)  # For testing
app.include_router(own_socket.router)


# app.include_router(route_directions.router)
@app.post("/directions", status_code=status.HTTP_200_OK)
async def call_directions(directionRequest: DirectionsRequest):
    return await directions(directionRequest)


@app.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    return {"message": "pong"}


@app.post("/checkCoordinates", status_code=status.HTTP_200_OK)
async def checkCoordinates(point: Point):
    if await check_point_in_polygon(point.coordinates):
        return {"message": "true"}
    return {"message": "false"}


@app.get("/test", status_code=status.HTTP_200_OK)
async def test():
    with open("sample_data.json", "r") as f:
        json_data = json.load(f)
    return json_data

@app.post("/login", status_code = status.HTTP_200_OK)
async def login(login_input: LoginInput):
    db_data = await search_login(login_input.username, login_input.password)
    
    # Valid
    if db_data: 
        return db_data

    # Invalid: Return person_id = 0, access_level = 0
    # since these cases are normally impossible.
    else:
        return {
            "person_id": 0,
            "access_control": 0
        }

@app.post("/convert_coordinates", status_code = status.HTTP_200_OK)
async def convert_coordinates(points: list[Point]):
    location_names: list[str]= list()
    for point in points:
        print(point)
        lng, lat = point.coordinates[0], point.coordinates[1]
        location_names.append(gmaps.reverse_geocode((lat, lng), result_type="street_address")[0]["formatted_address"])
    return {"locations": location_names}

@app.post("/add_request", status_code=status.HTTP_200_OK)
async def add_request(input: AddRequestInput):
    person_id: int = input.person_id
    raw_coordinates = list()
    coordinate_names = list()
    for point in input.coordinates:
        lng, lat = point.coordinates[0], point.coordinates[1]
        raw_coordinates.append({"coordinates": [lng, lat]})
        coordinate_names.append(gmaps.reverse_geocode((lat, lng), result_type="street_address")[0]["formatted_address"])
    request_id = await add_request_row(person_id, raw_coordinates, coordinate_names)
    return {"request_id": request_id}

@app.post("/save_route", status_code=status.HTTP_200_OK)
async def save_route(input: SaveRouteInput):
    try:
        tsp_output = await tsp(input.points)
        t = len(tsp_output)
        for i in range(t):
            start_lng, start_lat = tsp_output[i]["start"][0], tsp_output[i]["start"][1]
            end_lng, end_lat = tsp_output[i]["end"][0], tsp_output[i]["end"][1]
            start_name = gmaps.reverse_geocode((start_lat, start_lng), result_type="street_address")[0]["formatted_address"]
            end_name = gmaps.reverse_geocode((end_lat, end_lng), result_type="street_address")[0]["formatted_address"]
            tsp_output[i]["start"] = start_name
            tsp_output[i]["end"] = end_name
            tsp_output[i]["data"] = tsp_output[i]["data"].dict()

        route_id = await add_route_info_row(tsp_output)
        success = await update_route_info_id(input.request_id, route_id)
        return {"success": (True if success is not None and success == input.request_id else False)}
    except Exception as e:
        print(f"Error {e}")
        return {"success": 0}

@app.post("/get_route_info", status_code=status.HTTP_200_OK)
async def get_route_info(route_id: RouteInfo):
    data = await route_info(route_id.route_id)
    return {"payload": data}

@app.post("/update_rescued", status_code=status.HTTP_200_OK)
async def update_rescued(request_id: UpdateRescued):
    await update_rescued_boolean(request_id.request_id)
    return {"message": "done"}
