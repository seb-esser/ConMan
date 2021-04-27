

from neo4j_middleware.Neo4jQueryUtilities import Neo4jQueryUtilities as neo4jUtils


class SccDetector:
    """description of class"""

    def __init__(self, connector,  label, printToConsole = True):
        self.label = label
        self.connector = connector
        self.printToConsole = printToConsole


    def performSCC(self):
        call = "CALL gds.alpha.scc.stream({"
        nodeQuery = "  nodeQuery: 'MATCH (u:{}) RETURN id(u) AS id',".format(self.label)
        relQuery = "  relationshipQuery: 'MATCH (u1:{})-->(u2:{}) RETURN id(u1) AS source, id(u2) AS target'".format(self.label, self.label)
        closing = "})"
        unpackParams = "YIELD nodeId,componentId"
        ret = "RETURN gds.util.asNode(nodeId).p21_id AS p21_id, nodeId as NodeId, componentId AS Component"
        sort = "ORDER BY Component DESC"

        cypher = neo4jUtils.BuildMultiStatement( [call, nodeQuery, relQuery, closing, unpackParams, ret, sort] )
        raw = self.connector.run_cypher_statement(cypher)
        self.results = raw
       
        if self.printToConsole:
            print('{:<10} \t {:<10} \t {:<10}'.format('p21_id', 'nodeId', 'componentValue'))
            for res in raw: 
                print('{:<10} \t {:<10} \t {:<10}'.format(res[0], res[1], res[2]))

    def evaluateResults(self):
        data = self.results
        # ToDo: implement an analysis to check if the model/graph contains strongly connected components 
        raise Exception('Evaluation of SCC results is not implemented yet. ')



