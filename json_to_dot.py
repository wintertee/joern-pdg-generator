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


def eog_pass(graph):
    """skip reference and literal nodes for EOG edges"""
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
    """Filter edges based on specific criteria"""
    cdfg_labels = ["ARGUMENTS", "DFG", "EOG", "INVOKES", "PARAMETERS"]
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
    """Process the graph from input JSON and export to DOT format"""
    try:
        graph = json_to_networkx(input_path)

        eog_pass(graph)

        ast_edges, other_edges = edge_filter(graph)
        graph.remove_edges_from(other_edges)
        write_dot_file(graph, os.path.join(output_path, "ast_cdfg.dot"))

        graph.remove_edges_from(ast_edges)
        write_dot_file(graph, os.path.join(output_path, "cdfg.dot"))

        msg = f"Successfully processed graph {input_path} and exported to {output_path}"
        msg += f"\nExported ast_cdfg.dot with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges."
        msg += f"\nExported cdfg.dot with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges."

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
