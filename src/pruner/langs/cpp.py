import logging

import networkx as nx

logger = logging.getLogger(__name__)


def remove_global_import(graph):
    """
    Remove useless graph rooted by <includes>:<global> node"""
    nodes_to_remove = []
    for node, data in graph.nodes(data=True):
        if data["label"] == "METHOD" and data.get("FULL_NAME") == "<includes>:<global>":
            logger.debug(f"Removing node {node} with data {data}")
            nodes_to_remove.append(node)
            for des in nx.descendants(graph, node):
                nodes_to_remove.append(des)
            break
    graph.remove_nodes_from(nodes_to_remove)
    return graph
