import pytest
import warnings
import json

from typing import List

from fastapi import status
from httpx import ASGITransport, AsyncClient
from main import app, startup_event
from models import Point, TSPinput

from random import randint
import time

@pytest.mark.asyncio
async def test_tsp():
    start = time.time()
    async with startup_event(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request = client.build_request(url="/tsp", method="GET", 
                json={
                    "start": {"coordinates": [1,1]},
                    "other_points": [
                        {"coordinates": [10, 10]},
                        {"coordinates": [2, 2]},
                        {"coordinates": [0, 0]}
                    ]
                }
            )
            response = await client.send(request)
        end = time.time()
        print("TIME TAKEN: ", end-start)
        # print(response.json())
        assert response.json() == [
            {"coordinates": [1.0, 1.0]},
            {"coordinates": [0.0, 0.0]},
            {"coordinates": [2.0, 2.0]},
            {"coordinates": [10.0,10.0]}
        ]

def generate_points(n: int) -> TSPinput:
    start: Point = {"coordinates": [randint(0, 100_000), randint(0, 100_000)]}
    other_points: list[Point] = list()
    for i in range(n-1):
        lat = float(randint(0, 100_000))
        lng = float(randint(0, 100_000))
        p = {"coordinates":[lat,lng]}
        other_points.append(p)
    ret: TSPinput = {
        "start": start,
        "other_points": other_points
    }
    return ret

@pytest.mark.asyncio
async def test_time():
    test_cases = 1000
    n = 6
    total_start = time.time()
    for i in range(test_cases):
        body = generate_points(n)
        # print(body)
        start = time.time()
        async with startup_event(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                request = client.build_request(url="/tsp", method="GET", json=body)
                response = await client.send(request)
            end = time.time()
            # print(response.json())
            # print(f"RANDOM TEST {i+1} TIME TAKEN: ", end-start)
    total_end = time.time()
    print(f"TIME TAKEN FOR n={n} {test_cases} TEST CASES: ", total_end-total_start)
    print(f"AVERAGE TIME FOR n={n} {test_cases} TEST CASES: ", (total_end-total_start)/test_cases)