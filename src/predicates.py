def null_ddg_edge(edge, data, graph) -> bool:
    """
    In PDG, each METHOD has empty DDG edges with all its AST children.
    And each METHOD_RETURN has incomping DDG edges.
    We remove these edges as they are not useful for the analysis.
    """

    # Outcoming empty DDG edges from METHOD
    if data["label"] == "DDG: ":
        return True

    # Incomping empty DDG edges to METHOD_RETURN
    if graph.nodes[edge[1]]["label"] == "METHOD_RETURN" and "DDG" in data["label"]:
        return True

    return False


def ast_leaves_node(node, data, graph) -> bool:
    """
    Some AST leafs are not useful for the analysis, we remove them
    """
    AST_LEAFS = [
        "IDENTIFIER",
        "LITERAL",
        "FIELD_IDENTIFIER",
        "LOCAL",
        "MEMBER",
        "MODIFIER",
    ]
    if data["label"] in AST_LEAFS:
        return True

    return False


def operator_method_body_node(node, data, graph) -> bool:
    """
    We remove methods not explicitly defined in the code.
    """


    def is_operator_root(data):
        return data["label"] == "METHOD" and "LINE_NUMBER" not in data.keys()

    if is_operator_root(data):
        # return True
        pass

    else:
        for u, v, k, data in graph.in_edges(node, keys=True, data=True):
            if data["label"] == "AST":
                parent_data = graph.nodes[u]
                if is_operator_root(parent_data):
                    return True

    return False
