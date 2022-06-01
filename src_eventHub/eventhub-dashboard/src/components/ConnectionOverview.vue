<template>
  <div id="connectedUsers">
    <h2>Connected users</h2>
    {{ connectedUsers }}
  </div>
</template>

<script>
import {io} from "socket.io-client";

export default {
  name: "ConnectionOverview",

  data() {
    return {
      connectedUsers: []
    }
  },

  created: function () {
    console.log("Hit onCreated method in App.vue. ");
    var con = io("http://localhost:5000");
    con.on("UserConnected", data => {
          console.log(data);
          this.connectedUsers.push(data);

        }
    );
  },
}
</script>

<style scoped>

</style>