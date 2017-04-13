
from graph_io import *
from vertexcoder import *

with open('bigtrees1.grl') as f:
    L = load_graph(f, read_list=True)
    graph1, graph2 = L[0][0], L[0][2]

coder1 = VertexCoder.fromGraph(graph1)
coder2 = VertexCoder.fromGraph(graph2)

print("Hashing graph 1...")
coder1.generateCode(True)
print("Hashing graph 2...")
coder2.generateCode(True)

with open('graph1.dot', 'w') as f:
    write_dot(graph1, f, graph1.directed)
with open('graph2.dot', 'w') as f:
    write_dot(graph2, f, graph1.directed)

with open('vertexcodertree1.dot', 'w') as f:
    write_dot(coder1.toGraph(), f, graph1.directed)
with open('vertexcodertree2.dot', 'w') as f:
    write_dot(coder2.toGraph(), f, graph2.directed)

print(hex(coder1.code))
print(hex(coder2.code))


