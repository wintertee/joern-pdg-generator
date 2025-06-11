import argparse
import logging
from collections import defaultdict

import utils

logger = logging.getLogger(__name__)

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
        factory = cls.factories[node_data.get("label")]
        return factory(cls, node_data)

    factories = defaultdict(
        lambda: (
            lambda cls, data: (
                logger.warning(f"No factory found for label '{data['label']}'"),
                cls(node_type=data.get("label")),
            )[1]
        )
    )
    factories["BLOCK"] = lambda cls, data: cls(
        node_type="BLOCK",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("TYPE_FULL_NAME"),
        code=data.get("CODE"),
    )
    factories["CALL"] = lambda cls, data: cls(
        node_type="CALL",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("METHOD_FULL_NAME"),
        code=data.get("CODE"),
    )
    factories["CONTROL_STRUCTURE"] = lambda cls, data: cls(
        node_type="CONTROL_STRUCTURE",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("CONTROL_STRUCTURE_TYPE"),
        code=data.get("CODE"),
    )
    factories["FIELD_IDENTIFIER"] = lambda cls, data: cls(
        node_type="FIELD_IDENTIFIER",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("CANONICAL_NAME"),
        code=data.get("CODE"),
    )
    factories["IDENTIFIER"] = lambda cls, data: cls(
        node_type="IDENTIFIER",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("NAME"),
        code=data.get("CODE"),
    )
    factories["JUMP_TARGET"] = lambda cls, data: cls(
        node_type="JUMP_TARGET",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("NAME"),
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
        value=data.get("NAME"),
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
        line_number=data.get("LINE_NUMBER"),
        value=data.get("FULL_NAME"),
        # code=data.get("CODE"),
        # ignore code, as only available for CPP
    )
    factories["METHOD_PARAMETER_IN"] = lambda cls, data: cls(
        node_type="METHOD_PARAMETER_IN",
        line_number=data.get("LINE_NUMBER"),
        code=data.get("CODE"),
    )
    factories["METHOD_PARAMETER_OUT"] = lambda cls, data: cls(
        node_type="METHOD_PARAMETER_OUT",
        line_number=data.get("LINE_NUMBER"),
        code=data.get("CODE"),
    )
    factories["METHOD_REF"] = lambda cls, data: cls(
        node_type="METHOD_REF",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("METHOD_FULL_NAME"),
        code=data.get("CODE"),
    )
    factories["METHOD_RETURN"] = lambda cls, data: cls(
        node_type="METHOD_RETURN",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("EVALUATION_STRATEGY"),
        code=data.get("CODE"),
    )
    factories["MODIFIER"] = lambda cls, data: cls(
        node_type="MODIFIER",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("MODIFIER_TYPE"),
        code=data.get("CODE"),
    )
    factories["UNKNOWN"] = lambda cls, data: cls(
        node_type="UNKNOWN",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("CONTAINED_REF"),
        code=data.get("CODE"),
    )
    factories["RETURN"] = lambda cls, data: cls(
        node_type="RETURN",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("ARGUMENT_NAME"),
        code=data.get("CODE"),
    )
    factories["TYPE"] = lambda cls, data: cls(
        node_type="TYPE",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("NAME"),
        code=data.get("CODE"),
    )
    factories["TYPE_DECL"] = lambda cls, data: cls(
        node_type="TYPE_DECL",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("FULL_NAME"),
        code=data.get("CODE"),
    )
    factories["TYPE_REF"] = lambda cls, data: cls(
        node_type="TYPE_REF",
        line_number=data.get("LINE_NUMBER"),
        value=data.get("TYPE_FULL_NAME"),
        # code=data.get("CODE"),
    )

    def __repr__(self):
        if self.value is None:
            return f"[{self.node_type}] @ {self.line_number}\\n{self.code}"
        return f"[{self.node_type}] @ {self.line_number}\\n{self.value}\\n{self.code}"


def pretty_graph(graph):
    color_node(graph)
    color_edge(graph)
    pretty_label(graph)


def pretty_label(graph):
    # refernce graph中，label只显示类型。针对每种类型的节点，优化label的显示。
    for node, data in graph.nodes(data=True):
        if "label" in data:
            data["original_label"] = data.get("label")
            data["label"] = ASTNodeLabel.from_node_data(data)


def color_node(graph):
    # Modify the label for each node
    for node, data in graph.nodes(data=True):
        try:
            graph.nodes[node]["color"] = CPG_COLORS[data.get("label")]
        except KeyError as e:
            logger.warning(f"Node {node} has no color for label {data.get('label')}. Error: {e}")


def color_edge(graph):
    # Modify the label for each node
    for u, v, k, data in graph.edges(keys=True, data=True):
        if data.get("label") == "AST":
            graph.edges[u, v, k]["color"] = CPG_COLORS["AST_EDGE"]
        elif "CFG" in data.get("label"):
            graph.edges[u, v, k]["color"] = CPG_COLORS["CFG_EDGE"]
        elif "DDG" in data.get("label") or "REACHING_DEF" in data.get("label"):
            graph.edges[u, v, k]["color"] = CPG_COLORS["DDG_EDGE"]
        elif "CDG" in data.get("label"):
            graph.edges[u, v, k]["color"] = CPG_COLORS["CDG_EDGE"]
        elif "CALL" in data.get("label"):
            graph.edges[u, v, k]["color"] = CPG_COLORS["CALL_EDGE"]


def main():
    parser = argparse.ArgumentParser(description="Visualize CPG")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("--output", type=str, default="./out/pretty.dot", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    utils.setup_logging(args.verbose)

    graph = utils.read_dot_file(args.input)
    pretty_graph(graph)
    utils.write_dot_file(graph, args.output)


if __name__ == "__main__":
    main()
