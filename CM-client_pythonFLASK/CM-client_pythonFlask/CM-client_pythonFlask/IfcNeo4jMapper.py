
class IfcNeo4jMapper:
    
    def __init__(self):
        pass


    def mapEntities(entities):
        # STEP 1: create all routed entities and add their guids
        for entity in entities:
            cypher_statement = str.join('CREATE(n:', entity['type'] , "{" + 'globalId: {}'.format(entity['globalId'])  , "}" , ')')
            print(cypher_statement)
            connector.run_cypher_statement(cypher_statement)
            
            print('\n')
        return True

    def mapAttributes(attributes):
        ## recursive function that maps all unrooted attributes of a given entity

        return True
