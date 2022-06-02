<template>
  <div>
    <h2>Tracked Models</h2>
    <template v-if="!models.length">
      <v-banner
          single-line
          :sticky="sticky"
          :rounded="true"
      >
        Trying to get model data from backend ...
        <v-progress-circular
            indeterminate
            color="primary"
        ></v-progress-circular>
        <v-row class="justify-end">
          <v-btn icon="mdi-reload" color="primary" @click="getModelsFromBackend">
          </v-btn>
        </v-row>
      </v-banner>
    </template>

    <template v-else>
      <div>
        <v-expansion-panels>
          <v-expansion-panel
              v-for="i in models"
              :key="i.Name"

          >
            <v-expansion-panel-title>
              {{ i.Name }}
            </v-expansion-panel-title>
            <v-expansion-panel-text>

              <v-list>
                <v-list-subheader>Available timestamps</v-list-subheader>
                <v-list-item
                    v-for="(item, j) in i.timestamps"
                    :key="j"
                    :value="item"
                >
                  <v-list-item-title v-text="item"></v-list-item-title>
                  <v-row class="justify-end">
                    <v-btn small icon="mdi-download">download file</v-btn>
                  </v-row>
                </v-list-item>

              </v-list>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </template>
  </div>

</template>

<script lang="js">

import axios from 'axios';

export default {
  name: "TrackedModels",

  data() {
    return {
      models: []
    }
  },

  created() {
    this.getModelsFromBackend()

  },

  methods: {

    async getModelsFromBackend() {
      var res = await axios.get("http://localhost:5000/api/getModels")
      console.log(res.data["models"])
      this.models = res.data["models"]
    }

  }
}
</script>

<style scoped>

</style>