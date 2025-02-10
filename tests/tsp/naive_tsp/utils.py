from osmnx.distance import great_circle
from typing import List

from models import Point
from naive_tsp.structs import Graph



def naive_create_graph(points: List[Point]) -> Graph: 
    """
    Convert to a complete, weighted, directed graph, in which the weights of the edges
    are the haversine distance between the adjacent vertices.
    """
    n = len(points) 
    G = Graph()

    # Add points[i] as the ith node of the graph
    for i in range(n):
        G.add_node(
            i, 
            lat = points[i].coordinates[0], 
            lng = points[i].coordinates[1]
        )
    
    # Add edge (i, j) for each possible i, j combination such that its weight 
    # is the haversine distance between Point i and Point j
    for i in range(n):
        lat_i, lng_i = points[i].coordinates
        for j in range(i+1, n):
            lat_j, lng_j = points[j].coordinates
            haversine_distance = great_circle(lat_i, lng_i, lat_j, lng_j)
            
            G.add_edge(
                i, j,
                weight = haversine_distance
            )
    
    return G


