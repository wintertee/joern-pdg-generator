import argparse
import logging

import pruner
import pruner.langs
import pruner.predicates
import utils
from cpg import CPG, CPGTemplate
from visualization import pretty_graph

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Delete nodes and edges from a Graphviz .dot file.")
    parser.add_argument("input_file", help="Path to the input .dot file.", nargs="?", default="out/all/export.dot")
    parser.add_argument("--cfg", nargs="+", help="Paths to the CFG .dot files")
    parser.add_argument("-o", "--output", default="./out/v2.dot", help="Path to the output .dot file (default: v2.dot)")
    parser.add_argument("--lang", choices=["py", "java", "cpp"], help="Language of the input files")
    parser.add_argument("--ast", action="store_true", help="Keep AST nodes")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    utils.setup_logging(args.verbose)

    node_filter: CPGTemplate = (
    CPG.METHOD_
    + CPG.TYPE
    + CPG.AST
    + CPG.CALLGRAPH_CALL_
    + CPG.PDG_DDG_
)

    edge_filter: CPGTemplate = (
        CPGTemplate()
        + CPG.METHOD_
        + CPG.TYPE
        + CPG.CALLGRAPH_CALL_
        + CPG.PDG_DDG_
    )

    if args.ast:
        node_filter += CPG.AST
        edge_filter += CPG.AST

    graph = utils.read_dot_file(args.input_file)

    # Delete nodes with specified labels (partial match)
    nodes_to_remove = [
        node for node, data in graph.nodes(data=True) if data.get("label") not in node_filter.node_labels
    ]
    logger.debug(f"Nodes to remove: {nodes_to_remove}")
    utils.remove_nodes_from(graph, nodes_to_remove)

    # Delete edges with specified labels, considering MultiDiGraph
    edges_to_remove = [
        (u, v, k)
        for u, v, k, data in graph.edges(keys=True, data=True)
        if data.get("label") not in edge_filter.edge_labels
    ]
    utils.remove_edges_from(graph, edges_to_remove)

    utils.replace_ddg_label(graph)

    for cfg_file in args.cfg:
        sub_cfg_graph = utils.read_dot_file(cfg_file)
        for u, v, data in sub_cfg_graph.edges(data=True):
            data["label"] = "CFG"
        graph.update(sub_cfg_graph.edges(data=True))

    graph_pruner = pruner.GraphPruner(graph)

    if args.lang == "py":
        if args.ast is None:
            graph_pruner.add_prune_function(pruner.langs.python.remove_artifact_nodes_without_ast)
        else:
            graph_pruner.add_prune_function(pruner.langs.python.remove_artifact_nodes_with_ast)
    elif args.lang == "cpp":
        graph_pruner.add_prune_function(pruner.langs.cpp.remove_global_import)

    graph_pruner.add_edge_predicate(pruner.predicates.edges.null_ddg)
    graph_pruner.add_edge_predicate(pruner.predicates.edges.cdg)

    # graph_pruner.add_node_predicate(pruner.predicates.nodes.ast_leaves)
    graph_pruner.add_node_predicate(pruner.predicates.nodes.operator_method_body)
    graph_pruner.add_node_predicate(pruner.predicates.nodes.operator_fieldaccess)

    graph_pruner.prune()
    graph_pruner.remove_isolated_nodes()

    # Render the graph as an SVG file
    pretty_graph(graph)
    utils.write_dot_file(graph, args.output)


if __name__ == "__main__":
    main()
