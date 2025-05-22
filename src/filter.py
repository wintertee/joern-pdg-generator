import argparse

import networkx as nx

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
    # + CPG.CALLGRAPH
    # + CPG.CFG
    + CPG.DOMINATORS
    # + CPG.PDG
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
    # + CPG.AST
    # + CPG.CALLGRAPH
    # + CPG.CFG
    + CPG.DOMINATORS
    # + CPG.PDG
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

    # # Remove empty  REACHING_DEF
    # edges_to_remove = []
    # for u, v, k, data in graph.edges(keys=True, data=True):
    #     if data.get("label", "") == "REACHING_DEF" and "property" not in data.keys():
    #         edges_to_remove.append((u, v, k))
    # graph.remove_edges_from(edges_to_remove)
    # print(f"Removed {len(edges_to_remove)} REACHING_DEF edges without property")

    # Remove operator nodes
    # operator_method_nodes = [
    #     node for node, data in graph.nodes(data=True) if "<operator>." in data.get("FULL_NAME", "")
    # ]
    # graph.remove_nodes_from(operator_method_nodes)
    # print(f"Removed {len(operator_method_nodes)} operator nodes")
    # [print(f"Removed operator node: {node}") for node in operator_method_nodes]

    # Remove <init> for java
    # init_method_nodes = [node for node, data in graph.nodes(data=True) if "<init>" in data.get("FULL_NAME", "")]
    # graph.remove_nodes_from(init_method_nodes)
    # print(f"Removed {len(init_method_nodes)} <init> nodes")
    # keywords = [
    #     # "METHOD<BR/>&lt;operator&gt;",
    #     # "&lt;fakeNew&gt;",
    #     # "&lt;metaClassAdapter&gt;",
    #     "<init>",
    # ]

    # nodes_to_remove = set()

    # for component in nx.weakly_connected_components(graph):
    #     if any(any(keyword in graph.nodes[node].get("FULL_NAME", "") for keyword in keywords) for node in component):
    #         # Collect all nodes in the connected component for removal
    #         nodes_to_remove.update(component)

    # # Remove all collected nodes after iteration
    # graph.remove_nodes_from(nodes_to_remove)

    # delete isolated nodes
    isolated_nodes = list(nx.isolates(graph))
    graph.remove_nodes_from(isolated_nodes)
    print(f"Removed {len(isolated_nodes)} isolated nodes")

    for u, v, k, data in graph.edges(keys=True, data=True):
        if data.get("label") == "REACHING_DEF":
            data["label"] = f"DDG: {data.get('property', '')}"
            if "property" in data.keys():
                # Remove the property key from the data dictionary
                del data["property"]

    # Render the graph as an SVG file
    graph = pretty_graph(graph)
    write_dot_file(graph, output_file)


def main():
    parser = argparse.ArgumentParser(description="Delete nodes and edges from a Graphviz .dot file.")
    parser.add_argument("input_file", help="Path to the input .dot file.", nargs="?", default="out/all/export.dot")
    parser.add_argument("output_file", help="Path to the output .dot file.", nargs="?", default="out/filtered.dot")

    args = parser.parse_args()

    delete_nodes_and_edges(args.input_file, args.output_file, node_filter.node_labels, edge_filter.edge_labels)


if __name__ == "__main__":
    main()
