from pprint import pprint

from neo4j_middleware.neo4jConnector import Neo4jConnector
import pandas

def align_by_guid(connector):
    ts_1 = ""
    ts_2 = ""

    # align based on GUIDs
    cy = """
        MATCH (n:PrimaryNode:{}) 
        MATCH (m:PrimaryNode:{}) WHERE m.GlobalId = n.GlobalId
        MERGE (n)-[:ALIGNED{AlignmentType: ''ByGuid''}]-(m) 
        """.format(ts_1, ts_2)
    connector.run_cypher_statement(cy)


def align_by_ito_result(connector, ts_1, ts_2):

    # load data
    df = pandas.read_excel("00_sampleData/updateAlignment-Data/AdjacentToRoom.xlsx")
    column_headers = df.columns.values
    print(column_headers)

    guid_pairs = df.loc[:, ['SourceGUID', 'TargetGUID']]
    for index, row in guid_pairs.iterrows():
        cy = ("MATCH (a:{0} {{ GlobalId: \"{1}\" }}), (b:{2} {{ GlobalId: \"{3}\" }}) "
              "RETURN a, b").format(ts_1, row["SourceGUID"], ts_2,  row["TargetGUID"])
        print(cy)

def align_by_spatial_structure(connector):
    pass


def main():
    connector = Neo4jConnector()
    connector.connect_driver()

    # by solibri
    align_by_ito_result(connector,"ts20230831T094926", "ts20230831T094633")

    connector.disconnect_driver()


if __name__ == "__main__":
    main()
