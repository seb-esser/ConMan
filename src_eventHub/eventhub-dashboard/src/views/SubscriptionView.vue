<template>
  <div id="dashboard">
    <div id="left">
      <div>
        <h2>Delivery Teams</h2>
        <DeliveryTeam v-for="(team, index) in this.deliveryTeams"
                      :key="team.id"
                      :TeamId=team.id
                      :TeamUUID=team.uuid
                      :TeamName=team.name
                      :members=team.members
                      v-on:deleteThisTeam="deleteTeam(index)"
        />

        <v-dialog
            v-model="dialog"
        >
          <template v-slot:activator="{ props }">
            <v-btn
                v-bind="props"
                color="primary"
            >
              Add Delivery Team
            </v-btn>

          </template>

          <v-card>
            <v-card-title>
              <span class="text-h5">Add Team</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-col>
                  <v-row>
                    <v-text-field
                        v-model="teamName"
                        label="Team Name*"
                        required
                        @keyup.enter="submitNewTeam"
                    ></v-text-field>
                  </v-row>
                </v-col>
              </v-container>
              <small>*indicates required field</small>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                  color="blue-darken-1"
                  text
                  @click="dialog = false"
              >
                Close
              </v-btn>
              <v-btn
                  color="blue-darken-1"
                  text
                  @click="submitNewTeam"
              >
                Save
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </div>

    <div id="right">
      <h2>Subscriptions and Topic hierarchy</h2>

      <v-treeview
          :items="treeItems"
          selectable
          open-all
      >
      </v-treeview>
    </div>
  </div>
</template>


<script>


import axios from "axios";
import DeliveryTeam from "@/components/DeliveryTeam";

export default {
  name: "SubscriptionView",
  components: {DeliveryTeam},


  data() {
    return {
      deliveryTeams: [],
      treeItems: [
        {
          id: 1,
          name: 'Applications :',
          children: [
            {id: 2, name: 'Calendar : app'},
            {id: 3, name: 'Chrome : app'},
            {id: 4, name: 'Webstorm : app'},
          ],
        },
        {
          id: 5,
          name: 'Documents :',
          children: [
            {
              id: 6,
              name: 'vuetify :',
              children: [
                {
                  id: 7,
                  name: 'src :',
                  children: [
                    {id: 8, name: 'index : ts'},
                    {id: 9, name: 'bootstrap : ts'},
                  ],
                },
              ],
            },
            {
              id: 10,
              name: 'material2 :',
              children: [
                {
                  id: 11,
                  name: 'src :',
                  children: [
                    {id: 12, name: 'v-btn : ts'},
                    {id: 13, name: 'v-card : ts'},
                    {id: 14, name: 'v-window : ts'},
                  ],
                },
              ],
            },
          ],
        },
        {
          id: 15,
          name: 'Downloads :',
          children: [
            {id: 16, name: 'October : pdf'},
            {id: 17, name: 'November : pdf'},
            {id: 18, name: 'Tutorial : html'},
          ],
        },
        {
          id: 19,
          name: 'Videos :',
          children: [
            {
              id: 20,
              name: 'Tutorials :',
              children: [
                {id: 21, name: 'Basic layouts : mp4'},
                {id: 22, name: 'Advanced techniques : mp4'},
                {id: 23, name: 'All about app : dir'},
              ],
            },
            {id: 24, name: 'Intro : mov'},
            {id: 25, name: 'Conference introduction : avi'},
          ],
        },
      ],
      dialog: false,
    }

  },
  created() {
    this.getDeliveryTeams()
  },


  methods: {

    async getDeliveryTeams() {
      var res = await axios.get("http://localhost:5000/api/getDeliveryTeams")
      this.deliveryTeams = res.data
    },

    async submitNewTeam() {
      var data = {"teamName": this.teamName}
      var res = await axios.post("http://localhost:5000/api/CreateDeliveryTeam", data)
      var newTeam = eval(res.data)
      this.deliveryTeams.push(newTeam)
      this.dialog = false
      this.teamName = ""
    },

    deleteTeam: function (team_index) {
      this.deliveryTeams.splice(team_index, 1);
    },
  }
}
</script>

<style scoped>
/*styles the div container with the "dashboard" id*/
#dashboard {
  display: flex;
  margin: 2px;
  min-height: 400px;;
}

#left {
  flex: 0 0 50%;
  margin: 4px;
  min-height: 400px;

}

#right {
  flex: 1;
  margin: 4px;
}
</style>