<template>
  <div id="line"
  >
    <v-card
        elevation="2"
        hover="true">
      <v-container>
        <v-form>
          <v-row>
            <v-col justify='left'>
              {{ lastName }}
            </v-col>
            <v-col justify='left'>
              {{ firstName }}
            </v-col>
            <v-col justify='left'>
              {{ uuid }}
            </v-col>
            <v-col justify='right'>
              <v-btn x-small
                     color="normal"
              >edit
              </v-btn>
              <v-btn x-small
                     color="normal"
                     @click="removeMember"

              >remove
              </v-btn>

            </v-col>
          </v-row>
        </v-form>
      </v-container>

    </v-card>

  </div>
</template>

<script>

import axios from "axios";

export default {
  name: "MemberView",

  props: {
    lastName: {type: String, default: ""},
    firstName: {type: String, default: ""},
    uuid: {type: String, default: ""}
  },
  methods: {
    async removeMember() {
      const memberId = this.$props.uuid;
      await axios.delete("http://localhost:5000/api/deleteMember", {data: {"uuid": memberId}})
      // escalate the deletion to the parent component
      this.$emit('deleteThisMember')
    }
  }

}
</script>

<style scoped>

</style>