<template>
  <v-card variant="outlined">
    <v-card-title>{{ TeamName }}</v-card-title>
    <v-card-subtitle> TeamID: {{ TeamUUID }}</v-card-subtitle>
    <v-card-text>

      <MemberView
          v-for="(member, index) in this.$props.members"
          :key="member.user_id"
          :lastName="member.last_name"
          :firstName="member.first_name"
          :uuid="member.user_id"
          v-on:deleteThisMember="deleteMember(index)">
      </MemberView>

      <v-dialog
          v-model="dialog"
      >
        <template v-slot:activator="{ props }">
          <v-btn-group>
            <v-btn

                v-bind="props"
                color="secondary"
            >
              Add team member
            </v-btn>
            <v-btn
                color="secondary"
                @click="removeTeam"
            >
              Delete Team
            </v-btn>
          </v-btn-group>
        </template>

        <v-card>
          <v-card-title>
            <span class="text-h5">Add Team Member</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-col>
                <v-row>
                  <v-text-field
                      v-model="firstName"
                      label="First name*"
                      required
                      autofocus="true"
                  ></v-text-field>
                </v-row>

                <v-row>
                  <v-text-field
                      v-model="lastName"
                      label="Last name*"
                      @keydown.enter="submitNewMember"
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
                @click="submitNewMember"
            >
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

    </v-card-text>

  </v-card>

</template>

<script>

import axios from "axios";
import MemberView from "@/components/MemberView";

export default {
  name: "DeliveryTeam",
  components: {MemberView},


  props: {
    TeamId: {type: Number, default: 0},
    TeamUUID: {type: String, default: ""},
    TeamName: {type: String, default: ""},
    members: {type: Object}
  },
  data: () => ({
    dialog: false,
  }),

  methods: {
    async submitNewMember() {
      var data = {"FirstName": this.firstName, "LastName": this.lastName, "TeamId": this.$props.TeamId}
      var res = await axios.post("http://localhost:5000/api/createMember", data)
      var newMember = eval(res.data)
      this.$props.members.push(newMember)
      this.dialog = false
    },

    deleteMember: function (index) {
      this.$props.members.splice(index, 1);
    },

    async removeTeam() {
      // delete all members of the team

      // delete team
      const teamId = this.$props.TeamUUID;
      await axios.delete("http://localhost:5000/api/deleteDeliveryTeam", {data: {"uuid": teamId}})
      // escalate the deletion to the parent component
      this.$emit('deleteThisTeam')
    }

  }
}
</script>

<style scoped>

</style>