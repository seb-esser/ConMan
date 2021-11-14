""" package import """
import re

""" file import """
from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
import xml.etree.ElementTree as ET

class CityGMLGraphGenerator:
    
    """
    CityGML to neo4j mapper. 
    Parses a given citygml file and maps its contents to a neo4j graph
    """
    # constructor


    def __init__(self, connector, file_path):

        # get the root of the tree
        self.root = ET.parse(file_path).getroot()
        self.connector = connector
        my_label = self.root.findtext('{http://www.opengis.net/gml}name')
        my_label = my_label.replace('-', '')
        my_label = my_label.replace('\n', '')
        my_label = my_label.replace(' ', '')
        self.label = my_label
        
    
    def generateGraph(self):
        """
        parses the CityGML model into the graph database
        @return: the label, by which you can identify the model in the database
        """

        # delete entire graph if label already exists
        print('DEBUG INFO: entire graph labeled with >> {} << gets deleted \n'.format(
            self.label))
        self.connector.run_cypher_statement(
            'MATCH(n:{}) DETACH DELETE n'.format(self.label))

        print('[CityGML > {} < ]: Generating graph... '.format(self.label))

        # map the root
        root_id = self.__mapEntity(self.root, 'PrimaryNode')
        self.__buildNodes(self.root, root_id)
        
    
    def __buildNodes(self, entity, parent_id):
        # recursive method
        
        # get all children (1 level below)
        children = entity.findall('./')
        if not children:
            pass
        else:
            # iterate over all children
            for child in children:

                # map the entity as a secondary node
                child_id = self.__mapEntity(child, 'SecondaryNode')
                cypher_statement = Neo4jGraphFactory.merge_on_node_ids(parent_id, child_id)
                self.connector.run_cypher_statement(cypher_statement)
                
                self.__buildNodes(child, child_id)
    
    
    def __mapEntity(self, entity, label):
        
        # get the tag of the entity (remove the namespace)
        tag = re.sub("[\{].*?[\}]", "", entity.tag)
        my_dict = {'EntityType': tag}
        
        # run cypher command
        cypher_statement = Neo4jGraphFactory.create_node_with_attr(
            label , my_dict, self.label)
        node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')[0]
        return node_id
        