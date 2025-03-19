import pytest
from pprint import pprint

from httpx import ASGITransport, AsyncClient
from main import app, startup_event
from models import LoginInput

@pytest.mark.asyncio
async def test_login_valid():
    async with startup_event(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request = client.build_request(url="/login", method="POST", json={
                "username": "Constituent1",
                "password": "Constituent1"
            })
            response = await client.send(request)

            pprint(response.json())
            assert response.json() == {
                "person_id": 1,
                "access_control": 1
            }

@pytest.mark.asyncio
async def test_login_invalid():
    async with startup_event(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request = client.build_request(url="/login", method="POST", json={
                "username": "UserNameThatIsNotInDatabase",
                "password": "PasswordThatIsNotInDatabase"
            })
            response = await client.send(request)

            pprint(response.json())
            assert response.json() == {
                "person_id": 0,
                "access_control": 0
            }