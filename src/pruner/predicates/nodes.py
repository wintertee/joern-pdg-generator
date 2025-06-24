def is_ast_leaf(node, data, graph) -> bool:
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


def is_method_implicitly_defined(node, data, graph) -> bool:
    """
    We remove methods not explicitly defined in the code.
    """

    def is_operator_root(data):
        return data["label"] == "METHOD" and "LINE_NUMBER" not in data.keys()

    if is_operator_root(data):
        return True
        pass

    else:
        for u, v, k, data in graph.in_edges(node, keys=True, data=True):
            if data["label"] == "AST":
                parent_data = graph.nodes[u]
                if is_operator_root(parent_data):
                    return True

    return False


def operator_fieldaccess(node, data, graph) -> bool:
    """
    We remove field access nodes that are not explicitly defined in the code.
    """

    if data["label"] == "CALL" and data.get("NAME") == "<operator>.fieldAccess":
        return True
    if data["label"] == "CALL" and data.get("NAME") == "<operator>.indirectFieldAccess":
        return True
    return False
