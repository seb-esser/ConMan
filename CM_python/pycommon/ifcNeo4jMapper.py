
class IfcNeo4jMapper:
    
    def __init__(self):
        print('Initialized mapper. ')
        pass


    def mapEntities(self, connector, entities):
        # STEP 1: create all routed entities and add their guids
        for entity in entities:
            print('Creating entity with guid {} in graph...'.format(entity['globalId']))
            # formulate cypher command
            cypher_statement = 'CREATE(n:' + entity['type'] + '{' + 'globalId:"{}'.format(entity['globalId']) + '"}' + ')'
            # run command on database
            connector.run_cypher_statement(cypher_statement)

        return True

    def mapAttributes(self, attributes):

        # cases to be considered:
        switch = {
            "atomicAttr": "mapAtomic",
            "dictAttr": "mapNestedAttrs",
            "globalId": "mapIdAsRelationship"
            }

        ## recursive function that maps all unrooted attributes of a given entity
        for attr, val in attributes:
            if isinstance(val, dict) or isinstance(val, list):
            # dealing with lists and arrays
                prop_val = hash(str(val))
                prop_cyper[attr] = prop_val
                # ToDo: implement recursive parsing
                # else if attr = ofType('globalId'):
                    ## dealing with a atomic property
                    #prop_val = val
                    #prop_cyper[attr] = prop_val
            
            # print('\t{:<25}: {}'.format(attr, prop_val))
             
            # prps = format_json(prop_cyper)


              #cypher_statement = ''
              #cypher_statement = 'Match(n) where n.globalId="{}" set n.{} = {} return n'.format(entity['globalId'], attrName, attrV

