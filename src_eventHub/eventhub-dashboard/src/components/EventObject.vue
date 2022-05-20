<template>
  <div class="p-0">
    <p>
     {{eventId}} - {{topic}} - {{payload}}
    </p>
  </div>

</template>

<script>
export default {
  name: "EventObject",
  props: {
    eventId: {type: Number, default: 0},
    topic: {type: String, default: ""},
    payload: {type: String, default: ""}},
  data() {return {} }
}
</script>

<style scoped>

</style>
