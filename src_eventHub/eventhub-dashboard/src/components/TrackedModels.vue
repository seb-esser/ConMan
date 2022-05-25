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
  data() {
    return {
      models: []
    }
  },

  created() {
    this.models = []
  },

  methods: {

    async getModelsFromNeo4j() {
      let res = await useNeo4jQuery('MATCH (n:PrimaryNode{EntityType: "IfcProject"}) RETURN n.Name, LABELS(n)');

      for (let i in res.records) {
        var modelName = res.records[i]._fields[0]
        var labels = res.records[i]._fields[1]

        var PATTERN = 'ts'
        var timestamp = labels.filter(function (str) {
          return str.includes(PATTERN);
        });

        const model = {"name": modelName, "timestamp": timestamp[0]};

        var index = this.models.findIndex(x => x.name === modelName && x.timestamp === timestamp[0]);
        index === -1 ? this.models.push(model) : console.log("This item already exists");

      }
      console.log("Loaded version-controlled models: DONE. ")
    }

  }
}
</script>

<style scoped>

</style>