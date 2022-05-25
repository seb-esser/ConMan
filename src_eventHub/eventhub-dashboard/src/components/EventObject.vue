<template>
  <div id="line">
    <v-card
        elevation="2"
        hover=true
        v-on:click="greet"

    >
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

    </v-card>
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
  },
  methods: {
    greet() {
      // `this` inside methods points to the current active instance
      alert(`Hello ${this.name}!`)

    }
  }
}
</script>

<style scoped>
#line {
  min-height: auto;
  margin: 4px;
}

</style>
