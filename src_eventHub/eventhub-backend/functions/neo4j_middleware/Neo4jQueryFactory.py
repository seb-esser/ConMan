from functions.neo4j_middleware.Neo4jFactory import Neo4jFactory


class Neo4jQueryFactory(Neo4jFactory):

    @classmethod
    def get_loaded_models(cls):
        """ returns a cypher statement to query a node by its P21_id and a given (optional) label. """
        cy = 'MATCH (n:PrimaryNode{EntityType: \"IfcProject\"}) return n.Name, LABELS(n)'
        return cy


