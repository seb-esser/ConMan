""" package import """
import progressbar
from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
import re
import xml.etree.ElementTree as ET

""" file import """


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

        # data for progressbar
        self.increment = 100 / len(self.root.findall(".//*"))
        self.percent = 0

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
                cypher_statement = Neo4jGraphFactory.merge_on_node_ids(
                    parent_id, child_id)
                self.connector.run_cypher_statement(cypher_statement)

                self.__buildNodes(child, child_id)

    def __mapEntity(self, entity, label):

        # print the progressbar
        progressbar.printbar(self.percent)

        # get the attribute dictionary of the entity
        attrs = entity.attrib
        
        # remove all the namespaces
        key_list = list(attrs.keys())    
        for key in key_list:
            new_key = re.sub("[\{].*?[\}]", "", key)
            attrs[new_key] = attrs.pop(key)

        # get the tag of the entity (remove the namespace)
        tag = re.sub("[\{].*?[\}]", "", entity.tag)
        attrs["EntityType"] = tag

        # get the text if there is one
        # if it is a position, then convert the text into individual coord-attributes
        if entity.text:
            if re.sub("[\{].*?[\}]", "", entity.tag) == 'pos':
                xyz = entity.text.split()
                attrs["X"] = xyz[0]
                attrs["Y"] = xyz[1]
                attrs["Z"] = xyz[2]
            else:
                attrs["Text"] = entity.text
        

        # run cypher command
        cypher_statement = Neo4jGraphFactory.create_node_with_attr(
            label, attrs, self.label)
        node_id = self.connector.run_cypher_statement(
            cypher_statement, 'ID(n)')[0]

        # increment the percentage and return the id
        self.percent += self.increment
        return node_id
