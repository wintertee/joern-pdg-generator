from typing import Callable

import networkx as nx

from utils import remove_edges_from, remove_nodes_from

predicator = Callable[[tuple, dict, nx.MultiDiGraph], bool]


class PredicatePruner:
    def __init__(self):
        self.node_predicates: list[predicator] = []
        self.edge_predicates: list[predicator] = []

    def add_node_predicate(self, predicate_func: predicator):
        self.node_predicates.append(predicate_func)

    def add_edge_predicate(self, predicate_func: predicator):
        self.edge_predicates.append(predicate_func)

    def prune(self, graph):
        self.prune_edges(graph)
        self.prune_nodes(graph)

    def prune_edges(self, graph: nx.MultiDiGraph):
        """
        Remove edges from the graph based on the provided predicate functions.

        Args:
            graph (networkx.Graph): The graph to modify
            predicates (list): List of predicate functions to determine which edges to remove
        """
        edges_to_remove = []
        for u, v, k, data in graph.edges(keys=True, data=True):
            edge = (u, v, k)
            if any(predicate(edge, data, graph) for predicate in self.edge_predicates):
                edges_to_remove.append(edge)
        remove_edges_from(graph, edges_to_remove)

    def prune_nodes(self, graph: nx.MultiDiGraph):
        """
        Remove nodes from the graph based on the provided predicate functions.

        Args:
            graph (networkx.Graph): The graph to modify
            predicates (list): List of predicate functions to determine which nodes to remove
        """
        nodes_to_remove = []
        for node, data in graph.nodes(data=True):
            if any(predicate(node, data, graph) for predicate in self.node_predicates):
                nodes_to_remove.append(node)
        remove_nodes_from(graph, nodes_to_remove)
