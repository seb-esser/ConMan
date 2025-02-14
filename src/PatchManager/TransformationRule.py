import networkx

from PatchManager.DoublePushOut import DoublePushOut
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class TransformationRule:
    """
    Optimized representation of graph transformation rule which can be transferred into a DPO rule
    """

    def __init__(self, gluing_pattern: GraphPattern, push_out_pattern: GraphPattern, context_pattern: GraphPattern,
                 operation_type):

        self.push_out_pattern = push_out_pattern
        self.gluing_pattern = gluing_pattern
        self.context_pattern = context_pattern
        self.operation_type = operation_type

    def get_dpo_rule(self) -> DoublePushOut:
        """
        translates glue, context, and pushout into DPO rule
        @return:
        """
        # finally compile DPO rule
        lhs = None
        interface = None
        rhs = None

        if self.operation_type == StructuralModificationTypeEnum.ADDED:
            # construct lhs
            lhs = self.context_pattern
            # construct interface
            interface = self.context_pattern
            # construct rhs
            context_paths = self.context_pattern.paths
            push_out_paths = self.push_out_pattern.paths
            gluing_paths = self.gluing_pattern.paths

            paths = context_paths + push_out_paths + gluing_paths
            rhs = GraphPattern(paths=paths)

        elif self.operation_type == StructuralModificationTypeEnum.DELETED:
            # -- construct lhs --
            context_paths = self.context_pattern.paths
            push_out_paths = self.push_out_pattern.paths
            gluing_paths = self.gluing_pattern.paths

            print(self.gluing_pattern.to_cypher_match())
            print(self.push_out_pattern.to_cypher_match())

            paths = context_paths + push_out_paths + gluing_paths
            lhs = GraphPattern(paths=paths)

            # -- construct rhs --
            rhs = self.context_pattern
            # -- construct interface --
            interface = self.context_pattern

        return DoublePushOut(lhs, interface, rhs)

    def run_cleanup(self):
        """
        run clean up and remove unnecessary attributes
        @return:
        """
        self.context_pattern.tidy_node_attributes()
        self.gluing_pattern.tidy_node_attributes()
        self.push_out_pattern.tidy_node_attributes()

    def get_nx_graph(self):
        """

        @return:
        """

        node_highlighter = ""
        if self.operation_type == StructuralModificationTypeEnum.DELETED:
            node_highlighter = "REMOVED"
        elif self.operation_type == StructuralModificationTypeEnum.ADDED:
            node_highlighter = "INSERTED"

        push = self.push_out_pattern.to_nx_graph(cluster_type="pushout", node_highlighter=node_highlighter)
        context = self.context_pattern.to_nx_graph(cluster_type="context")
        glue = self.gluing_pattern.to_nx_graph(cluster_type="glue")

        graph = networkx.compose_all([context, glue, push])

        return graph
