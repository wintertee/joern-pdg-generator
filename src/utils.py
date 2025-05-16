import logging

from networkx.drawing.nx_agraph import read_dot, write_dot

logger = logging.getLogger(__name__)


def read_dot_file(file_path):
    graph = read_dot(file_path)
    logger.debug(f"Loaded {graph} from {file_path}")
    return graph


def write_dot_file(graph, output_file):
    """
    Write a graph to a .dot file.

    Args:
        graph (networkx.Graph): The graph to write
        output_file (str): Path to the output .dot file
    """
    logger.info(f"Writing {graph} to {output_file}")
    write_dot(graph, output_file)
