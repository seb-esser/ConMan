// by convention, composable function names start with "use"
export async function useNeo4jQuery(cypherStatement) {

    const neo4j = require('neo4j-driver')
    const uri = "bolt://localhost:7687";
    const user = "neo4j";
    const password = "password"

    const driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {encrypted: "ENCRYPTION_OFF"})
    const session = driver.session()

    var result = [];
    try {
        const raw = await session.run(cypherStatement)

        for (let i in raw.records) {
            console.log("name" + raw.records[i]._fields[0] + " labels:" + raw.records[i]._fields[1])
        }

        result = raw.records

    } finally {
        await session.close()
    }

    // on application exit:
    await driver.close()

    return result
}