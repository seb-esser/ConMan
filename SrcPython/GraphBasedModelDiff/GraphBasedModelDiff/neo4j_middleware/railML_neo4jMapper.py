""" package import """
import xml.etree.ElementTree as ET 
from lxml import etree

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory



class railML_neo4jmapper:

    
    def __init__(self, myConnector, timestamp, filepath, config):
        self.connector = myConnector
        self.timeStamp = timestamp
        self.config = config

        xsd_file_path = './00_sampleData/RailML_xml/schema/railML3-1/'
        namespaces = ['common3', 
                      'infrastructure3', 
                      'interlocking3', 
                      'railml3', 
                      'rollingstock3', 
                      'rtm4railml3', 
                      'timetable3']

        self.subschemas = {}

        for ns in namespaces:
            # load schema definition       
            with open(xsd_file_path + ns + '.xsd') as f:
                xmlschema_doc = etree.parse(f)
                # store schema for namespace
                self.subschemas[ns] = xmlschema_doc


        # snippet for validation
        # xmlschema = etree.XMLSchema(xmlschema_doc)

        # load instance data
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

        #iter = root.iter()
        
        #for i in iter:
        #    print(i)

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

        for rootedItem in self.tree.getroot():
            self.getDirectChildren(rootedItem, 1)


    # private recursive function
    def getDirectChildren(self, parent, indent = 0):


        for child in parent:             

            print("".ljust(indent*4) + '{}\t{}'.format(child.tag, child.attrib))
            
            self.getDirectChildren(child, indent + 1)

        


