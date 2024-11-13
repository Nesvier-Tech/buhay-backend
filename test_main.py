import pytest
import warnings
from fastapi import status
from main import app, startup_event
import json
from httpx import AsyncClient


VALID_START = "121.04932,14.65491"
VALID_END = "121.07471,14.66651"


async def fetch_directions(client, params):
    response = await client.get(
        f"/directions{params}",
        headers={"accept": "application/json"},
    )
    return response


@pytest.mark.asyncio
async def test_invalid_start_end_coordinates():
    # Test invalid start and end coordinates
    async with startup_event(app):
        params = f"?start=invalid_coords&end=invalid_coords"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await fetch_directions(client, params)
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        )  # Expecting a bad request for invalid coordinates


@pytest.mark.asyncio
async def test_missing_start_parameter():
    # Test missing start parameter
    async with startup_event(app):
        params = f"?end={VALID_END}"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await fetch_directions(client, params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_missing_end_parameter():
    # Test missing end parameter
    async with startup_event(app):
        params = f"?start={VALID_START}"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await fetch_directions(client, params)
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )  # Expecting a bad request for missing end


@pytest.mark.asyncio
async def test_valid_coordinates_endpoint():
    # Suppress FutureWarnings
    async with startup_event(app):
        params = f"?start={VALID_START}&end={VALID_END}"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await fetch_directions(client, params)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_respond_with_safe_route():
    # Get a valid and safe route
    async with startup_event(app):
        params = f"?start={VALID_START}&end={VALID_END}"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/directions{params}",
                headers={"accept": "application/json"},
            )

        assert response.json()["message"] == "Safe route found."
