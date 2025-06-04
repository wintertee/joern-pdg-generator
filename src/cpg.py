from dataclasses import dataclass, field


@dataclass(frozen=True)
class CPGTemplate:
    node_labels: list = field(default_factory=list)
    edge_labels: list = field(default_factory=list)

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        # Concatenate the lists of node and edge labels
        new_node_labels = self.node_labels + other.node_labels
        new_edge_labels = self.edge_labels + other.edge_labels
        return self.__class__(new_node_labels, new_edge_labels)


class CPG:
    """
    Code Property Graph Specification
    https://cpg.joern.io/
    """

    METADATA = CPGTemplate(
        node_labels=["META_DATA"],
        edge_labels=[],
    )

    FILESYSTEM = CPGTemplate(
        node_labels=["FILE"],
        edge_labels=["SOURCE_FILE"],
    )

    NAMESPACE = CPGTemplate(
        node_labels=["NAMESPACE", "NAMESPACE_BLOCK"],
        edge_labels=[],
    )

    # use underscore to mark this layer is not complete (see below)
    METHOD_ = CPGTemplate(
        node_labels=[
            "METHOD",
            # "METHOD_PARAMETER_IN",
            # "METHOD_PARAMETER_OUT",
            "METHOD_RETURN",
        ],
        edge_labels=[],
    )

    METHOD_PARAMETER_ = CPGTemplate(
        node_labels=[
            "METHOD_PARAMETER_OUT",
            # Since every METHOD_PARAMETER_IN are connected to their METHOD_PARAMETER_OUT, this is redundancy..
            # https://github.com/joernio/joern/blob/f6f3f2627cd909507f7917c5bdb1db0d771b124e/joern-cli/frontends/x2cpg/src/main/scala/io/joern/x2cpg/passes/base/MethodDecoratorPass.scala#L9
        ],
        edge_labels=[],
    )

    TYPE = CPGTemplate(
        node_labels=["MEMBER", "TYPE", "TYPE_PARAMETER", "TYPE_DECL", "TYPE_ARGUMENT"],
        edge_labels=["ALIAS_OF", "BINDS_TO", "INHERITS_FROM"],
    )

    AST = CPGTemplate(
        node_labels=[
            "AST_NODE",
            "BLOCK",
            "CALL",
            "CALL_REPR",
            "CONTROL_STRUCTURE",
            "EXPRESSION",
            "FIELD_IDENTIFIER",
            "IDENTIFIER",
            "JUMP_LABEL",
            "JUMP_TARGET",
            "LITERAL",
            "LOCAL",
            "METHOD_REF",
            "MODIFIER",
            "RETURN",
            "TYPE_REF",
            "UNKNOWN",
            "METHOD_PARAMETER_IN",
            # We move it from METHOD layer, as it is always connected to METHOD node with AST edge.
            # i.e. if we remove AST edges, this node will not have parents.
        ],
        edge_labels=["AST", "CONDITION"],
    )

    CALLGRAPH_CALL_ = CPGTemplate(
        node_labels=[],
        edge_labels=[
            # "ARGUMENT",
            "CALL",
            # "RECEIVER",
        ],
    )

    CALLGRAPH_AST_ = CPGTemplate(
        node_labels=[],
        edge_labels=[
            "ARGUMENT",
            "RECEIVER",
        ],
    )

    CFG = CPGTemplate(
        node_labels=["CFG_NODE"],
        edge_labels=["CFG"],
    )

    DOMINATORS = CPGTemplate(
        node_labels=[],
        edge_labels=["DOMINATE", "POST_DOMINATE"],
    )

    PDG_CDG_ = CPGTemplate(
        node_labels=[],
        edge_labels=[
            "CDG",
            # "REACHING_DEF",
        ],
    )

    PDG_DDG_ = CPGTemplate(
        node_labels=[],
        edge_labels=[
            "REACHING_DEF",
        ],
    )

    COMMENT = CPGTemplate(
        node_labels=["COMMENT"],
        edge_labels=[],
    )

    FINDING = CPGTemplate(
        node_labels=["FINDING", "KEY_VALUE_PAIR"],
        edge_labels=[],
    )

    SHORTCUTS = CPGTemplate(
        edge_labels=["CONTAINS", "EVAL_TYPE", "PARAMETER_LINK"],
    )

    TAGSANDLOCATION = CPGTemplate(
        node_labels=["LOCATION", "TAG", "TAG_NODE_PAIR"],
        edge_labels=["TAGGED_BY"],
    )

    CONFIGURATION = CPGTemplate(
        node_labels=["CONFIG_FILE"],
        edge_labels=[],
    )

    BINGDING = CPGTemplate(
        node_labels=["BINDING"],
        edge_labels=["BINDS"],
    )

    ANNOTATION = CPGTemplate(
        node_labels=[
            "ANNOTATION",
            "ANNOTATION_LITERAL",
            "ANNOTATION_PARAMETER",
            "ANNOTATION_PARAMETER_ASSIGN",
            "ARRAY_INITIALIZER",
        ],
        edge_labels=[],
    )

    BASE = CPGTemplate(node_labels=["DECLARATION"], edge_labels=["REF"])

    UNKNOWN = CPGTemplate(node_labels=[], edge_labels=["CAPTURE"])
