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
    METHOD = CPGTemplate(
        node_labels=[
            "METHOD",  # We keep this node for CALL edge in CALLGRAPH
            "METHOD_PARAMETER_IN",
            "METHOD_PARAMETER_OUT",
            "METHOD_RETURN",
        ],
        edge_labels=[],
    )
    METHOD_PARAMETER_OUT = CPGTemplate(
        node_labels=[
            "METHOD_PARAMETER_OUT",
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
        ],
        edge_labels=["AST", "CONDITION"],
    )

    CALLGRAPH = CPGTemplate(
        node_labels=[],
        edge_labels=[
            "ARGUMENT",
            # "CALL",
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

    PDG = CPGTemplate(
        node_labels=[],
        edge_labels=[
            "CDG",
            # "REACHING_DEF", # Keep DDG
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
