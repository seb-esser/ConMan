""" package import """
import xml.etree.ElementTree as ET 

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory



class railML_neo4jmapper:

    
    def __init__(self, myConnector, timestamp, filepath, config):
        self.connector = myConnector
        self.timeStamp = timestamp
        self.config = config
        self.tree = ET.parse(filepath)

    def mapRootedEntities(self):
        
        # builds the objRel to group all subtrees
        root = self.tree.getroot()
        print(root)
        
        # characteristics of root
        root_tag = root.tag
        print(root_tag)

        root_attrs = root.attrib
        print(root_attrs)

        rootedNodeIds = []

        # rooted entities
        for child in root: 
            print('\t{} : {}'.format(child.tag, child.attrib))
            cypher = neo4jGraphFactory.CreateRootedNode(child.attrib['id'], child.tag, self.timeStamp)
            nodeId = self.connector.run_cypher_statement(cypher, 'ID(n)')
            rootedNodeIds.append(nodeId)

        # build objRelNode
        cypher = neo4jGraphFactory.CreateObjectifiedRelNode("null", "railML", self.timeStamp)
        ObjRelNodeId = self.connector.run_cypher_statement(cypher, 'ID(n)')

        # connect rooted nodes and objRelNode
        for rootNode in rootedNodeIds:
            cypher = neo4jGraphFactory.MergeNodesByNodeIDs(ObjRelNodeId[0], rootNode[0])
            self.connector.run_cypher_statement(cypher)



    # public
    def mapResourceEntities(self):
        pass

    # private recursive function
    def getDirectChildren(self):
        pass


