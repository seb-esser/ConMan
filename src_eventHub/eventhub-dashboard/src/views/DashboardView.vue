<template>
 <div id="dashboard">
   <div id="left"> <EventStream></EventStream></div>
   <div id="right"> <ConnectionOverview></ConnectionOverview></div>

  </div>
</template>

<script>
import EventStream from "@/components/EventStream";
import ConnectionOverview from "@/components/ConnectionOverview";

export default {
  name: "DashboardView",
  components: {
    ConnectionOverview,
    EventStream
  }
}
</script>

<style scoped>
/*styles the div container with the "dashboard" id*/
#dashboard {
  display: flex;
  margin: 2px

}

#left {
  flex: 0 0 50%;
  border-width:2px;
  border-style:solid;
  border-color:cadetblue;
  margin: 4px;
}

#right {
  flex: 1;
  border-width:2px;
  border-style:solid;
  border-color:cadetblue;
  margin: 4px;
}

</style>