
from graph_io import *
from vertexcoder import *
import time

file = input("Enter file:")

with open(file) as f:
    L = load_graph(f, read_list=True)
    graph1, graph2 = L[0][0], L[0][2]

hashesDictionary = dict()
durations = []
amountOfGraphs = 0

for i in range(len(L)):
    for j in range(len(L[i])):
        amountOfGraphs += 1
        graph =  L[i][j]
        print("Graph ["+str(i)+"]["+str(j)+"]: Amount of vertices: " + str(len(graph.vertices)) + ", Edges: " + str(len(graph.edges)))
        print("Hashing")
        start = time.time()
        coder = VertexCoder.fromGraph(graph)
        coder.generateCode(False)
        end = time.time()
        duration = end-start
        durations.append(duration)
        print('Hashing finished, time: ' + str(duration))
        print("Hash of this graph: " + str(hex(coder.code))+ "\n\n")
        if coder.code not in hashesDictionary:
            hashesDictionary[coder.code] = set()
        hashesDictionary[coder.code].add(graph)

print("Result of this batch: ")
print("Isomorph graphs: ")
amountOfIsmorphGraphs = 0
for g in hashesDictionary:
    print(str(len(hashesDictionary[g])) + " graphs with hash " + str(hex(g)))
    if len(hashesDictionary[g]) > 1:
        amountOfIsmorphGraphs += len(hashesDictionary[g])
print(str(amountOfIsmorphGraphs) + " of isomorph graphs in total\n")
totalDuration = 0
for d in durations:
    totalDuration += d

print("Total duration of this batch: " + str(totalDuration) + " for " + str(amountOfGraphs) + " graphs.")



