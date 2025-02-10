import pytest
import warnings
import json

from typing import List

from fastapi import status
from httpx import ASGITransport, AsyncClient
from main import app, startup_event
from models import Point, TSPinput

from random import randint
from time import time



def generate_points(n: int) -> TSPinput:
    start: Point = {"coordinates": [randint(0, 100_000), randint(0, 100_000)]}
    other_points: List[Point] = list()
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
async def test_tsp():
    start = time()
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
        end = time()
        print("TIME TAKEN: ", end-start)
        # print(response.json())
        assert response.json() == [
            {"coordinates": [1.0, 1.0]},
            {"coordinates": [0.0, 0.0]},
            {"coordinates": [2.0, 2.0]},
            {"coordinates": [10.0,10.0]}
        ]

@pytest.mark.asyncio
async def test_time():
    test_cases = 1000
    n = 6
    total_start = time()
    for i in range(test_cases):
        body = generate_points(n)
        # print(body)
        # start = time()
        async with startup_event(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                request = client.build_request(url="/tsp", method="GET", json=body)
                response = await client.send(request)
            # end = time()
            # print(response.json())
            # print(f"RANDOM TEST {i+1} TIME TAKEN: ", end-start)
    total_end = time()
    print(f"TIME TAKEN FOR n={n} {test_cases} TEST CASES: ", total_end-total_start)
    print(f"AVERAGE TIME FOR n={n} {test_cases} TEST CASES: ", (total_end-total_start)/test_cases)

@pytest.mark.asyncio
async def test_correctness():
    test_cases = 10 # The brute force solver might be very, very slow
    n = 6

    print(f'Testing Correctness...')
    total_start = time()
    for i in range(test_cases):
        body = generate_points(n)
        # print(body)

        async with startup_event(app):
            tsp_start = time()
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as tsp_client:
                request = tsp_client.build_request(url="/tsp", method="GET", json=body)
                tsp_response = await tsp_client.send(request)
            tsp_end = time()
            # print(tsp_response.json())
            print(f'Test {i + 1}, /tsp: {tsp_end - tsp_start}')

            naive_tsp_start = time()
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as naive_tsp_client:
                request = naive_tsp_client.build_request(url="/naive_tsp", method="GET", json=body)
                naive_tsp_response = await naive_tsp_client.send(request)
            naive_tsp_end = time()
            # print(naive_tsp_response.json())
            print(f'Test {i + 1}, /naive_tsp: {naive_tsp_end - naive_tsp_start}')

            assert(tsp_response.json() == naive_tsp_response.json())

    total_end = time()

    print(f'Total time: {total_end - total_start}')
    print(f'Average time per test case: {(total_end - total_start) / test_cases}')
    