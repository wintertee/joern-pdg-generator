from collections import defaultdict
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
            "CALL",
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
        edge_labels=["CDG", "REACHING_DEF"],
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


CPG_COLORS = {
    # 基本类：表示程序的基础结构，例如抽象语法树节点（AST_NODE）、代码块（BLOCK）等
    "AST_NODE": "dimgray",
    "BLOCK": "gray",
    "UNKNOWN": "darkgray",
    "AST_EDGE": "lightgray",
    # 数据类：表示与数据和变量相关的信息，例如字面值（LITERAL）、标识符（IDENTIFIER）等
    "LITERAL": "darkgreen",
    "FIELD_IDENTIFIER": "seagreen",
    "IDENTIFIER": "limegreen",
    "LOCAL": "mediumspringgreen",
    "TYPE_REF": "palegreen",
    "MEMBER": "springgreen",
    "TYPE": "yellowgreen",
    "IMPORT": "chartreuse",  # 新增导入节点，属于数据类
    "DDG_EDGE": "lightgreen",  # 数据依赖边
    # 条件类：表示控制依赖的结构，例如条件控制结构（CONTROL_STRUCTURE）
    "CONTROL_STRUCTURE": "mediumblue",
    "CDG_EDGE": "dodgerblue",  # 控制依赖边
    # 流程控制类：表示程序控制流中的跳转，例如跳转标签（JUMP_LABEL）和跳转目标（JUMP_TARGET）
    "JUMP_LABEL": "darkorange",
    "JUMP_TARGET": "coral",
    "CFG_EDGE": "lightsalmon",  # 控制流边
    # 函数和调用类：表示与函数定义和调用相关的信息，例如函数（METHOD）、调用（CALL）等
    "METHOD": "firebrick",
    "METHOD_PARAMETER_IN": "indianred",
    "METHOD_PARAMETER_OUT": "lightcoral",
    "METHOD_RETURN": "salmon",
    "CALL": "crimson",
    "CALL_REPR": "tomato",
    "METHOD_REF": "orangered",
    "RETURN": "lightpink",
    "CALL_EDGE": "mistyrose",  # 函数调用边
    # 表达式和修饰类：表示表达式和代码修饰符，例如表达式（EXPRESSION）和修饰符（MODIFIER）
    "EXPRESSION": "indigo",
    "MODIFIER": "mediumpurple",
    # 类型相关类：表示与类型定义和参数相关的信息
    "TYPE_ARGUMENT": "darkkhaki",
    "TYPE_DECL": "goldenrod",
    "TYPE_PARAMETER": "khaki",
}


class ASTNodeLabel:
    node_type: str
    line_number: int | None
    value: str | None
    code: str | None

    def __init__(
        self, node_type: str, line_number: int | None = None, value: str | None = None, code: str | None = None
    ):
        self.node_type = node_type
        self.line_number = line_number
        self.value = value
        self.code = code

    @classmethod
    def from_node_data(cls, node_data):
        """
        Create an ASTNode instance from node data.
        """
        factory = cls.factories[node_data["label"]]
        return factory(cls, node_data)

    factories = defaultdict(
        lambda: (
            lambda cls, node_data: (
                print(f"Warning: No factory found for label '{node_data['label']}'"),
                cls(node_type=node_data["label"]),
            )[1]
        )
    )
    factories["BLOCK"] = lambda cls, data: cls(
        node_type="BLOCK",
        line_number=data.get("LINE_NUMBER"),
        value=data["TYPE_FULL_NAME"],
        code=data.get("CODE"),
    )
    factories["CALL"] = lambda cls, data: cls(
        node_type="CALL",
        line_number=data.get("LINE_NUMBER"),
        value=data["METHOD_FULL_NAME"],
        code=data.get("CODE"),
    )
    factories["CONTROL_STRUCTURE"] = lambda cls, data: cls(
        node_type="CONTROL_STRUCTURE",
        line_number=data.get("LINE_NUMBER"),
        value=data["CONTROL_STRUCTURE_TYPE"],
        code=data.get("CODE"),
    )
    factories["FIELD_IDENTIFIER"] = lambda cls, data: cls(
        node_type="FIELD_IDENTIFIER",
        line_number=data.get("LINE_NUMBER"),
        value=data["CANONICAL_NAME"],
        code=data.get("CODE"),
    )
    factories["IDENTIFIER"] = lambda cls, data: cls(
        node_type="IDENTIFIER",
        line_number=data.get("LINE_NUMBER"),
        value=data["NAME"],
        code=data.get("CODE"),
    )
    factories["LITERAL"] = lambda cls, data: cls(
        node_type="LITERAL",
        line_number=data.get("LINE_NUMBER"),
        code=data.get("CODE"),
    )
    factories["LOCAL"] = lambda cls, data: cls(
        node_type="LOCAL",
        line_number=data.get("LINE_NUMBER"),
        value=data["NAME"],
        code=data.get("CODE"),
    )
    factories["MEMBER"] = lambda cls, data: cls(
        node_type="MEMBER",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("NAME"),
        code=data.get("CODE"),
    )
    factories["METHOD"] = lambda cls, data: cls(
        node_type="METHOD",
        value=data["FULL_NAME"],
        code=data.get("CODE"),
    )
    factories["METHOD_PARAMETER_IN"] = lambda cls, data: cls(
        node_type="METHOD_PARAMETER",
        code=data.get("CODE"),
    )
    factories["METHOD_REF"] = lambda cls, data: cls(
        node_type="METHOD_REF",
        line_number=data.get("LINE_NUMBER"),
        value=data["METHOD_FULL_NAME"],
        code=data.get("CODE"),
    )
    factories["METHOD_RETURN"] = lambda cls, data: cls(
        node_type="METHOD_RETURN",
        line_number=data.get("LINE_NUMBER"),
        value=data["EVALUATION_STRATEGY"],
        code=data.get("CODE"),
    )
    factories["MODIFIER"] = lambda cls, data: cls(
        node_type="MODIFIER",
        line_number=data.get("LINE_NUMBER"),
        value=data["MODIFIER_TYPE"],
        code=data.get("CODE"),
    )
    factories["UNKNOWN"] = lambda cls, data: cls(
        node_type="UNKNOWN",
        line_number=data.get("LINE_NUMBER"),
        value=data["CONTAINED_REF"],
        code=data.get("CODE"),
    )
    factories["RETURN"] = lambda cls, data: cls(
        node_type="RETURN",
        line_number=data.get("LINE_NUMBER"),
        code=data.get("CODE"),
    )
    factories["TYPE"] = lambda cls, data: cls(
        node_type="TYPE",
        line_number=data.get("LINE_NUMBER"),
        value=data["NAME"],
        code=data.get("CODE"),
    )
    factories["TYPE_DECL"] = lambda cls, data: cls(
        node_type="TYPE_DECL",
        line_number=data.get("LINE_NUMBER"),
        value=data["FULL_NAME"],
        code=data.get("CODE"),
    )
    factories["TYPE_REF"] = lambda cls, data: cls(
        node_type="TYPE_REF",
        line_number=data.get("LINE_NUMBER"),
        value=data["TYPE_FULL_NAME"],
        code=data.get("CODE"),
    )

    def __repr__(self):
        return f"[{self.node_type}] @ {self.line_number}\\n{self.value}\\n{self.code}"
