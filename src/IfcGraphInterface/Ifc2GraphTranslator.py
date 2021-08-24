""" package import """
import ifcopenshell
import progressbar
import concurrent.futures

""" file import """
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory

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
            self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(
                ifc_version)
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
        """
        parses the IFC model into the graph database
        @return: the label, by which you can identify the model in the database
        """

        # delete entire graph if label already exists
        print('DEBUG INFO: entire graph labeled with >> {} << gets deleted \n'.format(
            self.label))
        self.connector.run_cypher_statement(
            'MATCH(n:{}) DETACH DELETE n'.format(self.label))

        print('[IFC_P21 > {} < ]: Generating graph... '.format(self.label))

        # extract model data

        type_list = self.model.types()
        entity_list = []
        for type in type_list:
            elements = self.model.by_type(type, False)
            entity_list += elements

        # Split list into n equal chunks for threading
        n = 4
        split_list = list(entity_list[i::n] for i in range(n))

        
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.thread_target, split_list)
            #print(results)

            #for f in concurrent.futures.as_completed(results):
            #    print(f.result())
        # props = self.model.by_type('IfcPropertyDefinition')

        # parse rooted node + subgraphs
        # self.__mapPrimaryEntity(obj_definitions)
        # self.__mapObjrelationships(obj_relationships)

        # parse objectified relationships
        # self.__mapObjRelationships(obj_relationships)

        # ToDo: handle IfcPropertyDefinition

        print('[IFC_P21 > {} < ]: Generating graph - DONE. \n '.format(self.label))

        return self.label

    # method for threading
    def thread_target(self, entity_list):
        # Data for progressbar
        increment = 100 / len(entity_list)
        percent = 0
        for entity in entity_list:
                
            # print progressbar
            progressbar.printbar(percent)
                
            # check if the entity is either an ObjectDef or Relationship or neither
            if entity.is_a('IfcObjectDefinition'):
                self.__mapPrimaryEntity(entity)
            elif entity.is_a('IfcRelationship'):
                self.__mapObjRelationship(entity)
            else:
                self.__mapSecondaryEntity(entity)

            # add increment to percentage
            percent += increment
            
        progressbar.printbar(percent)
        return None
        
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
    def __mapPrimaryEntity(self, entity):
        
        # get some basic data
        info = entity.get_info()
        entityId = info['GlobalId']
        entityType = info['type']
        
        # neo4j: build rooted node
        cypher_statement = Neo4jGraphFactory.create_primary_node(entityId, entityType, self.label)
        parent_node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')[0]
        
        # get all attrs and children
        self.build_node_content(entity, 0, parent_node_id)
        
    def __mapSecondaryEntity(self, entity):
        info = entity.get_info()
        entityType = info['type']

        cypher_statement = Neo4jGraphFactory.create_secondary_node_wouRels(entityType, self.label)
        node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')[0]
        
        self.build_node_content(entity, 0, node_id)
        
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
        node_attribute_names, _, _ = self.separate_attributes(
            entity)

        # define dict of attributes that get directly attached to the node
        node_attr_dict = {}
        for a in node_attribute_names:
            node_attr_dict[a] = info[a]

        # attach p21_id param
        node_attr_dict['p21_id'] = p21_id

        # --1-- append node attributes to current node
        # atomic attrs exist on current node -> map to node
        cypher_statement = Neo4jGraphFactory.add_attributes_by_node_id(
            node_id, node_attr_dict, self.label)
        self.connector.run_cypher_statement(cypher_statement)

        

    def check_node_exists(self, p21_id_child: int) -> bool:
        """
        check if a node with a specified p21_id already exists in the graph
        @param p21_id_child:
        @return: True or False
        """
        cy = Neo4jQueryFactory.get_node_exists(
            p21_id=p21_id_child, label=self.label)
        node_exists = self.connector.run_cypher_statement(cy)[0][0]
        return node_exists

    # public entry
    def __mapObjRelationship(self, objRel):

        # loop over all relationships
        
            # get some basic data
        info = objRel.get_info()
        entityId = info['GlobalId']
        entityType = info['type']
        # neo4j: build rooted node
        cypher_statement = Neo4jGraphFactory.create_connection_node(
            entityId, entityType, self.label)
        node_id = self.connector.run_cypher_statement(
            cypher_statement, 'ID(n)')[0]
        # get all attrs and children
        self.build_node_content(objRel, 0, node_id)

    
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
            class_definition = self.schema.declaration_by_name(
                clsName).all_attributes()
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
            is_entity = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.entity)
            is_type = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.type_declaration)
            is_select = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.select_type)

            is_pdt_select = False
            is_entity_select = False
            is_nested_select = False

            # ToDo: Distinguish if it is a select of entities or a select of predefinedTypes
            if is_select:
                # methods = attr.type_of_attribute().declared_type()
                # print(dir(methods))
                lst = attr.type_of_attribute().declared_type().select_list()

                is_entity_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.entity) for x in lst])
                is_pdt_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.type_declaration) for x in lst])
                is_nested_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.select_type) for x in lst])

            is_enumeration = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.enumeration_type)
            is_aggregation = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.aggregation_type)

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
                               'Scale',          # from IfcCartesianPointTransformationOperator3D in 2x3
                               'Orientation',    # from IfcFaceOuterBound in 2x3
                               'SelfIntersect',  # from IfcCompositeCurve in 2x3
                               'SameSense',      # from IfcCompositeCurveSegment in IFC2x3
                               'SenseAgreement',  # from IfcTrimmedCurve in IFC2x3
                               'AgreementFlag',   # from IfcPolygonalBoundedHalfSpace
                               'ParameterTakesPrecedence',
                               'ClosedCurve',
                               'SelfIntersect',
                               'LayerOn',
                               'LayerFrozen',
                               'LayerBlocked',
                               'ProductDefinitional',
                               'Scale2',  # IfcCartesianTransformationOperator2DnonUniform
                               'Scale3',
                               'RelatedPriorities',
                               'RelatingPriorities',
                               'SameSense',
                               'AgreementFlag',
                               'USense',
                               'VSense',
                               'WeightsData',
                               'Weights',
                               'Sizeable',
                               'ParameterTakesPrecedence',
                               'IsCritical',
                               'DestabilizingLoad',
                               'IsLinear',
                               'RepeatS',
                               'RepeatT',
                               'IsHeading',
                               'IsMilestone',
                               'Priority',
                               'SenseAgreement',
                               'IsPotable',
                               'NumberOfRiser',
                               'NumberOfTreads',
                               'Pixel',
                               'InputPhase',
                               'Degree'
                               ]:
                node_attributes.append(attr.name())

            elif is_type or is_enumeration or is_pdt_select or is_nested_select:
                node_attributes.append(attr.name())
            elif is_entity or is_entity_select:
                single_associations.append(attr.name())
            elif is_aggregation:
                # ToDo: check if it is an aggregation of types or an aggregation of entities
                # https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/link/ifctrimmedcurve.htm -> trimSelect
                if attr.name() in [
                    'Coordinates',
                    'DirectionRatios',
                    'CoordList',
                    'segments',
                    'MiddleNames',
                    'PrefixTitles',
                    'SuffixTitles',
                    'Roles',
                    'Addresses',
                    'CoordIndex',
                    'InnerCoordIndices',
                    'Trim1',
                    'Trim2',
                    'Orientation',



                ]:
                    node_attributes.append(attr.name())
                else:
                    aggregated_associations.append(attr.name())
            else:
                raise Exception('Tried to encode the attribute type of entity #{} clsName: {} attribute {}. '
                                'Please check your graph translator.'.format(entity_id, clsName, attr.name()))

        return node_attributes, single_associations, aggregated_associations
