from utils import read_dot_file, write_dot_file
import networkx as nx

merged = read_dot_file("out/pretty.dot")
output = read_dot_file("out/output.dot")
diff = nx.difference(output, merged)
write_dot_file(diff, "out/diff.dot")
