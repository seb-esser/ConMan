<template>
  <div class="p-0">

    {{ eventId }} - {{ topic }} - {{ payload }}
    <div>
      <b-button-toolbar key-nav aria-label="Toolbar with button groups">

        <b-button-group class="mx-1">
          <b-button>Edit</b-button>
          <b-button>Undo</b-button>
          <b-button>Redo</b-button>
        </b-button-group>

      </b-button-toolbar>
    </div>

  </div>

</template>

<script>

export default {
  name: "EventObject",
  props: {
    eventId: {type: Number, default: 0},
    topic: {type: String, default: ""},
    payload: {type: String, default: ""}
  },
  data() {
    return {}
  }
}
</script>

<style scoped>

</style>
