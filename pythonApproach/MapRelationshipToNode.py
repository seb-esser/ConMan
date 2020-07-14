

def map_relationship_to_node(rel, database):
    # fetch all var names and assign attributes
    info = rel.get_info()
    class_name = info['type']
    instance_id = info['id']
    print("\tClass:\t" + class_name)
    print("\tEntityId:\t" + str(instance_id))

    # test if relationship connects two routed entities
    if hasattr(rel, 'RelatingObject') and hasattr(rel, 'RelatedObjects'):
        relatedElement = rel[4]
        relatingElements = rel[5]
        print('-> Related Object:')
        print(relatedElement)
        print('-> Relating Objects:')
        print(relatingElements)

        for i in range(0, len(relatingElements)-1):
            elemId = relatingElements[i].get_info()['id']

            cypher = ""
            cypher = cypher + 'MATCH(n) WHERE n.EntityId = "{}" \n'.format(relatedElement.get_info()['id'])
            cypher = cypher + 'MATCH(m) WHERE m.EntityId = "{}" \n'.format(elemId)
            cypher = cypher + 'merge (n) -[rel:IfcRelationship]->(m)'.format(class_name)

            database.run_cypher_statement(cypher)



