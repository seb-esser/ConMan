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

<script lang="js">
import {useNeo4jQuery} from "@/functions/neo4jhandler/neo4jconnector";

export default {
  name: "TrackedModels",
  methods: {

    async getModelsFromNeo4j() {
      var res = await useNeo4jQuery('MATCH (n:PrimaryNode{EntityType: "IfcProject"}) RETURN n.Name, LABELS(n)')
      console.log(res)

    }

  }
}
</script>

<style scoped>

</style>