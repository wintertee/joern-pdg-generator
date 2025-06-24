from typing import Callable

import networkx as nx

from utils import remove_edges_from, remove_nodes_from

predicator = Callable[[tuple, dict, nx.MultiDiGraph], bool]


__all__ = [
    "GraphPruner",
    "predicator",
]


class GraphPruner:
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.node_predicates: list[predicator] = []
        self.edge_predicates: list[predicator] = []
        self.custom_prune_functions = []

    def add_node_predicate(self, predicate_func: predicator):
        self.node_predicates.append(predicate_func)

    def add_edge_predicate(self, predicate_func: predicator):
        self.edge_predicates.append(predicate_func)

    def add_prune_function(self, prune_function: Callable[[nx.MultiDiGraph], None]):
        self.custom_prune_functions.append(prune_function)

    def prune(self):
        for prune_function in self.custom_prune_functions:
            prune_function(self.graph)
        self._prune_edges()
        self._prune_nodes()

    def remove_isolated_nodes(self):
        """
        Remove isolated nodes from the graph.
        """
        isolated_nodes = list(nx.isolates(self.graph))
        remove_nodes_from(self.graph, isolated_nodes)

    def _prune_edges(self):
        """
        Remove edges from the graph based on the provided predicate functions.

        Args:
            graph (networkx.Graph): The graph to modify
            predicates (list): List of predicate functions to determine which edges to remove
        """
        edges_to_remove = []
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            edge = (u, v, k)
            if any(
                predicate(edge, data, self.graph) for predicate in self.edge_predicates
            ):
                edges_to_remove.append(edge)
        remove_edges_from(self.graph, edges_to_remove)

    def _prune_nodes(self):
        """
        Remove nodes from the graph based on the provided predicate functions.

        Args:
            graph (networkx.Graph): The graph to modify
            predicates (list): List of predicate functions to determine which nodes to remove
        """
        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            if any(
                predicate(node, data, self.graph) for predicate in self.node_predicates
            ):
                nodes_to_remove.append(node)
        remove_nodes_from(self.graph, nodes_to_remove)
