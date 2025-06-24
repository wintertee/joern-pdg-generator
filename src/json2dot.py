import argparse
import json
import os
import traceback

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph


def sanitize_node_id(node_id):
    """Sanitize node ID to ensure it is a valid DOT identifier"""
    # Replace invalid characters with underscores
    sanitized_id = str(node_id).replace("-", "_").replace(" ", "_")
    return sanitized_id


def format_node_attributes(node_data):
    """Format node attributes for DOT export"""
    attributes = {}

    # Add labels as a comma-separated string
    if "labels" in node_data:
        attributes["original_label"] = ",".join(node_data["labels"])

    # Add all properties
    if "properties" in node_data:
        for key, value in node_data["properties"].items():
            # Handle special cases for complex data types
            if isinstance(value, list):
                attributes[key] = ",".join(str(v) for v in value)
            elif isinstance(value, dict):
                attributes[key] = str(value)
            elif isinstance(value, str) and "\n" in value:
                # Replace newlines with literal \n to prevent DOT from adding backslashes
                attributes[key] = value.replace("\n", "\\n")
            else:
                attributes[key] = value

    # label optimized for visualization
    start_line = str(attributes.get("startLine", ""))
    end_line = str(attributes.get("endLine", ""))
    name = str(attributes.get("name", ""))
    code = str(attributes.get("code", ""))

    attributes["label"] = attributes["original_label"] + "@" + start_line + "~" + end_line + "\\n" + name + "\\n" + code

    return attributes


def format_edge_attributes(edge_data):
    """Format edge attributes for DOT export"""
    attributes = {}

    # Add edge type
    if "type" in edge_data:
        attributes["label"] = edge_data["type"]

    # Add all properties
    if "properties" in edge_data:
        for key, value in edge_data["properties"].items():
            if isinstance(value, list):
                attributes[key] = ",".join(str(v) for v in value)
            elif isinstance(value, dict):
                attributes[key] = str(value)
            else:
                attributes[key] = value

    return attributes


def json_to_networkx(json_file_path):
    """Convert JSON graph to NetworkX MultiGraph"""
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create a MultiGraph to handle multiple edges between the same nodes
    G = nx.MultiDiGraph()

    # Add nodes
    for node in data.get("nodes", []):
        node_id = sanitize_node_id(node["id"])
        attributes = format_node_attributes(node)
        G.add_node(node_id, **attributes)

    # Add edges
    for edge in data.get("edges", []):
        edge_id = sanitize_node_id(edge["id"])
        start_node = sanitize_node_id(edge["startNode"])
        end_node = sanitize_node_id(edge["endNode"])
        attributes = format_edge_attributes(edge)

        # Add edge with its ID as key for MultiGraph
        G.add_edge(start_node, end_node, key=edge_id, **attributes)

    return G


def remove_type_nodes(graph):
    """Remove nodes with type 'Type' from the graph
    We want to keep parameter and argument edges. However `Type` nodes have those edges, resulting in isolated connected components.
    """
    nodes_to_remove = [node for node, data in graph.nodes(data=True) if "Type" in data.get("original_label")]
    graph.remove_nodes_from(nodes_to_remove)


def eog_pass(graph):
    """skip reference and literal nodes for EOG edges. We also skip Block nodes.
    Check the specification: https://fraunhofer-aisec.github.io/cpg/CPG/specs/eog/
    This allows a shallower graph with less EOG edges, which is more efficient for message-passing GNNs.
    However, it may break the AssignmentExpression as it transformed

    ┌───────────┐      ┌───┐      ┌───┐      ┌─────┐      ┌───────────┐
    │ last_Stmt ├─────►│ a ├─────►│ 1 ├─────►│ a=1 ├─────►│ next_Stmt │
    └───────────┘ EOG  └─▲─┘ EOG  └─┬─┘ EOG  └─────┘ EOG  └───────────┘
                         │          │
                         │          │
                         └──────────┘
                            DFG

    into:

    ┌───────────┐                            ┌─────┐      ┌───────────┐
    │ last_Stmt ┼───────────────────────────►│ a=1 ├─────►│ next_Stmt │
    └───────────┘           EOG              └─────┘ EOG  └───────────┘
                    ┌───┐      ┌───┐
                    │ a │◄─────┤ 1 │
                    └───┘  DFG └───┘

    So we have two connected components... To avoid this, AST should be added back to the graph.
    As a result, the graph will be much shallower and denser.

    """
    for node, data in graph.nodes(data=True):
        if any(label in data["original_label"] for label in ["Reference", "Literal", "Block"]):
            last_nodes = []
            incoming_edges = []
            outgoing_edge = None
            next_node = None

            for u, v, k, edge_data in graph.in_edges(node, keys=True, data=True):
                if edge_data["label"] == "EOG":
                    last_nodes.append(u)
                    incoming_edges.append((u, v, k, edge_data))

            for u, v, k, edge_data in graph.out_edges(node, keys=True, data=True):
                if edge_data["label"] == "EOG":
                    next_node = v
                    outgoing_edge = (u, v, k, edge_data)
                    break

            if last_nodes and next_node:
                graph.remove_edge(*outgoing_edge[:3])
                for i in range(len(last_nodes)):
                    last_node = last_nodes[i]
                    incoming_edge = incoming_edges[i]
                    graph.remove_edge(*incoming_edge[:3])
                    graph.add_edge(last_node, next_node, key=incoming_edge[2], **incoming_edge[3])


def edge_filter(graph):
    """Filter edges based on specific criteria

    - ARGUMENTS: find origin of arguments in a CALL node
    - DFG: data flow graph edges
    - EOG: control flow edges (Evaluation Order Graph)
    - INVOKES: function calls
    - PARAMETERS: link function declaration to its parameters
    - REFERS_TO: link variable node to its declaration
    """

    cdfg_labels = ["ARGUMENTS", "DFG", "EOG", "INVOKES", "PARAMETERS", "REFERS_TO"]
    ast_labels = ["AST"]

    ast_edges = []
    other_edges = []

    for u, v, k, data in graph.edges(keys=True, data=True):
        if any(label in data["label"] for label in ast_labels):
            ast_edges.append((u, v, k))
        elif any(label in data["label"] for label in cdfg_labels):
            continue
        else:
            other_edges.append((u, v, k))

    return ast_edges, other_edges


def remove_isolated_nodes(graph):
    """Remove isolated nodes from the graph"""
    isolated_nodes = list(nx.isolates(graph))
    for node in isolated_nodes:
        graph.remove_node(node)


def write_dot_file(graph, output_path):
    """Write the graph to a DOT file"""
    A = to_agraph(graph)
    A.graph_attr["linelength"] = int(1e6)
    A.node_attr["shape"] = "box"  # Set node shape to box
    A.node_attr["style"] = "rounded"  # Set node style to rounded corners
    A.write(output_path)


def process_graph(input_path, output_path):
    """Process the graph from input JSON and export to DOT format
    write 3 types of dot files:
    1. original.dot - the original graph with all nodes and edges
    2. ast_minimal_cfg_dfg.dot - AST + CDFG with simplified EOG edges
    3. cdfg.dot - the final graph after removing AST edges and isolated nodes


    """
    try:
        # STEP 1: read the JSON file and convert it to a NetworkX graph
        graph = json_to_networkx(input_path)

        msg = f"Successfully processed graph {input_path}"

        # STEP 2: export the original graph to a DOT file
        output_filename = os.path.join(output_path, "original.dot")
        write_dot_file(graph, output_filename)
        msg += f"\nExported {output_filename} with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges."

        # STEP 3: remove `Type` nodes and non-ast-cdfg edges
        remove_type_nodes(graph)
        ast_edges, other_edges = edge_filter(graph)
        graph.remove_edges_from(other_edges)

        # STEP 4: export the graph with AST and simplified CDFG edges to a DOT file
        graph_with_eog_pass = graph.copy()
        eog_pass(graph_with_eog_pass)
        remove_isolated_nodes(graph_with_eog_pass)

        output_filename = os.path.join(output_path, "ast_minimal_cfg_dfg.dot")
        write_dot_file(graph_with_eog_pass, output_filename)
        msg += f"\nExported {output_filename} with {graph_with_eog_pass.number_of_nodes()} nodes and {graph_with_eog_pass.number_of_edges()} edges."

        # STEP 5: export the graph without AST and EOG simplification (raw CDFG)
        graph.remove_edges_from(ast_edges)
        remove_isolated_nodes(graph)
        output_filename = os.path.join(output_path, "cdfg.dot")
        write_dot_file(graph, output_filename)

        msg += f"\nExported {output_filename} with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges."

        return (True, msg)

    except Exception as e:
        msg = f"Error processing graph {input_path}: {str(e)}\n{traceback.format_exc()}"
        return (False, msg)


def main():
    parser = argparse.ArgumentParser(description="Convert JSON graph to DOT format")
    parser.add_argument("input_json", help="Input JSON file path")
    parser.add_argument("-o", "--output", help="Output DOT file directory")

    args = parser.parse_args()

    success, msg = process_graph(args.input_json, args.output)
    print(msg)


if __name__ == "__main__":
    main()
