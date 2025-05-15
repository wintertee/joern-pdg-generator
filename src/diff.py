import json
from pprint import pprint

from utils import read_dot_file

merged = read_dot_file("out/merged.dot")
filtered = read_dot_file("out/filtered.dot")

merged_nodes = list(merged.nodes(data=True))
filtered_nodes = list(filtered.nodes(data=True))

for i, (node, data) in enumerate(merged_nodes):
    merged_nodes[i] = (node, json.dumps(data))
for i, (node, data) in enumerate(filtered_nodes):
    filtered_nodes[i] = (node, json.dumps(data))
merged_nodes = set(merged_nodes)
filtered_nodes = set(filtered_nodes)
diff = merged_nodes - filtered_nodes
pprint(diff)
print(f"Filtered nodes not in merged: {len(diff)}")


# merged_edges = list(merged.edges(data=True))
# filtered_edges = list(filtered.edges(data=True))

# for i, (u, v, data) in enumerate(merged_edges):
#     merged_edges[i] = (u, v, json.dumps(data))

# for i, (u, v, data) in enumerate(filtered_edges):
#     filtered_edges[i] = (u, v, json.dumps(data))

# merged_edges = set(merged_edges)
# filtered_edges = set(filtered_edges)

# diff = filtered_edges - merged_edges

# pprint(filtered_edges - merged_edges)

# print(f"Filtered edges not in merged: {len(diff)}")
