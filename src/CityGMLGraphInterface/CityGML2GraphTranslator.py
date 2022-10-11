""" package import """
import re
import xml.etree.ElementTree as ET

""" file import """
from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
import progressbar


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
        """
        Recursive Method to map to build all nodes beginning from the root
        """

        # get the attribute dictionary of child entites which only contain information about the parent nodes
        attributes = self.filterEntitiesToAttributes(entity)

        # map the primary_node_type
        entity_id = self.__mapEntity(entity, 'SecondaryNode', attributes)

        # merge with parent node
        cypher_statement = Neo4jGraphFactory.merge_on_node_ids(
            parent_id, entity_id)
        self.connector.run_cypher_statement(cypher_statement)

        # get all children (1 level below)
        children = entity.findall('./')
        
        # exit statement
        if not children:
            pass
        else:
            # iterate over all children
            for child in children:
                
                # check the tags (again)
                if not self.checkTags(child):

                    # recursive call
                    self.__buildNodes(child, entity_id)


    def __mapEntity(self, entity, label, attributes=None):

        """
        Maps an primary_node_type to the database with a given label and attribute dict
        """
        # print the progressbar
        self.percent += self.increment
        progressbar.print_bar(self.percent)

        # get the attribute dictionary of the primary_node_type
        attrs = entity.attrib

        # remove all the namespaces
        key_list = list(attrs.keys())
        for key in key_list:
            new_key = self.removeNs(key)
            attrs[new_key] = attrs.pop(key)

        # get the tag of the primary_node_type (remove the namespace)
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
        cypher_statement = Neo4jGraphFactory.merge_node_with_attr(label, attrs, self.label)
        node_id = self.connector.run_cypher_statement(
            cypher_statement, 'ID(n)')[0]
        
        return node_id

    def filterEntitiesToAttributes(self, entity):
        """
        Filters entities and converts them to attributes of the parent node 
        """

        # create an empty dictionary
        attrs = {}
        
        # iterate over all direct childs (1 level down)
        for child in entity.findall('./'):

            # check whether the primary_node_type is within the list
            if self.checkTags(child):

                # measureAttribute and stringAttribute always have a name and a child primary_node_type which carries the value
                if self.removeNs(child.tag) == 'measureAttribute' or self.removeNs(child.tag) == 'stringAttribute':
                    
                    # get the name from the attribute dictionary
                    attr_name = child.attrib['name']
                    
                    # get the child
                    child2 = child.findall('./')[0]

                    # if that child has a unit of measurement, add that to the attribute name
                    if 'uom' in child2.attrib.keys():
                        attr_name = attr_name + child2.attrib['uom']

                    # add the new key and value to the dictionary
                    attrs[attr_name] = child2.text

                # most oter entites simply contain text
                else:
                    attrs[self.removeNs(child.tag)] = child.text

        # return the dictionary
        return attrs

    def checkTags(self, entity):
        """
        Checks the tag of an primary_node_type to determine whether it should be an attribute of the parent node
        """
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
        """
        Removes the namespace in front of a tag
        """
        return re.sub("[\{].*?[\}]", "", text)
