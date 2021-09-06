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
        self.timestamp = my_label

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
            self.timestamp))
        self.connector.run_cypher_statement(
            'MATCH(n:{}) DETACH DELETE n'.format(self.timestamp))

        print('[IFC_P21 > {} < ]: Generating graph... '.format(self.timestamp))

        # extract model data

        entity_list = []

        for element in self.model:
            entity_list.append(element)

        increment = 100 / (len(entity_list)*2)
        percent = 0
        
        for entity in entity_list:
                
            # print progressbar
            progressbar.printbar(percent)
                
            # check if the entity is either an ObjectDef or Relationship or neither
            if entity.is_a('IfcObjectDefinition'):
                self.__mapEntity(entity, "PrimaryNode")
            elif entity.is_a('IfcRelationship'):
                self.__mapEntity(entity, "ConnectionNode")
            else:
                self.__mapEntity(entity, "SecondaryNode")

            # add increment to percentage
            percent += increment
            
        for entity in entity_list:
            # print progressbar
            progressbar.printbar(percent)
            
            self.build_node_rels(entity)
            
            # add increment to percentage
            percent += increment

        print('[IFC_P21 > {} < ]: Generating graph - DONE. \n '.format(self.timestamp))

        return self.timestamp

        
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

    def __mapEntity(self, entity, label):
        # get some basic data
        info = entity.get_info()
        
        # node_attribute_names, single_associations, aggregated_associations = self.separate_attributes(entity)
        node_attribute_names, single_associations, aggregated_associations = self.separate_attributes(entity)
        
        # create a dictionary of attributes
        node_attr_dict = {}
        for a in node_attribute_names:
            node_attr_dict[a] = info[a]
        
        # rename some keys
        node_attr_dict['p21_id'] = node_attr_dict.pop('id')
        node_attr_dict['EntityType'] = node_attr_dict.pop('type')
        
        # run cypher command
        cypher_statement = Neo4jGraphFactory.create_node_with_attr(label, node_attr_dict, self.timestamp)
        # parent_node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')[0]
        self.connector.run_cypher_statement(cypher_statement)

    def build_node_rels(self, entity):
        # get info
        info = entity.get_info()
        p21_id = info['id']
        
        # get attribute definitions
        _, single_associations, aggregated_associations = self.separate_attributes(entity)
        
        for association in single_associations:
            entity = info[association]
            if entity is None:
                continue

            p21_id_child = entity.get_info()['id']

            edge_attrs = {'relType': association}

            # merge with existing
            cy = Neo4jGraphFactory.merge_on_p21(p21_id, p21_id_child, edge_attrs, self.timestamp)
            self.connector.run_cypher_statement(cy)
        
        for association in aggregated_associations:
            entities = info[association]
            i = 0
            if entities is None:
                # detected an array of associations but nothing was referenced within the given instance model
                continue
            for entity in entities:
                try:
                    p21_id_child = entity.get_info()['id']
                
                except:
                    raise Exception('Failed to query data from entity.')

                edge_attrs = {
                    'relType': association,
                    'listItem': i
                }

                # merge with existing
                cy = Neo4jGraphFactory.merge_on_p21(p21_id, p21_id_child, edge_attrs, self.timestamp)
                self.connector.run_cypher_statement(cy)

                # increase counter
                i += 1
    
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
        # info.pop('id')
        # info.pop('type')

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
                    'RefLongitude',
                    'RefLatitude'
                ]:
                    node_attributes.append(attr.name())
                else:
                    aggregated_associations.append(attr.name())
            else:
                raise Exception('Tried to encode the attribute type of entity #{} clsName: {} attribute {}. '
                                'Please check your graph translator.'.format(entity_id, clsName, attr.name()))
        node_attributes.append('id')
        node_attributes.append('type')
        return node_attributes, single_associations, aggregated_associations
