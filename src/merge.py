import argparse
import logging
from collections import defaultdict

import colorlog
import networkx as nx

import langs.cpp
import langs.python
import predicates
import utils
import visualization

logger = logging.getLogger(__name__)


def read_dot_files(ast_files, cfg_files, pdg_files) -> dict[str, list[nx.Graph]]:
    """
    Read multiple .dot files and return a list of graphs.

    Args:
        ast_files (list): List of AST .dot file paths
        cfg_files (list): List of CFG .dot file paths
        pdg_files (list): List of PDG .dot file paths

    Returns:
        list: List of graphs read from the .dot files
    """
    input_graphs = defaultdict(list)
    for graph_type, files in zip(["ast", "cfg", "pdg"], [ast_files, cfg_files, pdg_files]):
        if files is not None:
            for file_path in files:
                graph = utils.read_dot_file(file_path)
                input_graphs[graph_type].append(graph)
    return input_graphs


def add_edge_label(input_graphs):
    # we add labels to the edges to make them identifiable
    for graph in input_graphs["ast"]:
        for u, v, k, data in graph.edges(keys=True, data=True):
            data["label"] = "AST"

    for graph in input_graphs["cfg"]:
        for u, v, k, data in graph.edges(keys=True, data=True):
            data["label"] = "CFG"

    # we ignore the edges in the pdg graphs, as they are already labeled

    return input_graphs


def merge_graphs(input_graphs):
    ast_graph = nx.DiGraph()
    for graph in input_graphs["ast"]:
        ast_graph.update(graph)
    cfg_graph = nx.DiGraph()
    for graph in input_graphs["cfg"]:
        cfg_graph.update(graph)
    pdg_graph = nx.MultiDiGraph()
    for graph in input_graphs["pdg"]:
        pdg_graph.update(graph)
    # Merge the graphs into a single graph
    merged_graph = nx.MultiDiGraph()
    merged_graph.update(ast_graph)
    merged_graph.update(cfg_graph)
    merged_graph.update(pdg_graph)
    return merged_graph


def add_call_edges(merged_graph, ref_graph):
    for u, v, k, data in ref_graph.edges(keys=True, data=True):
        if data["label"] == "CALL":
            # If method not explicitly implemented, the "artifact" node only presents in AST graph.
            # If we not import AST graph, the call edge should be ignored.
            if merged_graph.has_node(u) and merged_graph.has_node(v):
                merged_graph.add_edge(u, v, **data)

    return merged_graph


def copy_node_data(merged_graph, ref_graph):
    for node in merged_graph.nodes():
        if node in ref_graph.nodes.keys():
            ref_data = ref_graph.nodes[node]
            merged_graph.nodes[node].update(ref_data)
        else:
            logger.warning(f"Node {node} not found in reference graph")
    return merged_graph


def main():
    parser = argparse.ArgumentParser(description="Merge multiple Graphviz .dot files into a single graph.")
    parser.add_argument("--ast", nargs="+", help="Paths to the AST .dot files")
    parser.add_argument("--cfg", nargs="+", help="Paths to the CFG .dot files")
    parser.add_argument("--pdg", nargs="+", help="Paths to the PDG .dot files")
    parser.add_argument("--ref", help="Path to the reference .dot file")
    parser.add_argument("--lang", choices=["py", "java", "cpp"], help="Language of the input files")
    parser.add_argument("--raw", action="store_true", help="disable pretty label and colorization")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "-o", "--output", default="merged.dot", help="Path to the output .dot file (default: merged.dot)"
    )

    args = parser.parse_args()
    if args.verbose:
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

    input_graphs = read_dot_files(args.ast, args.cfg, args.pdg)
    refer_graph: nx.Graph = utils.read_dot_file(args.ref)

    input_graphs = add_edge_label(input_graphs)

    merged_graph = merge_graphs(input_graphs)
    merged_graph = copy_node_data(merged_graph, refer_graph)
    merged_graph = add_call_edges(merged_graph, refer_graph)

    if args.lang == "py":
        if args.ast is None:
            merged_graph = langs.python.remove_artifact_nodes_without_ast(merged_graph)
        else:
            merged_graph = langs.python.remove_artifact_nodes_with_ast(merged_graph)
    elif args.lang == "cpp":
        merged_graph = langs.cpp.remove_global_import(merged_graph)

    utils.remove_edges_by_predicates(
        merged_graph,
        [
            predicates.null_ddg_edge,
            predicates.cdg_edge,
        ],
    )
    utils.remove_nodes_by_predicates(
        merged_graph,
        [
            predicates.ast_leaves_node,
            predicates.operator_method_body_node,
            predicates.operator_fieldaccess_node,
        ],
    )
    utils.remove_isolated_nodes(merged_graph)
    utils.add_virtual_root(merged_graph)

    merged_graph.name = f"Merged {args.lang} Graph"

    if not args.raw:
        visualization.pretty_graph(merged_graph)
    utils.write_dot_file(merged_graph, f"out/{args.output}")


if __name__ == "__main__":
    main()
