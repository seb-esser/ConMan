<template>
  <div>
  <h2>Event Stream</h2>
    <EventObject
        v-for="event in this.events"
        v-bind:key="event.eventId"
        :eventId=event.eventId
        :topic=event.topic
        :payload=event.payload
    >
    </EventObject>

  </div>

</template>

<script>

import EventObject from "@/components/EventObject";
// import io from "socket.io-client"

export default {
  name: "EventStream",
  components: {EventObject},
  props: {

  },
  created: function () {
    console.log("Hit onCreated method in Eventstream. ");
    // var con = io("http://localhost:5000");
    // con.on("newTransaction", data => {
    //   console.log(data);
    //   // this.msgBundles.push(data);
    //
    // });
  },

  data() {
    return {
      "events": [
        {"eventId": 1,
          "topic": "A/B/C",
          "payload": "someTransformationJSON"
        },
        {
          "eventId": 2,
          "topic": "A/B/C/D",
          "payload": "someTransformationJSON"
        }
      ]
    }
  },



}

</script>

<style scoped>

</style>
