<template>
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
</template>

<script>
import DeliveryTeam from "@/components/DeliveryTeam";
import axios from "axios";

export default {
  name: "ActorOverview",
  components: {DeliveryTeam},

  data() {
    return {
      deliveryTeams: [],
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

</style>