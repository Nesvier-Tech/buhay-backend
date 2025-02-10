from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Node:
    i: int # index
    lat: float
    lng: float

@dataclass
class Edge:
    i: int # from index
    j: int # to index
    weight: float

class Graph:
    """
    Represents a complete, weighted, directed graph
    """
    def __init__(self, nodes: List[Node] = [], edges: List[Edge] = []):
        self._nodes = nodes
        self._edges = edges

    @property
    def nodes(self):
        return self._nodes
    
    @property
    def edges(self):
        return self._edges

    def add_node(self, i: int, lat: float, lng: float):
        self._nodes.append(Node(i, lat, lng))
    
    def add_edge(self, i: int, j: int, weight: float):
        self._edges.append(Edge(i, j, weight))

        # Since complete digraph
        self._edges.append(Edge(j, i, weight))
    
    def get_node(self, i: int) -> Node:
        return list(filter(lambda n : n.i == i, self._nodes))[0]

Path = Tuple[float, List[Node]] # total distance, nodes
Coordinates = Tuple[float, float] # lat, lng