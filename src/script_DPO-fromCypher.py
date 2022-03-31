from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


def main():
    # cypher1 = "(n1:nodeTypeA:label1 {attrName1: \"attrVal\", attrName2: 23, intVal: 1, doubleVal: -1.34})" \
    #           "-[e1:EdgeType{edgeAttr: 345}]->(n2:nodeTypeB {boolAttr: TRUE, bl: false})"
    # print('In: {}'.format(cypher1))
    # pattern1 = GraphPattern.from_cypher_statement(cypher1)
    # cy = pattern1.to_cypher_merge()
    # print('Out: {}\n'.format(cy))
    #
    # cypher2 = "(n3:nodeTypeC {attrName3: \"attrVal\", attrName2: 23})<-[e2:EdgeType]-(n4:nodeTypeD)"
    # print('In: {}'.format(cypher2))
    # pattern2 = GraphPattern.from_cypher_statement(cypher2)
    # cy = pattern2.to_cypher_merge()
    # print('Out: {}\n'.format(cy))
    #
    # cypher3 = "(n4:asd{a:23})-[e1:EdgeType{a:\"b\"}]-(n5:nodeTypeE)<-[:r]-" \
    #           "(n6:ty)-[:r]->(n7:nodeLabel:nodeLabel2{a: \"a\"})"
    # print('In: {}'.format(cypher3))
    #
    # pattern3 = GraphPattern.from_cypher_statement(cypher3)
    # cy = pattern3.to_cypher_merge()
    # print('Out: {}\n'.format(cy))

    cypher4 = "(n1:Room)-[:r]->(w1:wall{Name:\"Wall1\"}) \n" \
              "(w3:wall{Name:\"Wall3\"})<-[b:r]-(n1)-[a:r]->(w2:wall{Name:\"Wall2\"})-[:e]->(win:window)"
    print('In: {}'.format(cypher4))

    pattern4 = GraphPattern.from_cypher_statement(cypher4)
    cy = pattern4.to_cypher_merge()
    print('Out merge-statement: {}'.format(cy))
    cy = pattern4.to_cypher_match()
    print('Out match-statement: \n{}'.format(cy))


if __name__ == "__main__":
    main()
