def null_ddg(edge, data, graph) -> bool:
    """
    In PDG, each METHOD has empty DDG edges with all its AST children.
    And each METHOD_RETURN has incomping DDG edges.
    We remove these edges as they are not useful for the analysis.
    """

    # Outcoming empty DDG edges from METHOD
    if data["label"] == "DDG: ":
        return True

    # Incoming empty DDG edges to METHOD_RETURN
    # Keep return DDG <RET> and CFG edges.
    if graph.nodes[edge[1]]["label"] == "METHOD_RETURN" and data["label"] not in [
        "DDG: &lt;RET&gt;",
        "CFG",
    ]:
        return True

    return False


def cdg(edge, data, graph) -> bool:
    """
    CDG (Control Dependence Graph) are automatically generated.
    We remove them to create only CDFG (Control Data Flow Graph).
    """
    if data["label"] == "CDG: ":
        return True
    return False
