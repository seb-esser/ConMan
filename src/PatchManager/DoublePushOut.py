from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class DoublePushOut:
    def __init__(self, lhs, i, rhs):
        self.left_hand_side: GraphPattern = lhs
        self.interface: GraphPattern = i
        self.right_hand_side: GraphPattern = rhs


    def cypher_statement(self):
        """

        """
        cy = """match(n1{GlobalId: 1})-[r1]->(n5)<-[r2]-(n4{GlobalId:4}) DELETE r1, r2, n5 return n1, n4"""


    def calc_stuff_to_be_removed(self):
        """

        """
        rmv_nodes = []
        rmv_edges = []
