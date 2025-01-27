from fastapi import APIRouter, HTTPException, status

from numpy import radians
from sklearn.cluster import DBSCAN

from models import Point
from typing import List, Tuple

router = APIRouter()

@router.get("/queue", status_code = status.HTTP_200_OK)
async def queue(points: List[Point]) -> List[List[Point]]:
    try:
        # Convert DBSCAN inputs to radians
        # Note: max_radius is in km
        max_radius = 3
        max_radius_in_rad = max_radius / 6371 
        X: List[Tuple[float, float]] = [radians(point.coordinates) for point in points]

        # Run DBSCAN algorithm from scikit-learn
        processed = DBSCAN(
            eps=max_radius_in_rad,
            min_samples=1,
            algorithm='ball_tree',
            metric='haversine'
        ).fit(X)

        # Return the points grouped by cluster 
        labels = processed.labels_
        clusters: List[List[Point]] = [[] for _ in len(set(labels))]
        for pt in range(len(points)):
            i = labels[pt]

            # If there are noise points, the maximum integer 
            # label value would be len(set(labels)) - 2
            clusters[i if i > -1 else -1].append(points[pt])

        return clusters


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

