import argparse
import networkx as nx
from utils import (
    read_dot_files,
    read_dot_file,
    write_dot_file,
    merge_graphs,
    add_edge_label,
    pretty_label,
    color_edge,
    color_node,
)


def add_call_edges(merged_graph, ref_graph):
    for u, v, k, data in ref_graph.edges(keys=True, data=True):
        if data["label"] == "CALL":
            merged_graph.add_edge(u, v, label="CALL")
        if data["label"] == "ARGUMENT":
            merged_graph.add_edge(u, v, label="ARGUMENT")
        if data["label"] == "RECEIVER":
            merged_graph.add_edge(u, v, label="RECEIVER")
    return merged_graph


def copy_node_data(merged_graph, ref_graph):
    for node in merged_graph.nodes():
        if node in ref_graph.nodes.keys():
            ref_data = ref_graph.nodes[node]
            merged_graph.nodes[node].update(ref_data)
        else:
            print(f"Node {node} not found in reference graph")
    return merged_graph


def main():
    parser = argparse.ArgumentParser(description="Merge multiple Graphviz .dot files into a single graph.")
    parser.add_argument("--ast", nargs="+", help="Paths to the AST .dot files")
    parser.add_argument("--cfg", nargs="+", help="Paths to the CFG .dot files")
    parser.add_argument("--pdg", nargs="+", help="Paths to the PDG .dot files")
    parser.add_argument("-r", "--reference", help="Path to the reference .dot file")
    # parser.add_argument("-o", "--output", default="final.dot", help="Path to the output .dot file (default: final.dot)")

    args = parser.parse_args()

    input_graphs: list[nx.Graph] = read_dot_files(args.ast, args.cfg, args.pdg)
    refer_graph: nx.Graph = read_dot_file(args.reference)

    input_graphs = add_edge_label(input_graphs)

    merged_graph = merge_graphs(input_graphs)
    merged_graph = copy_node_data(merged_graph, refer_graph)
    merged_graph = add_call_edges(merged_graph, refer_graph)

    merged_graph = color_node(merged_graph)
    merged_graph = color_edge(merged_graph)
    merged_graph = pretty_label(merged_graph)
    write_dot_file(merged_graph, "out/merged.dot")


if __name__ == "__main__":
    main()
