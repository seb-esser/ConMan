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
  </div>

  <div id="dashboard">
    <div id="bottom">
      <div id="left">
        <TrackedModels></TrackedModels>
      </div>
    </div>
  </div>
</template>

<script>
import EventStream from "@/components/EventStream";
import ConnectionOverview from "@/components/ConnectionOverview";
import TrackedModels from "@/components/TrackedModels";

export default {
  name: "DashboardView",
  components: {
    ConnectionOverview,
    EventStream,
    TrackedModels
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