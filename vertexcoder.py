import hashlib
import operator
import struct
from queue import *
from typing import Dict, Tuple

import math

from util import *
from graph import *


class VertexCoder(object):

    @staticmethod
    def fromGraph(graph: "Graph") -> "VertexCoder":
        """
        Creates a vertex coder tree from a graph instance.
        :param graph: The graph to create a vertex coder tree for.
        :return: The root of the vertex coder tree.
        """

        self = VertexCoder(None, None, None, 0, None)

        for v in graph.vertices:
            child = VertexCoder(v, None, self, 1, dict())
            self.children.append(child)

        return self

    def __init__(self, vertex: Vertex,
                 parentEdge: Edge,
                 creator: "VertexCoder",
                 generation: int,
                 vertexMap: Dict[Tuple[Vertex, Edge], "VertexCoder"]):
        self._vertex = vertex
        self._parentEdge = parentEdge
        self._code = None
        self._children = list()
        self._creator = creator
        self._isExpanded = False
        self._vertexMap = vertexMap
        self._generation = generation
        self._oldCode = 0

    def __str__(self):
        return 'Generation={}, Vertex={}, ParentEdge={}, Children={}'.format(
            self.generation,
            self.vertex,
            self.parentEdge,
            len(self.children))

    @property
    def vertex(self) -> Vertex:
        return self._vertex

    @vertex.setter
    def vertex(self, value: Vertex):
        self._vertex = value

    @property
    def parentEdge(self) -> Edge:
        return self._parentEdge

    @parentEdge.setter
    def parentEdge(self, value: Edge):
        self._parentEdge = value

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str):
        self._code = value

    @property
    def children(self) -> List["VertexCoder"]:
        return self._children

    @property
    def creator(self) -> "VertexCoder":
        return self._creator

    @creator.setter
    def creator(self, value: "VertexCoder"):
        self._creator = value

    @property
    def isExpanded(self):
        return self._isExpanded

    @property
    def generation(self) -> int:
        return self._generation

    @generation.setter
    def generation(self, value: int):
        self._generation = value

    @property
    def vertexMap(self) -> Dict[Tuple[Vertex, Edge], "VertexCoder"]:
        return self._vertexMap

    def generateCode(self, hashLabels: bool):
        """
        Generates the hash code of the vertex coder and puts the result in self.code.
        :param hashLabels: True if edge labels should be taken into account, false otherwise.
        """
        # The root has no vertex in the vertex coder tree and a child for each vertex.
        if self.vertex is None:

            with open('intermediate0.dot', 'w') as f:
                from graph_io import write_dot
                write_dot(self.toGraph(), f, False)

            # Iteratively expand children until either fully
            # expanded or all have distinct codes.
            for child in self.children:
                child.expand()

            while True:
                # Initially generate codes without labels to encode structure
                for child in self.children:
                    child.generateCode(False)

                # Sort to ensure uniformity
                self.children.sort(key=operator.attrgetter("code"))

                # Check for a consecutive unexpanded pair of children with same code.
                isDistinct = True
                i = 0
                while i < len(self.children) - 1:
                    if not self.children[i].isExpanded and self.children[i].code == self.children[i + 1].code:
                        isDistinct = False
                        break
                    i += 1

                # Done when all vertices are either fully expanded or distinct.
                if isDistinct:
                    break

                # Expand range of equivalent children

                j = i + 1
                while j < len(self.children) and self.children[i].code == self.children[j].code:
                    j += 1

                while i < j:
                    self.children[i].expand()
                    i += 1

        # Recursively generate code
        self._oldCode = self.code
        for child in self.children:
            child.generateCode(hashLabels)

        self.children.sort(key=operator.attrgetter("code"))

        # Construct code from vertex, parent edge and childrens' codes
        content = 0
        if self.vertex is not None:
            if hashLabels and self.parentEdge is not None and self.parentEdge.weight is not None:
                content += self.parentEdge.weight

            if not self.vertex.graph.directed:
                content += 2
            elif self.generation == 1 or self.parentEdge.head == self.vertex:
                content += 1

        for child in self.children:
            content += int(child.code)

        contentBytes = str(content).encode()
        self._code = int.from_bytes(hashlib.sha1(contentBytes).digest(), byteorder='big')

        if self._oldCode == self._code:
            self._isExpanded = True

    def expand(self):
        """
        Expands the vertex coder.
        """

        if self._isExpanded:
            return
        if len(self._children) == 0:
            # Expand this vertex
            for edge in self.vertex.incidence:
                if self._vertex == edge.tail:
                    child = None
                    if (edge.head, edge) in self.vertexMap:
                        child = self.vertexMap[(edge.head, edge)]
                        # Share next generation coder
                        if child.generation == self._generation + 1:
                            self.children.append(child)
                    else:
                        child = VertexCoder(edge.head, edge, self, self._generation + 1, self.vertexMap)
                        self._children.append(child)
                        self._vertexMap[(edge.head, edge)] = child

                else: # Vertex is target
                    if (edge.tail, edge) in self.vertexMap:
                        child = self.vertexMap[(edge.tail, edge)]
                        if child.generation == self._generation + 1:
                            self.children.append(child)
                    else:
                        child = VertexCoder(edge.tail, edge, self, self._generation + 1, self.vertexMap)
                        self.children.append(child)
                        self.vertexMap[(edge.tail, edge)] = child
        else:
            # Expand deeper
            for i in range(0, len(self.vertex.incidence)):
                # Only coder creator can expand to prevent duplicate expansion
                if self.children[i].creator == self:
                    self.children[i].expand()

    def toGraph(self):
        """
        Converts the vertex coder and its children to a graph.
        :return: The graph representing the structure of the vertex coder.
        """

        g = Graph(directed=True)

        root = Vertex(g, label="root")
        g.add_vertex(root)

        mapping = dict()
        mapping[self] = root

        agenda = Queue()
        agenda.put(self)

        while not agenda.empty():
            current = agenda.get()

            for child in current.children:
                if child not in mapping:
                    vertex = Vertex(g, label=child.vertex.label)
                    g.add_vertex(vertex)
                    mapping[child] = vertex
                else:
                    vertex = mapping[child]

                if child.parentEdge is not None:
                    direction = "f" if child.parentEdge.tail == current.vertex else "b"
                    weight = "{}({})".format(child.parentEdge.weight, direction)
                else:
                    weight = ""

                g.add_edge(Edge(mapping[current], vertex, weight=weight))
                agenda.put(child)

        return g