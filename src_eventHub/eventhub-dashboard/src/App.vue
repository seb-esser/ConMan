<template>
  <v-app>
    <v-navigation-drawer
        expand-on-hover>
      <!-- Header -->
      <vlist>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title class="text-h6">
              BIM-Event-Hub
            </v-list-item-title>
            <v-list-item-subtitle>
              version control for BIM models
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </vlist>

      <!-- the actual menu -->
      <v-divider></v-divider>

      <v-list density="compact">
        <v-list-item
            v-for="item in items"
            :key="item.title"
            router :to="item.route"
        >
          <v-list-item-avatar start>
            <v-icon :icon="item.icon"></v-icon>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app>
      <!-- -->
    </v-app-bar>

    <!-- Sizes your content based upon application components -->
    <v-main>

      <!-- Provides the application the proper gutter -->
      <v-container fluid>

        <!-- If using vue-router -->
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      2022 - TUM CMS
      <!-- -->
    </v-footer>

  </v-app>
</template>

<script>

export default {
  name: 'App',

  data() {
    return {
      drawer: true,
      items: [
        //  This list controls the entries given in the left navigation bar.
        //  If adding a new item, remember to add a new route to the router as well.

        {title: 'Home', icon: 'mdi-home', route: "/"},
        {title: 'Dashboard', icon: 'mdi-view-dashboard', route: "/dashboard"},
        {title: 'Subscriptions', icon: 'mdi-set-center', route: "/subscriptions"},
        {title: 'Graph Visualization', icon: 'mdi-graphql', route: "/graph"},
        {title: 'About', icon: 'mdi-help-box', route: "/about"},
      ],
      right: null,
    }
  },
}
</script>
