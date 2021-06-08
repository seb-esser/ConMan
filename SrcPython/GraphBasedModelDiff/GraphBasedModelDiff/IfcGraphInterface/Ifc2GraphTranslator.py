""" package import """
import ifcopenshell
import progressbar

""" file import """
from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory


class IFCGraphGenerator:
    """
    IfcP21 to neo4j mapper. 
    Translates a given IFC model in P21 encoding into a propertyGraph 
    """

    # constructor
    """ 
    Public constructor for IFCP21_neo4jMapper
    trigger console output while parsing using the ToConsole boolean
    """

    def __init__(self, connector, model_path, ParserConfig):

        # try to open the ifc model and load the content into the model variable
        try:
            self.model = ifcopenshell.open(model_path)
            ifc_version = self.model.schema
            self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_version)
        except:
            print('file path: {}'.format(model_path))
            raise Exception('Unable to open IFC model on given file path')

        # define the label (i.e., the model timestamp)
        my_label = 'ts' + self.model.wrapped_data.header.file_name.time_stamp
        my_label = my_label.replace('-', '')
        my_label = my_label.replace(':', '')
        self.label = my_label

        # set the connector
        self.connector = connector

        # set output 
        self.parserConfig = ParserConfig
        self.printToConsole = False
        self.printToLog = True

        super().__init__()

    # public entry method to generate the graph out of a given IFC model
    def generateGraph(self):
        # delete entire graph if label already exists
        print('DEBUG INFO: entire graph labeled with >> {} << gets deleted \n'.format(self.label))
        self.connector.run_cypher_statement('MATCH(n:{}) DETACH DELETE n'.format(self.label))

        print('[IFC_P21 > {} < ]: Generating graph... '.format(self.label))

        # extract model data
        obj_definitions = self.model.by_type('IfcObjectDefinition')
        obj_relationships = self.model.by_type('IfcRelationship')
        props = self.model.by_type('IfcPropertyDefinition')

        # parse rooted node + subgraphs
        self.__mapEntities(obj_definitions)

        # parse objectified relationships
        self.__mapObjRelationships(obj_relationships)

        # ToDo: handle IfcPropertyDefinition

        print('[IFC_P21 > {} < ]: Generating graph - DONE. \n '.format(self.label))

    def validateParsingResult(self):
        # ticket_PostEvent-VerifyParsedModel

        # step 1: count entities in IFC model

        # step 2: count number of nodes created in the related graph structure
        # step 2a: identify the graph by its label (i.e., timestamp)
        # step 2b: create a new method in the class Neo4jQueryFactory
        # step 2c: implement a suitable cypher statement into the recently created method in Neo4jQueryFactory
        # step 2d: run the cypher query using the self.connector.run_cypher_statement() 
        # step 2e: access the database response

        # step 3: compare num_entities from the IFC model with the number of nodes detected in the graph

        # step 4: print the test result to console. 

        pass

    # public entry
    def __mapEntities(self, rootedEntities):
        # data for progressbar
        increment = 100 / len(rootedEntities)
        percent = 0
        # loop over all rooted entities
        for entity in rootedEntities:
            # print progressbar
            progressbar.printbar(percent)

            # get some basic data
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build rooted node
            cypher_statement = Neo4jGraphFactory.create_primary_node(entityId, entityType, self.label)
            parent_node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')[0]

            # get all attrs and children
            self.build_node_content(entity, 0, parent_node_id)

            # update progressbar
            percent += increment

        # show last progressbar update
        progressbar.printbar(percent)

    # private recursive function
    def build_node_content(self, entity, indent: int, node_id: int):
        """

        @param entity:
        @param indent:
        @param node_id:
        @return:
        """

        if self.printToConsole:
            print("".ljust(indent * 4) + '{}'.format(entity))

        # print atomic attributes: 
        info = entity.get_info()
        p21_id = info['id']

        # separate associations from class attributes
        node_attribute_names, single_associations, aggregated_associations = self.separate_attributes(entity)

        # define dict of attributes that get directly attached to the node
        node_attr_dict = {}
        for a in node_attribute_names:
            node_attr_dict[a] = info[a]

        # attach p21_id param
        node_attr_dict['p21_id'] = p21_id

        # --1-- append node attributes to current node
        # atomic attrs exist on current node -> map to node
        cypher_statement = Neo4jGraphFactory.add_attributes_by_node_id(node_id, node_attr_dict, self.label)
        self.connector.run_cypher_statement(cypher_statement)

        # --2-- build simple associations with recursive call
        # query all traversal entities (i.e., associated entity instances)
        children = self.model.traverse(entity, 1)[1:]

        for association in single_associations:
            entity = info[association]
            if entity is None:
                continue

            entity_type = entity.get_info()['type']
            p21_id_child = entity.get_info()['id']

            edge_attrs = {'relType': association}

            node_exists = self.check_node_exists(p21_id_child)

            if node_exists:
                # merge with existing
                cy = Neo4jGraphFactory.merge_on_p21(p21_id, p21_id_child, edge_attrs, self.label)
                self.connector.run_cypher_statement(cy)

            else:
                # create new node
                cy = Neo4jGraphFactory.create_secondary_node(
                    parent_id=node_id, entity_type=entity_type, rel_attrs=edge_attrs, timestamp=self.label)
                child_id = self.connector.run_cypher_statement(cy, 'ID(n)')[0]

                # ToDo: consider to kick the recursion after creating all direct associations

                # kick the recursion and attach the attrs to the child node
                self.build_node_content(entity, indent+1, child_id)

        # --3-- build aggregated associations with recursive call
        for association in aggregated_associations:
            entities = info[association]
            i = 0
            if entities is None:
                # detected an array of associations but nothing was referenced within the given instance model
                continue
            for entity in entities:
                try:
                    entity_type = entity.get_info()['type']
                    p21_id_child = entity.get_info()['id']
                except:
                    raise Exception('Failed to query data from entity.')

                edge_attrs = {
                    'relType': association,
                    'listItem': i
                }

                # check if node already exists
                node_exists = self.check_node_exists(p21_id_child)

                if node_exists:
                    # merge with existing
                    cy = Neo4jGraphFactory.merge_on_p21(p21_id, p21_id_child, edge_attrs, self.label)
                    self.connector.run_cypher_statement(cy)

                else:
                    # create new node
                    cy = Neo4jGraphFactory.create_secondary_node(
                        parent_id=node_id, entity_type=entity_type, rel_attrs=edge_attrs, timestamp=self.label)
                    child_id = self.connector.run_cypher_statement(cy, 'ID(n)')[0]

                    # kick the recursion and attach the attrs to the child node
                    self.build_node_content(entity, indent + 1, child_id)

                # increase counter
                i += 1

        return None

    def check_node_exists(self, p21_id_child: int) -> bool:
        """
        check if a node with a specified p21_id already exists in the graph
        @param p21_id_child:
        @return: True or False
        """
        cy = Neo4jQueryFactory.get_node_exists(p21_id=p21_id_child, label=self.label)
        node_exists = self.connector.run_cypher_statement(cy)[0][0]
        return node_exists

    # public entry
    def __mapObjRelationships(self, objRels):

        # loop over all relationships
        for entity in objRels:
            # get some basic data
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build rooted node
            cypher_statement = Neo4jGraphFactory.create_connection_node(entityId, entityType, self.label)
            node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')[0]

            # get all attrs and children
            self.build_node_content(entity, 0, node_id)

    def separate_attributes(self, entity) -> tuple:
        """"
        Queries all attributes of the corresponding entity definition and returns if an attribute has
        attr type value, an entity value or is an aggregation of entities
        @entity:
        @return:
        """
        info = entity.get_info()
        clsName = info['type']
        entity_id = info['id']

        # remove entity_id and type
        info.pop('id')
        info.pop('type')

        # get the class definition for the current instance w.r.t. schema version
        # https://wiki.osarch.org/index.php?title=IfcOpenShell_code_examples#Exploring_IFC_schema

        # separate attributes into node attributes, simple associations, and sets of associations
        node_attributes = []
        single_associations = []
        aggregated_associations = []

        try:
            class_definition = self.schema.declaration_by_name(clsName).all_attributes()
        except:
            raise Exception("Failed to query schema specification in IFC2GraphTranslator.\n "
                            "Schema: {}, Entity: {} ".format(self.schema, clsName))

        for attr in class_definition:
            # check if attribute has attr value in the current entity instance
            # if info[name] is not None:
            #     print('attribute present')
            # else:
            #     print('attribute empty')
            #     continue

            # this is attr quite weird approach but it works
            try:
                attr_type = attr.type_of_attribute().declared_type()
            except:
                attr_type = attr.type_of_attribute()

            # get the value structure
            is_entity = isinstance(attr_type, ifcopenshell.ifcopenshell_wrapper.entity)
            is_type = isinstance(attr_type, ifcopenshell.ifcopenshell_wrapper.type_declaration)
            is_select = isinstance(attr_type, ifcopenshell.ifcopenshell_wrapper.select_type)

            is_pdt_select = False
            is_entity_select = False
            is_nested_select = False

            # ToDo: Distinguish if it is a select of entities or a select of predefinedTypes
            if is_select:
                # methods = attr.type_of_attribute().declared_type()
                # print(dir(methods))
                lst = attr.type_of_attribute().declared_type().select_list()

                is_entity_select = all([isinstance(x, ifcopenshell.ifcopenshell_wrapper.entity) for x in lst])
                is_pdt_select = all([isinstance(x, ifcopenshell.ifcopenshell_wrapper.type_declaration) for x in lst])
                is_nested_select = all([isinstance(x, ifcopenshell.ifcopenshell_wrapper.select_type) for x in lst])

            is_enumeration = isinstance(attr_type, ifcopenshell.ifcopenshell_wrapper.enumeration_type)
            is_aggregation = isinstance(attr_type, ifcopenshell.ifcopenshell_wrapper.aggregation_type)

            # catch some weird cases with IfcDimensionalExponents
            #  as this entity doesnt use types but atomic attr declarations
            if attr.name() in ['LengthExponent',
                               'MassExponent',
                               'TimeExponent',
                               'ElectricCurrentExponent',
                               'ThermodynamicTemperatureExponent',
                               'AmountOfSubstanceExponent',
                               'LuminousIntensityExponent',
                               'Exponent',      # from IfcDerivedUnitElement
                               'Precision',     # from IfcGeometricRepresentationContext
                               'Scale'          # from IfcCartesianPointTransformationOperator3D in 2x3
                               ]:
                node_attributes.append(attr.name())

            elif is_type or is_enumeration or is_pdt_select or is_nested_select:
                node_attributes.append(attr.name())
            elif is_entity or is_entity_select:
                single_associations.append(attr.name())
            elif is_aggregation:
                # ToDo: check if it is an aggregation of types or an aggregation of entities
                if attr.name() in ['Coordinates',
                                   'DirectionRatios',
                                   'CoordList',
                                   'segments',
                                   'MiddleNames',
                                   'PrefixTitles',
                                   'SuffixTitles',
                                   'Roles',
                                   'Addresses',
                                   'CoordIndex',
                                   'InnerCoordIndices'
                                   ]:
                    node_attributes.append(attr.name())
                else:
                    aggregated_associations.append(attr.name())
            else:
                raise Exception('Tried to encode the attribute type of entity #{} clsName: {} attribute {}. '
                                'Please check your graph translator.'.format(entity_id, clsName, attr.name()))

        return node_attributes, single_associations, aggregated_associations
