<template>
  <div id="dashboard">
    <div id="left">
      <div>
        <h2>Delivery Teams</h2>
        <DeliveryTeam v-for="team in this.deliveryTeams"
                      :key="team.id"
                      :TeamId=team.id
                      :TeamName=team.name
                      :members=team.members
        />

        <v-btn >Add Delivery Team</v-btn>
      </div>
    </div>

    <div id="right">
      <h2>Subscriptions and Topic hierarchy</h2>

      <v-treeview
          v-model="selection"
          :items="topics"
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
      deliveryTeams: []
    }

  },
  created() {
    this.getDeliveryTeams()
  },


  methods: {

    async getDeliveryTeams() {
      var res = await axios.get("http://localhost:5000/api/getDeliveryTeams")
      this.deliveryTeams = res.data
    }
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