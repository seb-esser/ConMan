<template>
  <div id="dashboard">
    <div id="top">
      <div id="left">
        <EventStream></EventStream>
      </div>
      <div id="right">
        <ConnectionOverview></ConnectionOverview>
      </div>
    </div>
    <div id="bottom">
    </div>
    <div>
      <TrackedModels></TrackedModels>
    </div>
  </div>
</template>

<script>
import EventStream from "@/components/EventStream";
import ConnectionOverview from "@/components/ConnectionOverview";
import trackedModels from "@/components/TrackedModels";

export default {
  name: "DashboardView",
  components: {
    ConnectionOverview,
    EventStream, trackedModels
  }
}
</script>

<style scoped>
/*styles the div container with the "dashboard" id*/
#dashboard {
  display: flex;
  margin: 2px
}

#top {
display: flex;
  margin: 2px;
   flex: 0 0 100%;
}

#bottom {
display: flex;
  margin: 2px;
   flex: 0 0 100%;
}

#left {
  flex: 0 0 50%;
  border-width: 2px;
  border-style: solid;
  border-color: cadetblue;
  margin: 4px;
}

#right {
  flex: 1;
  border-width: 2px;
  border-style: solid;
  border-color: cadetblue;
  margin: 4px;
}

</style>