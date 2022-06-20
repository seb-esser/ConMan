<template>
  <v-card variant="outlined">
    <v-card-title>{{ TeamName }}</v-card-title>
    <v-card-text>
      <v-table>
        <thead>
        <tr>
          <th class="text-left">
            First Name
          </th>
          <th class="text-left">
            Last Name
          </th>
          <th class="text-left">
            UserID
          </th>
          <th class="text-left">
            Actions
          </th>
        </tr>
        </thead>

        <tbody>
        <tr
            v-for="item in members"
            :key="item.user_id"
        >
          <td>{{ item.first_name }}</td>
          <td>{{ item.last_name }}</td>
          <td>{{ item.user_id }}</td>
          <td>
            <v-btn small icon="mdi-pencil">edit</v-btn>
            <v-btn small icon="mdi-delete">remove</v-btn>
          </td>
        </tr>
        </tbody>
      </v-table>

        <v-dialog
            v-model="dialog"
        >
          <template v-slot:activator="{ props }">
            <v-btn

                v-bind="props"
                color="secondary"
            >
              Add team member
            </v-btn>
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
                    ></v-text-field>
                  </v-row>

                  <v-row>
                    <v-text-field
                        v-model="lastName"
                        label="Last name*"
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

export default {
  name: "DeliveryTeam",

  props: {
    TeamId: {type: Number, default: 0},
    TeamName: {type: String, default: ""},
    members: {type: Object}
  },
  data: () => ({
    dialog: false,
    lastName: null,
    firstName: null
  }),

  methods: {
    async submitNewMember() {
      var data = {"FirstName": this.firstName, "LastName": this.lastName, "TeamId": this.$props.TeamId }
      var res = await axios.post("http://localhost:5000/api/createMember", data)
      console.log(res)
      var newMember = eval(res.data)
      this.$props.members.push(newMember)
      this.dialog = false
    }

    // async removeMember() {
    //   var memberId = this.$props.members.
    //   var res = await axios.delete("http://localhost:5000/api/deleteMember", memberId)
    // }
  }
}
</script>

<style scoped>

</style>