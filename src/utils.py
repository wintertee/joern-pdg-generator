from networkx.drawing.nx_agraph import read_dot, write_dot
import networkx as nx
from collections import defaultdict
from cpg import ASTNodeLabel


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
    merged_graph = nx.MultiDiGraph()
    for graphs in input_graphs.values():
        for graph in graphs:
            merged_graph.update(graph)
    return merged_graph


def pretty_graph(graph):
    graph = color_node(graph)
    graph = color_edge(graph)
    graph = pretty_label(graph)
    return graph


def pretty_label(graph):
    # refernce graph中，label只显示类型。针对每种类型的节点，优化label的显示。
    for node, data in graph.nodes(data=True):
        data["original_label"] = data["label"]
        data["label"] = ASTNodeLabel.from_node_data(data)
    return graph


cpg_colors = {
    # 基本类：表示程序的基础结构，例如抽象语法树节点（AST_NODE）、代码块（BLOCK）等
    "AST_NODE": "dimgray",
    "BLOCK": "gray",
    "UNKNOWN": "darkgray",
    "AST_EDGE": "lightgray",
    # 数据类：表示与数据和变量相关的信息，例如字面值（LITERAL）、标识符（IDENTIFIER）等
    "LITERAL": "darkgreen",
    "FIELD_IDENTIFIER": "seagreen",
    "IDENTIFIER": "limegreen",
    "LOCAL": "mediumspringgreen",
    "TYPE_REF": "palegreen",
    "DDG_EDGE": "lightgreen",  # 数据依赖边
    # 条件类：表示控制依赖的结构，例如条件控制结构（CONTROL_STRUCTURE）
    "CONTROL_STRUCTURE": "mediumblue",
    "CDG_EDGE": "dodgerblue",  # 控制依赖边
    # 流程控制类：表示程序控制流中的跳转，例如跳转标签（JUMP_LABEL）和跳转目标（JUMP_TARGET）
    "JUMP_LABEL": "darkorange",
    "JUMP_TARGET": "coral",
    "CFG_EDGE": "lightsalmon",  # 控制流边
    # 函数和调用类：表示与函数定义和调用相关的信息，例如函数（METHOD）、调用（CALL）等
    "METHOD": "firebrick",
    "METHOD_PARAMETER_IN": "indianred",
    "METHOD_PARAMETER_OUT": "lightcoral",
    "METHOD_RETURN": "salmon",
    "CALL": "crimson",
    "CALL_REPR": "tomato",
    "METHOD_REF": "orangered",
    "RETURN": "lightpink",
    "CALL_EDGE": "mistyrose",  # 函数调用边
    # 表达式和修饰类：表示表达式和代码修饰符，例如表达式（EXPRESSION）和修饰符（MODIFIER）
    "EXPRESSION": "indigo",
    "MODIFIER": "mediumpurple",
}


def color_node(graph):
    # Modify the label for each node
    for node, data in graph.nodes(data=True):
        try:
            graph.nodes[node]["color"] = cpg_colors[data["label"]]
        except KeyError as e:
            print(f"KeyError: {e}")
            print(f"Node data: {data}")
    return graph


def color_edge(graph):
    # Modify the label for each node
    for u, v, k, data in graph.edges(keys=True, data=True):
        if data["label"] == "AST":
            graph.edges[u, v, k]["color"] = cpg_colors["AST_EDGE"]
        elif data["label"] == "CFG":
            graph.edges[u, v, k]["color"] = cpg_colors["CFG_EDGE"]
        elif "DDG" in data["label"] or "REACHING_DEF" in data["label"]:
            graph.edges[u, v, k]["color"] = cpg_colors["DDG_EDGE"]
        elif "CDG" in data["label"]:
            graph.edges[u, v, k]["color"] = cpg_colors["CDG_EDGE"]
        elif "CALL" in data["label"]:
            graph.edges[u, v, k]["color"] = cpg_colors["CALL_EDGE"]
    return graph
