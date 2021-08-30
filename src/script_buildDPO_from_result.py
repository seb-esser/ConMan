import jsonpickle

from neo4jGraphDiff.Result import Result

# with open('result_solibriExample.json') as f:
#     content = f.read()
#
# print("[INFO] loading result json....")
# result: Result = jsonpickle.decode(content)
# print("[INFO] DONE. ")

# ToDo: these lists should be included in the result object. Apparently, these changes are not yet captured.
from neo4j_middleware.neo4jConnector import Neo4jConnector

guids_removed = [
    "32xlMB3wy8fOpMzyHpakTe",
    "2SeQTQUdv7Su2MXgROLa2$",
    "3cAF6Z6l1AaAN$n1Dh1jf8"
]

guids_added = [
    "1VQM4R42pgD4M9fKP5xbei",
    "1xYoyrIGL3SwPhpyfPm_Nq",
    "0I_5eIRzL7QhiRmNZWVpkh",
    "1VaaDkOIb9kR_m_Kk3toPA",
    "2D5DFc$nD1Xub_Y4N75Yhn"
]
label_init = "ts20121017T152740"
label_updt = "ts20121017T154702"

connector = Neo4jConnector()
connector.connect_driver()

for guid in guids_removed:
    cy = """
    MATCH removeNodes = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[*..10]->(sec:SecondaryNode:{0})
    WHERE NOT (sec)-[:SIMILAR_TO]->()

    OPTIONAL MATCH inclinedPointers = (sec)<-[:rel]-(extRefs_in)-[:SIMILAR_TO]-(a)
    OPTIONAL MATCH outgoingPointers = (sec)-[:rel]->(extRefs_out)-[:SIMILAR_TO]-(b)

    OPTIONAL MATCH context_1 = (extRefs_in)-[:rel*..2]-(prim_a:PrimaryNode)
    OPTIONAL MATCH context_2 = (extRefs_out)-[:rel*..2]-(prim_b:PrimaryNode)
    return count([n, sec])""".format(label_init, guid)
    # print(cy + '\n --- --- \n')

    raw = connector.run_cypher_statement(cy)[0]
    print(raw)




