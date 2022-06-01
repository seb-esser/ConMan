<template>
  <div>
    <h2>Tracked Models</h2>

<!--    <v-banner-->
<!--        single-line-->
<!--        :sticky="sticky"-->
<!--        :rounded="true"-->
<!--    >-->

<!--      <template v-slot:actions>-->
<!--        <v-btn block color="primary" @click="getModelsFromBackend">-->
<!--          Reload-->
<!--        </v-btn>-->
<!--      </template>-->
<!--    </v-banner>-->
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

            <v-list density="compact">
              <v-list-subheader>Available timestamps</v-list-subheader>
              <v-list-item
                  v-for="(item, j) in i.timestamps"
                  :key="j"
                  :value="item"
                  active-color="primary"
              >
                <v-list-item-title v-text="item"></v-list-item-title>

                <v-btn small icon="mdiCloudDownloadOutline">download file</v-btn>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>
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

  created (){
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