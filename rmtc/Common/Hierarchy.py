from rmtc.Common.Options import MAX_INT


class HierarchyNode(object):
    def __init__(self, data):
        self.data = data
        self.edges_to = {}
        """:type : dict[HierarchyNode, dict]"""
        self.edges_from = {}
        """:type : dict[HierarchyNode, dict]"""
        self.successors = {}
        """:type : dict[HierarchyNode, int]"""
        self.predecessors = {}
        """:type : dict[HierarchyNode, int]"""

        self.successor_changed_listeners = []
        """:type : list[() -> void]"""
        self.predecessor_changed_listeners = []
        """:type : list[() -> void]"""

    def add_edge_to(self, vertex_to, edge_properties):
        """:type vertex_to: HierarchyNode"""
        self.edges_to[vertex_to] = edge_properties
        self._update_successors(vertex_to, 1, edge_properties)
        if edge_properties.get('transitive') is True:
            for predecessor, d in self.predecessors.items():
                predecessor._update_successors(vertex_to, 1 + d, edge_properties)

    def add_edge_from(self, vertex_from, edge_properties):
        """:type vertex_from: HierarchyNode"""
        self.edges_from[vertex_from] = edge_properties
        self._update_predecessors(vertex_from, 1, edge_properties)
        if edge_properties.get('transitive') is True:
            for successor, d in self.successors.items():
                successor._update_predecessors(vertex_from, 1 + d, edge_properties)

    def _update_successors(self, successor, distance_to_successor, edge_properties):
        """
        :type successor: HierarchyNode
        :type distance_to_successor : int
        """
        self.successors[successor] = distance_to_successor
        if edge_properties.get('transitive') is True:
            successor_successors = successor.successors
            for s, d in successor_successors.items():
                if s in self.successors:
                    self.successors[s] = min(d + distance_to_successor, self.successors[s])
                else:
                    self.successors[s] = d + distance_to_successor

    def _update_predecessors(self, predecessor, distance_to_predecessor, edge_properties):
        """
        :type predecessor: HierarchyNode
        :type distance_to_predecessor : int
        """
        self.predecessors[predecessor] = distance_to_predecessor
        if edge_properties.get('transitive') is True:
            predecessor_predecessors = predecessor.predecessors
            for s, d in predecessor_predecessors.items():
                if s in self.predecessors:
                    self.predecessors[s] = min(d + distance_to_predecessor, self.predecessors[s])
                else:
                    self.predecessors[s] = d + distance_to_predecessor



class Hierarchy(object):

    def __init__(self):
        self.nodes = {}
        """:type: dict[object, DAGVertex]"""

    def add_element(self, obj):
        assert obj not in self.nodes
        self.nodes[obj] = HierarchyNode(obj)

    def can_add_edge(self, parent, child):
        return self.nodes[parent] not in self.nodes[child].successors

    def add_edge(self, parent, child, **edge_properties):
        vertex_parent = self.nodes[parent]
        vertex_child = self.nodes[child]
        assert vertex_parent not in vertex_child.successors
        vertex_parent.add_edge_to(vertex_child, edge_properties)
        vertex_child.add_edge_from(vertex_parent, edge_properties)


    def get_successors(self, obj):
        assert obj in self.nodes
        vertex = self.nodes[obj]
        return {s.data for s in vertex.successors}

    def get_distance_successor_pairs(self, obj):
        assert obj in self.nodes
        vertex = self.nodes[obj]
        return {(d, s.data) for s, d in vertex.successors.items()}

    def get_predecessors(self, obj):
        assert obj in self.nodes
        vertex = self.nodes[obj]
        return {s.data for s in vertex.predecessors}

    def get_distance_predecessor_pairs(self, obj):
        assert obj in self.nodes
        vertex = self.nodes[obj]
        return {(d, s.data) for s, d in vertex.predecessors.items()}

    def get_distance(self, successor, predecessor):
        successor_vertex = self.nodes[successor]
        predecessor_vertex = self.nodes[predecessor]
        if successor_vertex is predecessor_vertex:
            return 0
        distance = successor_vertex.predecessors.get(predecessor_vertex)
        if distance is None:
            return MAX_INT
        else:
            return distance

    def is_successor_of(self, successor, predecessor):
        successor_vertex = self.nodes[successor]
        predecessor_vertex = self.nodes[predecessor]
        distance = successor_vertex.predecessors.get(predecessor_vertex)
        return distance is not None

    def element_changed(self, obj):
        vertex = self.nodes[obj]
        for p in vertex.predecessors:
            for listener in p.successor_changed_listeners:
                listener()
        for s in vertex.successors:
            for listener in s.predecessor_changed_listeners:
                listener()

    def add_successor_changed_listener(self, obj, listener):
        vertex = self.nodes[obj]
        vertex.successor_changed_listeners.append(listener)

    def add_predecessor_changed_listener(self, obj, listener):
        vertex = self.nodes[obj]
        vertex.predecessor_changed_listeners.append(listener)


if __name__ == "__main__":
    h = Hierarchy()
    h.add_element("a")
    h.add_element("aa")
    h.add_element("ab")
    h.add_element("c")
    h.add_element("d1")
    h.add_element("d2")
    h.add_element("d3")
    h.add_edge("a", "aa")
    h.add_edge("a", "ab")
    h.add_edge("aa", "c")
    h.add_edge("ab", "c")
    h.add_edge("d1", "d2", True)
    h.add_edge("d2", "d3", False)
    h.add_edge("d3", "c")
    # print(h.get_distance_successor_pairs("a"))
    print(h.get_distance_predecessor_pairs("c"))
    def p_listener():
        print("predecessor changed")
    def s_listener():
        print("successor changed")

    h.add_predecessor_changed_listener("ab", p_listener)
    h.add_successor_changed_listener("ab", s_listener)

    h.element_changed("a")
    h.element_changed("c")
    h.element_changed("aa")

