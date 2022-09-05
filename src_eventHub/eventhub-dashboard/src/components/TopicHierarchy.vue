<template>
  <div>
    <h2>Subscriptions and Topic hierarchy</h2>
    <v-card variant="outlined">
      <div class="text-center d-flex pb-4">
        <v-btn class="ma-2" @click="all">
          Expand
        </v-btn>
        <v-btn class="ma-2" @click="none">
          Collapse
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
        >
          <v-expansion-panel-title>{{ topic.topicName }}</v-expansion-panel-title>
          <v-expansion-panel-text>
            <TopicView
                :content="topic.content"
            >
            </TopicView>

            <v-chip
                color="red"
                text-color="white"
                icon="mdi-blinds"
                outlined
            >Architecture
            </v-chip>
            <v-chip
                outlined
            >HVAC
            </v-chip>
            <v-spacer></v-spacer>
          </v-expansion-panel-text>

        </v-expansion-panel>
      </v-expansion-panels>


      <v-container class="py-0">
        <v-row
            align="center"
            justify="start"
        >
          <v-col
              v-for="(selection, i) in allSubscribers"
              :key="selection.text"
              class="shrink"
          >
            <v-chip
                :disabled="loading"
                closable
                @click:close="selected.splice(i, 1)"
            >
              <v-icon
                  left
                  :icon="selection.icon"
              ></v-icon>
              {{ selection.text }}
            </v-chip>
          </v-col>

          <v-col
              v-if="!allSelected"
              cols="12"
          >
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </div>
</template>

<script>
import TopicView from "@/components/TopicView";

export default {
  name: "TopicHierarchy",
  components: {TopicView},

  data() {
    return {
      panel: [],
      topics: [
        {
          "uuid": "A",
          "topicName": "Domain Model Architecture",
          "content": [
            {"id": 1, "name": "Walls"},
            {"id": 2, "name": "Windows"},
            {"id": 3, "name": "Doors"}
          ]
        },
        {
          "uuid": "B",
          "topicName": "Domain Model Structural Design",
          "content": [
            {"id": 1, "name": "Slabs"},
            {"id": 2, "name": "Columns"}
          ]
        },
      ],

      // to do: get this information from the database
      allSubscribers: [
        {
          text: 'Architecture',
          icon: 'mdi-nature',
        },
        {
          text: 'Structural Design',
          icon: 'mdi-glass-wine',
        }
      ],
      loading: false,
      selected: []
    }
  },
  computed: {
    allSelected() {
      return this.selected.length === this.allSubscribers.length
    },

  },

  watch: {
    selected() {
      this.search = ''
    },
  },

  methods: {
    all() {
      this.panel = ['A', 'B', 'C']
    },
    none() {
      this.panel = []
    },

    next() {
      this.loading = true

      setTimeout(() => {
        this.search = ''
        this.selected = []
        this.loading = false
      }, 2000)
    },
  },

}
</script>

<style scoped>

</style>