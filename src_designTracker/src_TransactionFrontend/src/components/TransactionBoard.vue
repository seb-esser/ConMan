<template>
  <div id="transactionBoard">
    <h3>TransactionBoard</h3>

   <EventContainer
       v-for="event in msgBundles"
       v-bind:key="event.id"
       :bundle="event"
   ></EventContainer>
  </div>
</template>

<script>



import EventContainer from "@/components/EventContainer";

import io from "socket.io-client"

export default {
  name: 'Transactions',

  components: {
    EventContainer
  },

  data() {
    return {
      msgBundles: []
    }
  },

  created: function () {
    console.log("Hit onCreated method in App.vue. ");
    var con = io("http://localhost:5000");
    con.on("newTransaction", data => {
      console.log(data);
      this.msgBundles.push(data);

    });


  }


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
