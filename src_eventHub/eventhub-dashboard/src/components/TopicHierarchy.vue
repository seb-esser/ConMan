<template>
  <div>
    <div class="text-center d-flex pb-4">
      <v-btn class="ma-2" @click="all">
        All
      </v-btn>
      <v-btn class="ma-2" @click="none">
        None
      </v-btn>
    </div>

    <v-expansion-panels
        variant="accordion"
        class="my-4"
        v-model="panel"
        multiple>

      <v-expansion-panel
          v-for="(topic) in this.topics"
          :key="topic.uuid"
          :title="topic.topicName"
          :value="topic.uuid"
          :text="topic.content"
      >
<!--        <v-expansion-panel-title>-->
<!--          <template v-slot:default="{ expanded }">-->
<!--            <v-row no-gutters="true">-->
<!--              <v-col cols="4" class="d-flex justify-start">-->
<!--                Trip name-->
<!--              </v-col>-->
<!--              <v-col-->
<!--                  cols="8"-->
<!--                  class="text-grey"-->
<!--              >-->
<!--                <v-fade-transition leave-absolute>-->
<!--                <span-->
<!--                    v-if="expanded"-->
<!--                    key="0"-->
<!--                >-->
<!--                  Enter a name for the trip-->
<!--                </span>-->
<!--                  <span-->
<!--                      v-else-->
<!--                      key="1"-->
<!--                  >-->
<!--                 Name-->
<!--                </span>-->
<!--                </v-fade-transition>-->
<!--              </v-col>-->
<!--            </v-row>-->
<!--          </template>-->
<!--        </v-expansion-panel-title>-->

      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script>
export default {
  name: "TopicHierarchy",
  data() {
    return {
      panel: [],
      topics: [
        {"uuid": "A", "topicName": "Topic A", "content": ["subA", "subB"]},
        {"uuid": "B", "topicName": "Topic B", "content": ["subC", "subD"]},
        {"uuid": "C", "topicName": "Topic C", "content": ["subE", "subF"]}
      ]
    }
  },
  methods: {
    all() {
      this.panel = ['A', 'B', 'C']
    },
    none() {
      this.panel = []
    },
  },
}
</script>

<style scoped>

</style>