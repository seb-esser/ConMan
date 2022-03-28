from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


def main():
    cypher1 = "(n1:nodeTypeA:label1 {attrName1: \"attrVal\", attrName2: 23})" \
              "-[e1:EdgeType{edgeAttr: 345}]->(n2:nodeTypeB {boolAttr: TRUE})"
    print(cypher1)
    pattern1 = GraphPattern.from_cypher_statement(cypher1)
    cy = pattern1.to_cypher_create()
    print(cy)
    cypher2 = "(n3:nodeTypeC {attrName3: \"attrVal\", attrName2: 23})<-[e2:EdgeType]-(n4:nodeTypeD)"
    pattern2 = GraphPattern.from_cypher_statement(cypher2)
    cypher3 = "(n4:asd{a:23})-[e1:EdgeType{a:\"b\"}]-(n5:nodeTypeE)<--(n6)-->(n7:nodeLabel:nodeLabel2{a: \"a\"})"
    pattern3 = GraphPattern.from_cypher_statement(cypher3)


if __name__ == "__main__":
    main()
