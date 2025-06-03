import argparse

import networkx as nx

import predicates
import utils
from cpg import CPG, CPGTemplate
from utils import read_dot_file, write_dot_file
from visualization import pretty_graph

node_filter: CPGTemplate = (
    CPGTemplate()
    + CPG.METADATA
    + CPG.FILESYSTEM
    + CPG.NAMESPACE
    # + CPG.METHOD
    + CPG.METHOD_PARAMETER_OUT
    # + CPG.TYPE
    # + CPG.AST
    + CPG.CALLGRAPH
    # + CPG.CFG
    + CPG.DOMINATORS
    + CPG.PDG
    + CPG.COMMENT
    + CPG.FINDING
    + CPG.SHORTCUTS
    + CPG.TAGSANDLOCATION
    + CPG.CONFIGURATION
    + CPG.BINGDING
    + CPG.ANNOTATION
    + CPG.BASE
    + CPG.UNKNOWN
)

edge_filter: CPGTemplate = (
    CPGTemplate()
    + CPG.METADATA
    + CPG.FILESYSTEM
    + CPG.NAMESPACE
    # + CPG.METHOD
    + CPG.METHOD_PARAMETER_OUT
    # + CPG.TYPE
    + CPG.AST
    + CPG.CALLGRAPH
    # + CPG.CFG
    + CPG.DOMINATORS
    + CPG.PDG
    + CPG.COMMENT
    + CPG.FINDING
    + CPG.SHORTCUTS
    + CPG.TAGSANDLOCATION
    + CPG.CONFIGURATION
    + CPG.BINGDING
    + CPG.ANNOTATION
    + CPG.BASE
    + CPG.UNKNOWN
)


def delete_nodes_and_edges(input_file, output_file, node_labels_to_delete, edge_labels_to_delete):
    # Load the graph from the .dot file
    graph = read_dot_file(input_file)

    # Delete nodes with specified labels (partial match)
    nodes_to_remove = [node for node, data in graph.nodes(data=True) if data.get("label") in node_labels_to_delete]
    graph.remove_nodes_from(nodes_to_remove)
    print(f"Removed {len(nodes_to_remove)} nodes")

    # Delete edges with specified labels, considering MultiDiGraph
    edges_to_remove = [
        (u, v, k) for u, v, k, data in graph.edges(keys=True, data=True) if data.get("label") in edge_labels_to_delete
    ]
    graph.remove_edges_from(edges_to_remove)
    print(f"Removed {len(edges_to_remove)} edges")

    for u, v, k, data in graph.edges(keys=True, data=True):
        if data.get("label") == "REACHING_DEF":
            data["label"] = f"DDG: {data.get('property', '')}"
            if "property" in data.keys():
                # Remove the property key from the data dictionary
                del data["property"]

    utils.remove_edges_by_predicates(
        graph,
        [
            predicates.null_ddg_edge,
            predicates.cdg_edge,
        ],
    )
    utils.remove_nodes_by_predicates(
        graph,
        [
            # predicates.ast_leaves_node,
            predicates.operator_method_body_node,
            predicates.operator_fieldaccess_node,
        ],
    )

    # delete isolated nodes
    isolated_nodes = list(nx.isolates(graph))
    graph.remove_nodes_from(isolated_nodes)
    print(f"Removed {len(isolated_nodes)} isolated nodes")

    # Render the graph as an SVG file
    pretty_graph(graph)
    write_dot_file(graph, output_file)


def main():
    parser = argparse.ArgumentParser(description="Delete nodes and edges from a Graphviz .dot file.")
    parser.add_argument("input_file", help="Path to the input .dot file.", nargs="?", default="out/all/export.dot")
    parser.add_argument("output_file", help="Path to the output .dot file.", nargs="?", default="out/filtered.dot")

    args = parser.parse_args()

    delete_nodes_and_edges(args.input_file, args.output_file, node_filter.node_labels, edge_filter.edge_labels)


if __name__ == "__main__":
    main()
