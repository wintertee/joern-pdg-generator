import networkx as nx


def remove_bad_nodes(graph: nx.DiGraph) -> nx.DiGraph:

    roots = [n for n, d in graph.in_degree() if d == 0]

    def is_bad_root(data):
        bad_root_names = {"<metaClassCallHandler>", "<metaClassAdapter>", "<fakeNew>", "<body>"}
        return data.get("label") == "METHOD" and any(
            [bad_root_name in data.get("NAME") for bad_root_name in bad_root_names]
        )

    good_roots = [root for root in roots if not is_bad_root(graph.nodes[root])]

    good_nodes = set()
    for root in good_roots:
        good_nodes.add(root)
        good_nodes.update(nx.descendants(graph, root))

    for node in list(graph.nodes()):
        if node not in good_nodes:
            graph.remove_node(node)
            print(f"Removed node: {node}")

    return graph
