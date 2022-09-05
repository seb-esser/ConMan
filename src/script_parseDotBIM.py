from dotbimpy import File

from neo4j_middleware import neo4jConnector


def main():
    connector = neo4jConnector.Neo4jConnector()
    connector.connect_driver()

    path = "00_sampleData/dotBIM/Fahrzeughalle/Fahrzeughalle.bim"
    file = File.read(path)
    # file.view()
    file_info = file.info
    file_version = file.schema_version
    file_identifier = ""

    cy = "MERGE (f:DotBimFile{{FileName: \"{}\" }})".format("Fahrzeughalle.bim")
    connector.run_cypher_statement(cy)

    print("processing meshes...")
    for mesh in file.meshes:
        cy = "MATCH (f:DotBimFile) " \
             "MERGE (m:DotBimMesh {{mesh_id: {0}, coordinates: {1}, indices: {2} }}) " \
             "MERGE (f)-[:mesh]->(m)".format(mesh.mesh_id, str(mesh.coordinates), str(mesh.indices))
        connector.run_cypher_statement(cy)

    print("processing elements ...")
    for element in file.elements:

        # node properties
        ty: str = element.type
        info: dict = element.info
        guid: str = element.guid

        # sub nodes
        color = element.color
        rotation = element.rotation
        vector = element.vector

        # build edge
        mesh_id = element.mesh_id

        cy = "MATCH (f:DotBimFile) " \
             "MERGE (e:DotBimElement{{guid: \"{0}\", info: \"{1}\", type: \"{2}\" }}) " \
             "MERGE (f)-[:element]->(e) " \
             "CREATE (c:DotBimColor{{r:{3}, g:{4}, b:{5}, a:{6}  }}) " \
             "MERGE (e)-[:color]->(c) " \
             "CREATE (r:DotBimRotation{{qx: {7}, qy: {8}, qz: {9}, qw: {10} }}) " \
             "MERGE (e)-[:rotation]->(r) " \
             "CREATE (v:DotBimVector{{x: {11}, y: {12}, z: {13} }}) " \
             "MERGE (e)-[:vector]->(v)".format(guid,
                       str(info),
                       ty,
                       color.r,
                       color.g,
                       color.b,
                       color.a,
                       rotation.qx,
                       rotation.qy,
                       rotation.qz,
                       rotation.qw,
                       vector.x,
                       vector.y,
                       vector.z)
        connector.run_cypher_statement(cy)

        # connect element with corresponding mesh
        cy = "MATCH (e:DotBimElement{{guid: \"{0}\" }})" \
             "MATCH (m:DotBimMesh{{mesh_id: {1} }})" \
             "MERGE (e)-[:REPRESENTATION]->(m)" \
             "".format(guid, mesh_id)
        connector.run_cypher_statement(cy)

    connector.disconnect_driver()


if __name__ == "__main__":
    main()
