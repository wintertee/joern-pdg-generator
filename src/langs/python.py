import logging

import networkx as nx

logger = logging.getLogger(__name__)

# The following functions do not work if class methods are not called!


def remove_artifact_nodes_with_ast(graph: nx.DiGraph) -> nx.DiGraph:
    root = [n for n, d in graph.in_degree() if d == 0]
    assert len(root) == 1, "There should be only one root node"
    root = root[0]

    subroots = graph.neighbors(root)

    def is_bad_root(data):
        if data["label"] == "TYPE_DECL":
            return True
        return False

    good_subroots = [subroot for subroot in subroots if not is_bad_root(graph.nodes[subroot])]

    good_nodes = set()
    for subroot in good_subroots:
        good_nodes.add(subroot)
        good_nodes.update(nx.descendants(graph, subroot))

    good_nodes.add(root)

    for node in list(graph.nodes()):
        if node not in good_nodes:
            # graph.nodes[node]["color"] = "blue"
            graph.remove_node(node)

    return graph


def remove_artifact_nodes_without_ast(graph: nx.DiGraph) -> nx.DiGraph:
    roots = [n for n, d in graph.in_degree() if d == 0]

    def is_bad_root(data):
        if data.get("label") == "METHOD":
            bad_root_names = {"<metaClassCallHandler>", "<metaClassAdapter>", "<fakeNew>", "<body>", "<meta>"}
            return any([bad_root_name in data.get("NAME") for bad_root_name in bad_root_names])
        if data.get("label") == "CALL":
            bad_call_names = {"<metaClassCallHandler>", "<metaClassAdapter>", "<fakeNew>", "<body>", "<meta>"}
            return any([bad_call_name in data.get("CODE") for bad_call_name in bad_call_names])
        return False

    good_roots = [root for root in roots if not is_bad_root(graph.nodes[root])]

    good_nodes = set()
    for subroot in good_roots:
        good_nodes.add(subroot)
        good_nodes.update(nx.descendants(graph, subroot))

    for node in list(graph.nodes()):
        if node not in good_nodes:
            # graph.nodes[node]["color"] = "blue"
            graph.remove_node(node)

    return graph
