from collections import defaultdict

import networkx as nx
from networkx.drawing.nx_agraph import read_dot, write_dot

from cpg import CPG_COLORS, ASTNodeLabel


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
                graph = read_dot(file_path)
                input_graphs[graph_type].append(graph)
    return input_graphs


def read_dot_file(file_path):
    graph = read_dot(file_path)
    print(f"Loaded {graph} from {file_path}")
    return graph


def write_dot_file(graph, output_file):
    """
    Write a graph to a .dot file.

    Args:
        graph (networkx.Graph): The graph to write
        output_file (str): Path to the output .dot file
    """
    print(f"Writing {graph} to {output_file}")
    write_dot(graph, output_file)


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


def pretty_graph(graph):
    graph = color_node(graph)
    graph = color_edge(graph)
    graph = pretty_label(graph)
    return graph


def pretty_label(graph):
    # refernce graph中，label只显示类型。针对每种类型的节点，优化label的显示。
    for node, data in graph.nodes(data=True):
        if "label" in data:
            data["original_label"] = data["label"]
            data["label"] = ASTNodeLabel.from_node_data(data)
    return graph


def color_node(graph):
    # Modify the label for each node
    for node, data in graph.nodes(data=True):
        try:
            graph.nodes[node]["color"] = CPG_COLORS[data["label"]]
        except KeyError:
            print(f"Error while coloring {node}, {data}")
    return graph


def color_edge(graph):
    # Modify the label for each node
    for u, v, k, data in graph.edges(keys=True, data=True):
        if data["label"] == "AST":
            graph.edges[u, v, k]["color"] = CPG_COLORS["AST_EDGE"]
        elif data["label"] == "CFG":
            graph.edges[u, v, k]["color"] = CPG_COLORS["CFG_EDGE"]
        elif "DDG" in data["label"] or "REACHING_DEF" in data["label"]:
            graph.edges[u, v, k]["color"] = CPG_COLORS["DDG_EDGE"]
        elif "CDG" in data["label"]:
            graph.edges[u, v, k]["color"] = CPG_COLORS["CDG_EDGE"]
        elif "CALL" in data["label"]:
            graph.edges[u, v, k]["color"] = CPG_COLORS["CALL_EDGE"]
    return graph
