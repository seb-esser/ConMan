<template>
  <div id="line">

    <v-container>
      <v-form>
        <v-row>
          <v-col justify='left'>
            {{ eventId }}
          </v-col>
          <v-col justify='left'>
            {{ topic }}
          </v-col>
          <v-col justify='left'>
            {{ payload }}
          </v-col>
          <v-col justify='right'>
            <v-btn x-small
                   color="normal"
                   >view
            </v-btn>
            <v-btn x-small
                   color="normal"
                   >more
            </v-btn>

          </v-col>
        </v-row>
      </v-form>
    </v-container>


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
#line {
  min-height: auto;
  margin: 4px;
  background-color: lightgrey
}

</style>
