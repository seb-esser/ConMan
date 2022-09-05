<template>
  <div id="dashboard">
    <div id="left">
      <ActorOverview></ActorOverview>
    </div>

    <div id="right">
      <TopicHierarchy></TopicHierarchy>
    </div>
  </div>
</template>


<script>

import TopicHierarchy from "@/components/TopicHierarchy";
import ActorOverview from "@/components/ActorOverview";

export default {
  name: "SubscriptionView",
  components: {ActorOverview, TopicHierarchy,},


  data() {
    return {
      dialog: false,
    }

  },

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