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
          <td>{{ item.user_id }} </td>
          <td>
            <v-btn small icon="mdi-pencil">edit</v-btn>
            <v-btn small icon="mdi-delete">remove</v-btn>
          </td>
        </tr>
        </tbody>
      </v-table>
      <v-btn>Add team member</v-btn>
    </v-card-text>

    <!--  <v-card-actions>-->
    <!--    <v-btn-group>-->
    <!--      <v-btn small icon="mdi-download">download file</v-btn>-->
    <!--      <v-btn small icon="mdi-download">download file</v-btn>-->
    <!--    </v-btn-group>-->
    <!--  </v-card-actions>-->
  </v-card>
</template>

<script>

export default {
  name: "DeliveryTeam",

  props: {
    TeamId: {type: Number, default: 0},
    TeamName: {type: String, default: ""},
    members: {type: Object}
  },
}
</script>

<style scoped>

</style>