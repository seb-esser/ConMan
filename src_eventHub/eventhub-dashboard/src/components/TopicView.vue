<template>
  <div>
    <v-card
        v-for="c in content"
        :key="c.id"
        :text="c.name">

    </v-card>
  </div>
</template>

<script>
export default {
  name: "TopicView",
  data() {
    return {
      content: []
    }
  }
}
</script>

<style scoped>

</style>