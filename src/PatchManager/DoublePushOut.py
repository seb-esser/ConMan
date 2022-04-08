from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class DoublePushOut:
    def __init__(self, lhs, i, rhs):
        self.left_hand_side: GraphPattern = lhs
        self.interface: GraphPattern = i
        self.right_hand_side: GraphPattern = rhs

    def to_cypher_serialization(self):
        raise NotImplementedError("not yet implemented")

    @classmethod
    def from_cypher_serialization(cls, raw):
        raise NotImplementedError("not yet implemented")

    def to_json_serialization(self):
        raise NotImplementedError("not yet implemented")

    @classmethod
    def from_json_serialization(cls, raw):
        raise NotImplementedError("not yet implemented")

    def plot_patterns(self):
        print("DPO cyphers: ")
        print("LHS:")
        print(self.left_hand_side.to_cypher_match())
        print("Interface:")
        print(self.interface.to_cypher_match())
        print("RHS:")
        print(self.right_hand_side.to_cypher_match())

