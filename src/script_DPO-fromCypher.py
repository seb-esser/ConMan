from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


def main():
    cypher1 = "(n1:nodeTypeA:label1 {attrName1: \"attrVal\", attrName2: 23})-[e1:EdgeType]->(n2:nodeTypeB {boolAttr: TRUE})"
    cypher2 = "(n3:nodeTypeC {attrName3: \"attrVal\", attrName2: 23})<-[e2:EdgeType]-(n4:nodeTypeD)"
    pattern1 = GraphPattern.from_cypher_statement(cypher1)
    pattern2 = GraphPattern.from_cypher_statement(cypher2)


if __name__ == "__main__":
    main()
