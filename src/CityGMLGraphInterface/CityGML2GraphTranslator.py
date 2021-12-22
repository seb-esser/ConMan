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

        attributes = self.filterNodesToAttributes(entity)

        # map the entity
        entity_id = self.__mapEntity(entity, 'SecondaryNode', attributes)

        cypher_statement = Neo4jGraphFactory.merge_on_node_ids(
            parent_id, entity_id)
        self.connector.run_cypher_statement(cypher_statement)

        # get all children (1 level below)
        children = entity.findall('./')
        if not children:
            pass
        else:
            # iterate over all children
            for child in children:

                if not self.checkTags(child):

                    # recursive call
                    self.__buildNodes(child, entity_id)

    def __mapEntity(self, entity, label, attributes=None):

        # print the progressbar
        progressbar.printbar(self.percent)

        # get the attribute dictionary of the entity
        attrs = entity.attrib

        # remove all the namespaces
        key_list = list(attrs.keys())
        for key in key_list:
            new_key = self.removeNs(key)
            attrs[new_key] = attrs.pop(key)

        # get the tag of the entity (remove the namespace)
        tag = self.removeNs(entity.tag)
        attrs["EntityType"] = tag

        # get the text if there is one
        # if it is a position, then convert the text into individual coord-attributes
        if entity.text:
            if entity.tag == '{http://www.opengis.net/gml}pos':
                xyz = entity.text.split()
                attrs["X"] = xyz[0]
                attrs["Y"] = xyz[1]
                attrs["Z"] = xyz[2]
            else:
                attrs["Text"] = entity.text

        if attributes != None:
            attrs.update(attributes)

        # run cypher command
        cypher_statement = Neo4jGraphFactory.create_node_with_attr(
            label, attrs, self.label)
        node_id = self.connector.run_cypher_statement(
            cypher_statement, 'ID(n)')[0]

        # increment the percentage and return the id
        self.percent += self.increment
        return node_id

    def filterNodesToAttributes(self, entity):

        attrs = {}
        for child in entity.findall('./'):
            if self.checkTags(child):
                if self.removeNs(child.tag) == 'measureAttribute' or self.removeNs(child.tag) == 'stringAttribute':

                    attr_name = child.attrib['name']
                    child2 = child.findall('./')[0]

                    if 'uom' in child2.attrib.keys():
                        attr_name = attr_name + child2.attrib['uom']

                    attrs[attr_name] = child2.text

                else:  # child.text:
                    attrs[self.removeNs(child.tag)] = child.text

        return attrs

    def checkTags(self, entity):
        # check if a node should actually be an attribute of the parent node
        # xml namespaces
        core = '{http://www.opengis.net/citygml/2.0}'
        bldg = '{http://www.opengis.net/citygml/building/2.0}'
        gen = '{http://www.opengis.net/citygml/generics/2.0}'
        grp = '{http://www.opengis.net/citygml/cityobjectgroup/2.0}'
        app = '{http://www.opengis.net/citygml/appearance/2.0}'
        gml = '{http://www.opengis.net/gml}'
        xAL = '{urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}'
        xLink = '{http://www.w3.org/1999/xlink}'
        xsi = '{http://www.w3.org/2001/XMLSchema-instance}'

        # tags of nodes to be converted to attributes for the node "building"
        building_list = ['{}description'.format(gml),
                         '{}name'.format(gml),
                         '{}creationDate'.format(core),
                         '{}relativeToTerrain'.format(core),
                         '{}class'.format(bldg),
                         '{}function'.format(bldg),
                         '{}usage'.format(bldg),
                         '{}yearOfConstruction'.format(bldg),
                         '{}roofType'.format(bldg),
                         '{}measuredHeight'.format(bldg),
                         '{}storeysAboveGround'.format(bldg),
                         '{}storeysBelowGround'.format(bldg),
                         '{}measureAttribute'.format(gen),
                         '{}stringAttribute'.format(gen)]

        if entity.tag in building_list:
            return True
        else:
            return False

    def removeNs(self, text):
        return re.sub("[\{].*?[\}]", "", text)
