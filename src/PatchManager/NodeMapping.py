from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class NodeMapping:
    """
    utility class to exchange mappings of nodes that are considered to be equal between two graphs
    """
    def __init__(self, node_init: NodeItem, node_updated: NodeItem, ts_init: str, ts_updated: str):
        """

        @param node_init:
        @param node_updated:
        @param ts_init:
        @param ts_updated:
        """
        self.Node_initial: NodeItem = node_init
        self.Node_updated: NodeItem = node_updated
        self.ts_initial: str = ts_init
        self.ts_updated: str = ts_updated
