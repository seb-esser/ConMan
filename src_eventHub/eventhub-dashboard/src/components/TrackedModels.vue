<template>
  <div>
    <h2>Tracked Models</h2>
    <v-banner
        single-line
        :sticky="sticky"
        :rounded="true"
    >
      We are not yet connected to our neo4j database.

      <template v-slot:actions>
        <v-btn block color="primary" @click="getModelsFromNeo4j">
          Get Online
        </v-btn>
      </template>
    </v-banner>
  </div>
</template>

<script>
export default {
  name: "TrackedModels",
  methods: {

    async getModelsFromNeo4j() {
      const neo4j = require('neo4j-driver')
      const uri = "bolt://localhost:7474";
      const user = "neo4j";
      const password = "password"

      const driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {encrypted: "ENCRYPTION_OFF"})
      const session = driver.session()

      var result = [];
      try {
        const raw = await session.run('MATCH (n:PrimaryNode{EntityType: "IfcProject" RETURN n.Name')
        console.log(raw.records)
        result = raw.records

      } finally {
        await session.close()
      }

      // on application exit:
      await driver.close()

      return result

    }

  }
}
</script>

<style scoped>

</style>