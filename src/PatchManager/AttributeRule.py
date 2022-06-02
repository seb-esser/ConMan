from neo4j_middleware.ResponseParser.GraphPath import GraphPath


class AttributeRule:
    """
    Representation of attribute modifications as part of patches
    """
    def __init__(self, path: GraphPath, attribute_name: str, init_value, updated_value):
        """

        @param path:
        @param attribute_name:
        @param init_value:
        @param updated_value:
        @return:
        """
        self.path: GraphPath = path
        self.attribute_name = attribute_name
        self.init_value = init_value
        self.updated_value = updated_value


