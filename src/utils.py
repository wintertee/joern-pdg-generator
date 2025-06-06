import logging

import colorlog
import networkx.drawing.nx_agraph

logger = logging.getLogger(__name__)


def read_dot_file(file_path):
    graph = networkx.drawing.nx_agraph.read_dot(file_path)
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
    networkx.drawing.nx_agraph.write_dot(graph, output_file)


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
            logger.debug(
                f"Removing node {graph.nodes[node]} with only one CFG edge {incoming_edge if has_incoming_cfg else outgoning_edge}"
            )

        elif has_incoming_cfg and has_outgoing_cfg:
            # We have both incoming and outgoing CFG edges
            # We need to remove the node but maintain the CFG flow
            if incoming_edge and outgoning_edge:
                graph.remove_edges_from([incoming_edge, outgoning_edge])
                graph.add_edge(incoming_edge[0], outgoning_edge[1], **incoming_edge[3])
                logger.debug(
                    f"Removing node {graph.nodes[node]} with both CFG edges {incoming_edge} and {outgoning_edge}"
                )

    graph.remove_nodes_from(nodes)


def add_virtual_root(graph):
    """
    Add a virtual root node connecting to all method nodes in the graph.
    """
    virtual_root = "FILE"
    if virtual_root not in graph:
        graph.add_node(virtual_root, label="FILE")
        for node, data in graph.nodes(data=True):
            if data["label"] == "METHOD":
                graph.add_edge(virtual_root, node, label="AST")
        logger.info(f"Added virtual root node {virtual_root} to the graph.")


def setup_logging(verbose=False):
    """
    Set up logging configuration.
    """
    if verbose:
        colorlog.basicConfig(
            format="%(log_color)s %(levelname)-8s [%(filename)s:%(lineno)s ->%(funcName)s()] %(message)s",
            level=logging.DEBUG,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    else:
        colorlog.basicConfig(
            format="%(log_color)s %(levelname)-8s [%(filename)s:%(lineno)s ->%(funcName)s()] %(message)s",
            level=logging.INFO,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )


def replace_ddg_label(graph):
    """
    Replace the label of DDG edges to include the property if it exists.
    """
    for u, v, k, data in graph.edges(keys=True, data=True):
        if data.get("label") == "REACHING_DEF":
            data["label"] = f"DDG: {data.get('property', '')}"
            if "property" in data:
                del data["property"]
