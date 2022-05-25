<template>
  <div id="dashboard">
  <div id="left">
    <v-card elevation="5" min-height="400"
        >
      <EventStream></EventStream>
    </v-card>
  </div>
  <div id="right">
    <v-card elevation="5" min-height="400">
      <ConnectionOverview></ConnectionOverview>
    </v-card>
  </div>
</div>

  <div id="dashboard">
    <div id="bottom">
      <div id="left">
            <v-card elevation="5" min-height="400"
        >
        <TrackedModels></TrackedModels>
              </v-card>
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
  margin: 4px;
  min-height: 400px;

}

#right {
  flex: 1;
  margin: 4px;
}

</style>