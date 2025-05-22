import logging
from typing import Any, Callable

import networkx as nx
from networkx.drawing.nx_agraph import read_dot, write_dot

logger = logging.getLogger(__name__)


def read_dot_file(file_path):
    graph = read_dot(file_path)
    logger.debug(f"Loaded {graph} from {file_path}")
    return graph


def write_dot_file(graph, output_file):
    """
    Write a graph to a .dot file.

    Args:
        graph (networkx.Graph): The graph to write
        output_file (str): Path to the output .dot file
    """
    logger.info(f"Writing {graph} to {output_file}")
    write_dot(graph, output_file)


def remove_edges_from(graph, edges):
    graph.remove_edges_from(edges)


def remove_nodes_from(graph, nodes):
    """
    Check if the CFG will be broken if we remove the node.
    If true, CFG flow should skip the node.
    """

    for node in nodes:
        has_incoming_cfg = False
        has_outgoing_cfg = False

        incoming_edge = None
        outgoning_edge = None

        for u, v, k, data in graph.in_edges(node, keys=True, data=True):
            if data["label"] == "CFG":
                has_incoming_cfg = True
                incoming_edge = (u, v, k, data)
                break

        for u, v, k, data in graph.out_edges(node, keys=True, data=True):
            if data["label"] == "CFG":
                has_outgoing_cfg = True
                outgoning_edge = (u, v, k, data)
                break

        if not has_incoming_cfg and not has_outgoing_cfg:
            # No CFG edges, so we can remove the node
            pass

        elif has_incoming_cfg != has_outgoing_cfg:
            # We are at the entry or exit of a CFG
            logger.warning(
                f"Removing node {graph.nodes[node]} with only one CFG edge {incoming_edge if has_incoming_cfg else outgoning_edge}"
            )

        elif has_incoming_cfg and has_outgoing_cfg:
            # We have both incoming and outgoing CFG edges
            # We need to remove the node but maintain the CFG flow
            if incoming_edge and outgoning_edge:
                graph.add_edge(incoming_edge[0], outgoning_edge[1], **incoming_edge[3])
                logger.warning(
                    f"Removing node {graph.nodes[node]} with both CFG edges {incoming_edge} and {outgoning_edge}"
                )

    graph.remove_nodes_from(nodes)


def remove_edges_by_predicates(graph, predicates: list[Callable[[tuple, dict, nx.Graph], bool]]):
    """
    Remove edges from the graph based on the provided predicate functions.

    Args:
        graph (networkx.Graph): The graph to modify
        predicates (list): List of predicate functions to determine which edges to remove

    Returns:
        networkx.Graph: The modified graph
    """
    edges_to_remove = []
    for u, v, k, data in graph.edges(keys=True, data=True):
        edge = (u, v, k)
        if any(predicate(edge, data, graph) for predicate in predicates):
            edges_to_remove.append(edge)
    remove_edges_from(graph, edges_to_remove)


def remove_nodes_by_predicates(graph, predicates: list[Callable[[Any, dict, nx.Graph], bool]]):
    """
    Remove nodes from the graph based on the provided predicate functions.

    Args:
        graph (networkx.Graph): The graph to modify
        predicates (list): List of predicate functions to determine which nodes to remove

    Returns:
        networkx.Graph: The modified graph
    """
    nodes_to_remove = []
    for node, data in graph.nodes(data=True):
        if any(predicate(node, data, graph) for predicate in predicates):
            nodes_to_remove.append(node)
    remove_nodes_from(graph, nodes_to_remove)
