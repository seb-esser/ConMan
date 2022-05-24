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
        <v-btn block color="primary">
          Get Online
        </v-btn>
      </template>
    </v-banner>
  </div>
</template>

<script>
export default {
  name: "TrackedModels"
}
</script>

<style scoped>

</style>